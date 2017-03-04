#!/usr/bin/env python2.5
"""
#############################################################################
##
## file :       callbacks..py
##
## description : This class manages a list of attributes subscribed to events that could have multiple receivers each one.
##      It supplies the ATK AttributeList behaviour.
##      device.DevChild and those inherited classes depends on that.
##      Global objects are:
##      _EventsList, _EventReceivers, _StatesList, _AttributesList, GlobalCallback
##      ... _EventReceivers must be substituted by DevicesList
##
## project :     Tango Control System
##
## $Author: Sergi Rubio Manrique, srubio@cells.es $
##
## $Revision: 2008 $
##
## copyleft :    ALBA Synchrotron Controls Section, CELLS
##               Bellaterra
##               Spain
##
#############################################################################
##
## This file is part of Tango Control System
##
## Tango Control System is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as published
## by the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## Tango Control System is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
###########################################################################
"""
import sys,os,time,re
import threading,weakref
from copy import *

from excepts import getLastException,exc2str
from objects import *
from functional import *
from dicts import *
from tango import PyTango,EventType,fakeAttributeValue,ProxiesDict
from tango import get_full_name,get_attribute_events
from threads import ThreadedObject,Queue,timed_range,wait,threading
from log import Logger,printf

"""
@package callbacks

@par Internal Variables
@li _EventsList[attr_name]  the last event received for each attribute
@li _StatesList[dev_name] keeps the last State read for each device
@li _AttributesList[dev_name] keeps the last AttributeValue struct for each attribute. 

@remarks Mostly used by PyStateComposer device

It provides persistent storage.
lock.acquire and lock.release should be used to prevent threading problems!, 
Use of the lists inside push_event is safe
"""

###############################################################################

# Lightweight implementation of TaurusListener/TaurusAttribute

EVENT_TO_POLLING_EXCEPTIONS = (
    'API_AttributePollingNotStarted',
    'API_DSFailedRegisteringEvent',
    'API_NotificationServiceFailed',
    'API_EventChannelNotExported',
    'API_EventTimeout',
    'API_EventPropertiesNotSet', #Typical for archive and data ready event
    'API_CommandNotFound')

EVENT_CONF_EXCEPTIONS = (
    'API_AttributePollingNotStarted',
    'API_EventPropertiesNotSet', #Typical for archive and data ready event
    )

EVENT_TYPES = [ 'attr_conf', 'data_ready', 'user_event', 'periodic', 'change', 'archive','quality']

class AttrCallback(Logger,Object):
  
  #def __call__(self,*args,**kwargs):
      #self.attr_read(args,kwargs)
  
  def attr_read(self,*args,**kwargs):
    try:
      print('Callback at %s'%time2str())
      print('Received %d arguments'%len(args))
      for a in args:
          print('\t%s'%str(a)[:80])
          for k,v in a.__dict__.items():
            print('\t%s: %s'%(k,v))
          return
    except:
      traceback.print_exc()

class EventListener(Logger,Object): #Logger,
    """
    The EventListener class accepts 3 event hooks:
        self.set_event_hook()
        self.set_error_hook()
        self.set_value_hook()
        
    All of them need a callable accepting three arguments: src,type,value
    
    In the case of value_hook it will not pass the event object but event.value/rvalue
    """
    
    def __init__(self, name, parent=None,source=False):
        """ 
        Pass name and parent object for logging.
        If source is True or an object, this listener will subscribe for source or parent events.
        If False, then subscription will have to be done using EventSource.addListener(EventListener)
        """
        self.name,self.parent,self.source = name,parent,source
        Logger.__init__(self,type(self).__name__+'(%s)'%self.name)
        self.last_event_time = 0
        #self.call__init__(Logger,name=name, parent=parent)
        self.set_event_hook()
        self.set_error_hook()
        self.set_value_hook()
        hooks = [o for o in (parent,source) if source and hasattr(o,'addListener')]
        if hooks: hooks[0].addListener(self)

    def set_event_hook(self,callable=None): self.event_hook = callable
    def set_error_hook(self,callable=None): self.error_hook = callable      
    def set_value_hook(self,callable=None): self.value_hook = callable

    def eventReceived(self, src, type_, value):
        """ 
        Method to implement the event notification
        Source will be an object, type a PyTango EventType, evt_value an AttrValue
        """
        t0 = time.time()
        inc = t0 - self.last_event_time
        delay = int(1e3*(t0 - (ctime2time(value.time) if hasattr(value,'time') else t0)))
        
        if getattr(value,'error',False):
            self.warning('%s: eventReceived(%s,ERROR,%s): +%s(+%s ms)'%(self.name,src,value,inc,delay))
            if self.error_hook is not None:
                try: self.error_hook(src,type_,value)
                except: self.warning(traceback.format_exc())
        else:
            value = getattr(value,'value',getattr(value,'rvalue',type(value)))
            self.debug('%s: eventReceived(%s,%s,%s): +%s(+%s ms)'%(self.name,src,type_,value,inc,delay))
            if value is not None and self.value_hook is not None:
              try:self.value_hook(src,type_,value)
              except: self.error(traceback.format_exc())
        if self.event_hook:
            try: self.event_hook(src,type_,value)
            except: self.error(traceback.format_exc())
        self.last_event_time = t0
    
class EventThread(Logger,ThreadedObject):
    """
    This class processes both Events and Polling.
    All listeners should implement eventReceived method
    All sources must have a listeners list
    On Current EventSource implementation this is a SINGLETONE!!!, its configuration
    will apply for the whole running process!
    

    The filtered argument will just forward last event received 
    on each loop iteration for each source. It can be set to False, True or a factor
    of latency.
    
    The latency (ms) specifies a time condition to abort event checking
    and proceed to callback execution.
    
    The real latency of the system is provided by inherited get_delay 
    and get_avg_delay methods
    
    """
    MinWait = 0.0001 #Event processing limited to 10KHz maximum (rest are queued)
    EVENT_POLLING_RATIO = 1000 #How many events to process before checking polled attributes
    
    def __init__(self,period_ms=None,filtered=False,latency=10.,loglevel='WARNING'):
        self.queue = Queue.Queue()
        self.sources = CaselessDict()
        self.event = threading.Event()
        period = 1e-3*(period_ms or 0) or self.MinWait
        ThreadedObject.__init__(self,target=self.process,period=period)
        Logger.__init__(self,type(self).__name__)
        self.filtered,self.latency = filtered,latency
        self.setLogLevel(loglevel)
        
    def setup(self,period_ms=None,filtered=None,latency=None,loglevel=None):
        """ 
        This method allows to reconfigure an already running EventThread 
        """
        self.filtered = notNone(filtered,self.filtered)
        self.latency = notNone(latency,self.latency)
        if period_ms is not None:
          period = 1e-3*(period_ms or 0) or self.MinWait
          self.set_period(period)
        if loglevel is not None:
          self.setLogLevel(loglevel)
        
    def set_period_ms(self,period):
        self.set_period(period*1e-3)
        
    def put(self,*args): 
        self.queue.put(*args)
    def get(self,*args,**kwargs):  
        return self.queue.get(*args,**kwargs)
    def wait(self,tout=None):
        self.event.wait(tout or self.MinWait)

    def register(self,source):
        self.info('EventThread.register(%s)'%source)
        if not self.get_started():
            self.start()
        if source.full_name not in self.sources:
            self.sources[source.full_name] = source
            source.last_read_time = time.time()
            
    def get_source(self,source): 
        if isString(source):
            name = source
        else:
            name = getattr(source,'full_name',getattr(source,'model',''))
            self.sources[name] = source
        return name
    
    def get_object(self,source):
        return self.sources.get(source,None) if isString(source) else source
      
    def get_pending(self):
        return queue.qsize()

    def process(self):
        """ 
        Currently, this implementation will process 100 events for each polling
        each time as max.
        """
        #self.debug('Processing Events')
        WAS_EMPTY = False
        queue = CaselessSortedDict()
        t0,evs,polls = now(),0,0
        filtered = self.filtered >= True
        
        #First, extract events from the queue
        for i in range(self.EVENT_POLLING_RATIO):
            try:
                data = self.get(block=False)
                evs+=1
                if isSequence(data):
                    source,args = data[0],data[1:]
                else: 
                    source,args = data,[]
                name = self.get_source(source)
                source = self.get_object(source)
                if source not in queue: queue[source] = []
                queue[source].append((source,args))

            except Queue.Empty,e:
                WAS_EMPTY = True
                break

            except Exception,e:
                #The queue is empty, long period attributes can be processed
                if 'empty' not in str(e).lower():
                    self.error(traceback.format_exc())
                break
              
            # Enable filtering if the performance is compromisesd
            if (False < self.filtered < True) and (
                  (time.time()-t0)>(self.filtered * 1e-3*self.latency) or 
                  self.queue.qsize() < self.EVENT_TO_POLLING_RATIO):
                filtered = True

            if now()>(t0+1e-3*self.latency):
                break 
        
        #Execute the events for each source
        #Sequential execution of events received is relatively guaranteed
        for s,events in sorted(queue.items()):
            #@TODO: Event Filters should be implemented here 
            #including removal of PERIODIC events if a change event is already in queue
            if filtered:
                events = events[-1:]
            while events:
                try:
                    e = events.pop(0)
                    source,args = e
                    source.last_read_time = now()
                    self.fireEvent(source,*args)
                    self.wait(0)                
                except:
                    self.error('%s:%s\n%s'%(s,e,traceback.format_exc()))

        self.wait(0) #breathing
       
        ## print('Executing pollings')
        t0 = now()
        pollings = []
        for s in self.sources.values():
            s.checkEvents(tdiff=2e-3*s.polling_period)
            if s.getMode():
                    nxt = s.last_read_time+(s.polling_period if s.isPollingEnabled() 
                               else s.KeepAlive)/1e3
                    pollings.append((nxt,s))
            
        for nxt,source in reversed(sorted(pollings)):
            if t0 > nxt and (s.isPollingActive() or WAS_EMPTY):
                try:
                  source.poll()
                  polls+=1
                except:
                  traceback.print_exc()
                  if WAS_EMPTY: break
                source.last_read_time = now()
                
        ## print('Check pending HW asynch requests')
        asynch_hw = [s[1] for s in pollings if getattr(s,'pending_request',None) is not None]
        for source in randomize(asynch_hw):
            try: 
              source.asynch_hook() #<<<< THIS SHOULD BE ASYNCHRONOUS!
            except Exception,e:
              traceback.print_exc()
            source.last_read_time = now() #<<< DO NOT UPDATE THAT HERE; DO IT ON ASYNCH()
            break
          
        self.wait(0)
        if evs or polls: self.debug('Processed %d events, %d pollings'%(evs,polls))
        return
                
    def fireEvent(self,source,*args):
        """ 
        It just retriggers every EventSource fireEvent method 
        If there's no method nor listeners, a callable is launched
        """
        try:
            if hasattr(source,'fireEvent'):
                source.fireEvent(*args)  ## Event types are filtered at EventSource.fireEvent
            elif hasattr(source,'listeners'):
                for l in source.listeners:
                    try: getattr(l,'eventReceived',l)(*([source]+list(args))) 
                    except: traceback.print_exc()
                    finally: self.event.wait(self.MinWait/len(source.listeners))
            elif isCallable(source):
                source(*data[1:0])        
        except:
            self.warning('fireEvent',source,args)
            self.warning(traceback.format_exc())


class EventSource(SingletonMap,Logger):
    """ 
    Simplified implementation of Taurus Attribute/Model and fandango.CachedAttributeProxy classes 
    
    It implements CachedAttributeProxy methods but doesnt inherit from it; 
    this regression is due to the lack of reliability of AttributeProxy in PyTango 9.
    
    Documentation at doc/recipes/EventsAndCallbacks.rst
    
    Slow Polling will be always enabled, as a KeepAlive is always kept reading
    the attribute values at an slow rate.
    
    Well, will be always enabled as long there are Listeners or Forced is True. If not polling
    will not be activated and it will be simply a CachedAttributeProxy.
    
    In this implementation, just a faster polling will be enabled if the 
    attribute provides no events. But the slow polling will never be fully disabled.
    
    If no events are received after EVENT_TIMEOUT, polling wil be also enabled.
    
    It will also subscribe to all attribute events, not only CHANGE and CONFIG
    
    All types are: 'CHANGE_EVENT,PERIODIC_EVENT,QUALITY_EVENT,ARCHIVE_EVENT,ATTR_CONF_EVENT,DATA_READY_EVENT,USER_EVENT'
    
    Arguments to EventSource(...) are:
    
    - name : attribute name (simple or full)
    - parent : device name or proxy
    - enablePolling (force polling by default)
    - pollingPeriod (3000)
    - keeptime (500 ms) min. time (in ms!) between HW reads
    - tango_asynch = True/False ; to use asynchronous Tango reading
    - listeners = a list of listeners to be added at startup
    
    Keep in mind that if tango_asynch=True; you will not get the latest value 
    when doing  read(cache=False). You must use read(cache=False,asynch=False) instead.
    
    @TODO: Listeners should be assignable to only one type of eventl.
    @TODO: read(cache=False) should trigger fireEvent if not called from poll()
    """
    
    EVENT_TIMEOUT = 1800  # 10s
    DEFAULT_LOG = 'WARNING'
    DEFAULT_EVENTS = [ 'periodic', 'change', 'archive', 'quality' ] #'user_event',
    VALUE_EVENTS = ['periodic','change','archive','quality','user_event']
    TAURUS_EVENTS = ['change','attr_conf']
    QUEUE = None
    DefaultPolling = 3000.
    KeepAlive = 15000.
    INSTANCES = []
    PROXIES = ProxiesDict()
    
    #States
    STATES = Struct({
      'UNSUBSCRIBED': 0, #Not using events at all
      'PENDING': 1, #Polled, waiting for first event
      'SUBSCRIBING': 2, #In the process of subscribing
      'SUBSCRIBED': 3, #Using events only
      'FORCED': 4, #Polling forced, interlaced with events
      'FAILED': -1, #Not working at all
      })
    
    def __init__(self, name, keeptime=1000., fake=False, parent=None, **kw):
        """ Arguments: loglevel, tango_asynch, pollingPeriod, keeptime, enablePolling, use_events """
        if 0 < name.replace('//','/').count('/') < name.count(':')+3:
            name += '/state'
        self.simple_name = name.split('/')[-1]
        if not parent and '/' in name: 
            parent = name.rsplit('/',1)[0]
        
        self.fake = kw.get('fake',False)
        if isString(parent):
            self.device = parent # just to keep it alive
            try:
              self.proxy = not self.fake and self.PROXIES[parent]
            except:
              self.proxy = not self.fake and PyTango.DeviceProxy(parent)
        else:
            try:
                self.device = parent.name()
                self.proxy = parent
            except:
                raise Exception('A valid device name is needed: %s'%([name,self.simple_name,parent]))
              
        self.full_name = get_full_name('/'.join((self.device,self.simple_name)))
        self.normal_name = '/'.join(self.device.split('/')[-3:]+[self.simple_name])
        #self.call__init__(Logger,self.full_name)
        Logger.__init__(self,self.full_name)
        self.setLogLevel(kw.get('loglevel',kw.get('log_level',self.DEFAULT_LOG)))
        self.info('Init()')
        assert self.fake or self.proxy,'A valid device name is needed'
        
        self.listeners = defaultdict(set) #[]       
        self.event_ids = dict() # An {EventType:ID} dict      
        self.state = self.STATES.UNSUBSCRIBED
        self.tango_asynch = kw.get('tango_asynch',False)
        self.write_with_read = kw.get('write_with_read',False)        
        
        # Indicates if the attribute is being polled periodically
        # stores if polling has been forced by user API
        self.forced = kw.get('enablePolling',kw.get('enable_polling',False))
        self.polled = self.forced #Forced is permanent, polled may change
        # current polling period in milliseconds
        self.polling_period = kw.get("pollingPeriod",kw.get('polling_period',self.DefaultPolling))
        self.keep_time = kw.get('keep_time',keeptime)
        # force tango events usage
        self.use_events = kw.get("use_events",[]) or []
        if self.use_events is True: self.use_events = self.DEFAULT_EVENTS

        self.attr_value = None
        self.event_lock = threading.Lock()
        self.last_event = dict()
        self.last_event_time = 0
        self.last_error = None
        self.last_read_time = 0
        self.pending_request = None
        self.stats = defaultdict(int)
        self.stats['start'] = now()
        EventSource.INSTANCES.append(weakref.ref(self))
                          
        if self.forced:
            self.activatePolling()

        listeners = toList(kw.get('listeners',[]))
        map(self.addListener,listeners)
            
    def __del__(self): 
        self.cleanUp()
    def __str__(self): 
        return 'EventSource(%s)'%(self.full_name)
    def __repr__(self):  
        return str(self)
        
    def cleanUp(self):
        self.debug("cleanUp")
        while self.listeners:
          self.removeListener(self.listeners.popitem())
        if self.isPollingEnabled():
          self.deactivatePolling()
        if self.checkState('SUBSCRIBED','PENDING'):
          self.unsubscribeEvents()
          
    def resetStats(self):
        t0 = now()
        self.stats = defaultdict(int)
        self.stats['start'] = t0
        return t0
        
    @staticmethod
    def thread():
        """
        It returns the current EventThread INSTANCE
        Use EventSource.thread().setup(...) to configure it
        """
        if EventSource.QUEUE is None:
            EventSource.QUEUE = EventThread()
        return EventSource.QUEUE
    
    @staticmethod
    def start_thread():
        th = EventSource.thread()
        if not th.get_started():
            th.start()
            
    def setState(self,state):
        try:
          state = self.STATES.get(state,state)
          if self.state != state:
            for k,v in self.STATES.items():
              if v==self.state: o = k
              if v==state: n = k
            self.state = state
            self.info('setState(): %s => %s'%(o,n))
        except:
          self.error('UNKNOWN STATE: %s'%state)
          
    def checkState(self,*states):
        states = states or [self.state]
        states = [self.STATES.get(s,s) for s in states]
        if self.state in states:
          return self.STATES.get_key(self.state)
        else:
          return False
            
    def getMode(self):
        """
        SYNCHRONOUS = 0
        EVENTS = 1
        POLLED = 2
        """
        m = (self.use_events and 1) or (self.forced and 2) or (self.polled and 3)
        return int(m)

    def isUsingEvents(self):
        """ This method doesnt tell if it wants to use_events but if it is actually receiving them """
        return self.checkState('SUBSCRIBED')
         
    def enablePolling(self,force=False):
        if force: self.activatePolling(force = force)
        
    def forcePolling(self, period = None):
        self.activatePolling(period,force=True)

    def disablePolling(self):
        self.deactivatePolling() # DON'T STOP THREADS HERE!

    def isPollingEnabled(self):
        """ It should be called isPollingAllowed instead """
        return self.polled

    def activatePolling(self,period = None, force = None):
        #self.factory().addAttributeToPolling(self, self.getPollingPeriod())      
        self.polling_period = notNone(period,self.polling_period)
        self.polled = True
        self.info('activatePolling(%s,%s)'%(self.full_name,self.polling_period))
        self.resetStats()
        self.forced = notNone(force,self.forced)
        self.thread().register(self)

    def deactivatePolling(self):
        #self.factory().removeAttributeFromPolling(self)
        self.info('deactivatePolling(%s,%s)'%(self.full_name,self.state))        
        self.polled = False
        self.forced = False

    def isPollingActive(self):
        return self.polled or self.forced

    def isPollingForced(self):
        return self.forced

    def changePollingPeriod(self, period):
        """change polling period to period miliseconds """
        self.polling_period = period
        self.activatePolling()

    def getPollingPeriod(self):
        """returns the polling period """
        return self.polling_period
      
    # LISTENER METHOD

    def _listenerDied(self, weak_listener):
        try:
            self.listeners.pop(weak_listener)
        except Exception, e:
            pass

    def addListener(self, listener,use_events=True,use_polling=False):
        """
        Adds a Listener to this EventSource object.
        use_events can be a boolean or a list of event types (change,attr_conf,periodic,archive)
        """
        if not isCallable(listener) \
          and not hasattr(listener,'eventReceived') \
            and not hasattr(listener,'event_received'):
              raise Exception('NotAValidListener!: %s'%listener)
        
        if not use_events: use_events = []
        elif use_events is True: use_events = self.DEFAULT_EVENTS
        use_events = toList(use_events or self.use_events)
        self.debug('addListener(%s,use_events=%s,polled=%s)'%(listener,use_events,use_polling))
        self.forced = self.forced or use_polling
        self.thread().register(self)
        if use_events:
            self.subscribeEvents(types=use_events,asynchronous=self.checkState('UNSUBSCRIBED'))
        if self.forced and not self.polled:
            self.activatePolling()
        weak = weakref.ref(listener,self._listenerDied)
        if weak not in self.listeners:
          #This line is needed, as listeners may be polling only
          self.listeners[weak] = set()
        for e in use_events:
            self.listeners[weak].add(e)
        return True

    def removeListener(self, listener):
        """
        Remove a listener object or callback.
        :listener: can be object, weakref, sequence or '*'
        """
        if listener == '*':
            self.warning('Removing all listeners')
            listener = self.listeners.keys()

        if isSequence(listener):
            while listener:
              self.removeListener(listener.pop())
            return
        elif not isinstance(listener,weakref.ReferenceType):
            listener = weakref.ref(listener,self._listenerDied)
            
        try:
            self.listeners.pop(listener)
        except Exception, e:
            return False
        if not self.listeners:
            self.unsubscribeEvents()
        return True

    def hasListeners(self):
        """ returns True if anybody is listening to events from this attribute """
        if not self.listeners:
            return False
        return len(self.listeners) > 0
      
    def fireEvent(self, event_type, event_value, listeners=None):
        """
        sends an event to all listeners or a specific one
        event type filtering is done here
        poll() events will be allowed to pass through
        """
        self.debug('fireEvent(%s), %d events in queue'%(event_type,self.thread().queue.qsize()))
        self.stats['fired']+=1
        listeners = listeners or self.listeners

        for l in listeners:
            try:
                #event filter will allow poll() events to pass through
                if (event_type not in ('periodic',PyTango.EventType.PERIODIC_EVENT) 
                    and l in self.listeners and event_type not in self.listeners[l]):
                    self.debug('%s event discarded'%event_type)
                    continue
                if isinstance(l, weakref.ref):
                    l = l()
                if hasattr(l,'eventReceived'):
                    self.debug('fireEvent(%s) => %s?' % (event_type,l))
                    l.eventReceived(self, event_type, event_value)
                elif isCallable(l):
                    l(self, event_type, event_value)
            except:
                traceback.print_exc()
        try:
            vtime = ctime2time(getattr(event_value,'time',None))
            self.stats['acc_latency'] += now()-vtime
            self.stats['latency'] = self.stats['acc_latency']/self.stats['fired']
        except: pass
            
                
    # TANGO RELATED METHODS
    
    def checkEventsReceived(self,types=None):
        types = types or self.event_ids
        if not types:
            return False
        for t in types:
            if not any(clmatch(e,t) or clmatch(t,e) for e in self.last_event):
                return False
        return True                
    
    def subscribeEvents(self,types=None,asynchronous=True):
        try:
          self.event_lock.acquire()
          t0 = self.resetStats()
          
          types = toList(types) if types else []
          if not isIterable(self.use_events): self.use_events = []
          self.use_events = sorted(set((self.use_events+types) or self.DEFAULT_EVENTS))

          if self.isUsingEvents() and self.checkEventsReceived(self.use_events):
              self.warning('AlreadySubscribed!')
              return False
            
          self.info('subscribeEvents(%s,asynch=%s)'%(self.use_events,asynchronous))

          if asynchronous:
              # Subscription to be done by checkEvents()
              #if self.checkState('SUBSCRIBING','PENDING'):
              self.setState('UNSUBSCRIBED')

          else:
              self.last_event_time = now()
              ##self.thread().stop() #DONT DO THIS WITHIN THE LOOP HOOK!

              try:
                for k,type_ in EventType.names.items():
                  if any(clmatch(e,k) for e in self.use_events):
                    try:
                        if self.event_ids.get(type_) is not None:
                            self.debug('event %s already subscribed'%type_)
                        else:
                          self.info('SUBSCRIBING to %s events'%type_)                      
                          self.event_ids[type_] = self.proxy.subscribe_event(
                              self.simple_name,type_,self,[],True)
                          if not self.isUsingEvents():
                              self.setState('SUBSCRIBING')
                    except:
                        self.debug('event %s not subscribed'%type_)

                ## State will be kept in SUBSCRIBING until an event is received
                ## If nothing arrives after N seconds, polling will be activated
                self.info('subscribeEvents() took %.2f seconds'%(now()-t0))
              except:
                self.error('subscribeEvents(): \n'+traceback.format_exc())
              finally:
                pass 
          
          #self.start_thread() #DONT DO THIS WITHIN THE LOOP HOOK!
          self.thread().register(self)

        except:
          self.error('subscribeEvents(): \n'+traceback.format_exc())
        finally:
          self.event_lock.release()

        return True

    def checkEvents(self,tdiff=None,vdiff=None):
        """
        tdiff: max time difference allowed between last_event_time and current time
        vdiff: difference between last event value and current hw value
        """
        #self.debug('checkEvents(...)')
        delta = now()-self.last_event_time 
        if delta > (tdiff or self.EVENT_TIMEOUT): tdiff = delta
        ## @TODO: vdiff should be compared against event config
        vdiff = vdiff if not isSequence(vdiff) else any(vdiff)
        r  =  True
        if self.use_events:
            if self.checkState('UNSUBSCRIBED'):
                self.subscribeEvents(asynchronous=False)
          
            if tdiff and (self.checkState('SUBSCRIBING') or (vdiff and self.isUsingEvents())):
                if not self.isUsingEvents():
                    self.warning('Event subscribing failed (tdiff=%s,vdiff=%s) switching to polling'%(tdiff,vdiff))
                    self.setState('PENDING')
                else:
                    self.warning('Values differ and no event received! (tdiff=%s,vdiff=%s)'%(tdiff,vdiff))
                r = False

        if self.listeners:
            if not self.polled and (self.forced or self.use_events and not self.isUsingEvents()):
                self.info('checkEvents(): events not subscribed, enabling polling')
                self.activatePolling()    
            
        else:
            if self.polled and not self.forced:
                self.info('checkEvents(): no clients, stop polling')
                self.deactivatePolling()
            
            # Do not unsubscribe events if not called explicitly
            #if self.isUsingEvents():
                #self.info('checkEvents(): no clients, disabling events')
                #self.unsubscribeEvents()

        return r
                
    def unsubscribeEvents(self):
        self.info('unsubscribeEvents(...)')
        self.use_events = []
        for type_,ID in  self.event_ids.items():
            try:
                self.proxy.unsubscribe_event(ID)
                self.event_ids.pop(type_)
            except Exception,e:
                self.debug('Error unsubscribing %s events: %s'%(type_,e))
        if not self.hasListeners() and not self.isPollingForced():
            self.deactivatePolling()
        self.setState('UNSUBSCRIBED')
    
    def decodeAttrInfoEx(self,attr_conf):
        pass
      
    def set_cache(self,value,t=None):
        """
        set_cache and fake are used by PyAlarm.update_locals
        It's used to emulate alarm state reading from other devices
        """
        self.last_read_time = t or time.time()
        self.attr_value = hasattr(value,'value') and value or fakeAttributeValue(self.full_name,value,error=False)
        self.fireEvent(EventType.PERIODIC_EVENT,self.attr_value)
      
    def write(self, value, with_read=None):
        """
        The with_read argument will trigger a read() call and an update in all listeners
        """
        with_read = with_read if with_read is not None else self.write_with_read
        self.debug('write(...,with_read=%s)'%with_read)
        self.stats['write']+=1
        self.proxy.write_attribute(self.simple_name,value)
        if with_read:
            return self.read(cache=False)

    def read(self, cache=None,asynch=None,_raise=True):
        """ 
        Read last value acquired, 
        if cache = False or not polled it will trigger
        a proxy.read_attribute() call.
        
        If asynch=True/False, self.tango_asynch will be overriden for this call.
        """
        self.debug('read(cache=%s,asynch=%s)'%(cache,asynch))
        asynch = notNone(asynch,self.tango_asynch)
        t0 = now()
        
        # If it was just updated, return cache
        if cache is None:
          vtime = ctime2time(getattr(self.attr_value,'time',None))
          if self.fake or (t0 < (vtime + self.keep_time*1e-3)):
              cache = True
          # If not polled, force HW reading
          elif not self.getMode():
              cache = False
          else:
              cache = True
       
        self.asynch_hook() # Check for pending asynchronous results
        
        if not cache or self.attr_value is None:          
          if not self.checkState('UNSUBSCRIBED'):
                self.info('Attribute first reading (subscribed but no events received yet)')          
          self.stats['read']+=1
          self.debug('%s.read_attribute(%s,%s,%s)'%(self.device,self.simple_name,self.tango_asynch,self.pending_request))

          try:
              ## Do not merge these IF's, order matters
              if asynch:
                  if self.pending_request is not None:
                      self.attr_value = notNone(self.asynch_hook(),self.attr_value)
                  else:
                      self.pending_request = self.proxy.read_attribute_asynch(self.simple_name),now()
                      self.attr_value = notNone(self.asynch_hook(),self.attr_value)
              else:
                  self.attr_value = self.proxy.read_attribute(self.simple_name)
          except Exception,e:
              # fakeAttributeValue initialized with full_name
              print('EventSource.read(%s) failed!:\n%s'%(self.full_name,exc2str(e)))#traceback.format_exc().split('desc')[-1][:80]))
              self.attr_value = fakeAttributeValue(self.full_name,value=e,error=e)
              
          self.last_read_time = t0
          self.fireEvent(EventType.PERIODIC_EVENT,self.attr_value)
            
        if _raise and getattr(self.attr_value,'error',False):
          raise self.attr_value.value
        else:
          return self.attr_value
        
    
    def asynch_hook(self):
        self.debug('asynch_hook()')
        if self.pending_request is None:
            return None
        try:
            self.attr_value = self.proxy.read_attribute_reply(self.pending_request[0])
            self.pending_request = None
            return self.attr_value
        except PyTango.AsynReplyNotArrived,e:
            return None
        #except PyTango.CommunicationFailed,e:
            ##Device killed or restarted
            #self.pending_request = None
            #return None
        #except PyTango.AsynCall
            ##raise Exception,'CHECK HERE FOR EXPIRED REQUEST OR REQUEST NO VALID ANYMORE (e.g. DEVICE RESTARTED)'
            #self.pending_request = None
            #return None
        except Exception, e:
            self.pending_request = None
            self.attr_value = e
        return None
    
    def getValueObj(self):
        v = self.read(cache=True)
        try: return v.value
        except: return v

    def poll(self):
        t0 = now()
        self.debug('poll(+%s): %s'%(t0-self.last_read_time,self.stats['poll']))
        self.stats['poll']+=1
        if self.checkState('SUBSCRIBING'):
            ## While subscribing, polling is ignored and resumed on SUBSCRIBED/PENDING state
            self.thread().lasts[self.full_name] = self.last_read_time = t0
            return
        try:
            prev = self.attr_value and self.attr_value.value
            ## The read() call will trigger a fireEvent()
            self.attr_value = self.read(cache=False) #(self.attr_value is not None))
            av = getattr(self.attr_value,'value',self.attr_value)
            diff = prev != av
            self.checkEvents(vdiff=diff)
        except Exception,e:
            self.debug('poll(%s): %s'%(self.full_name,exc2str(e)))            
        ##FIRE EVENT IS ALREADY DONE IN read() METHOD!
    
    def push_event(self,event):
        try:           
            REG_FAILED = 'API_DSFailedRegisteringEvent'
            NOT_READY = 'API_AttributeNotDataReadyEnabled'
            NOT_PROPS = 'API_EventPropertiesNotSet'
            self.stats['total_events']+=1
            t0 = now()
            type_ = event.event
            self.stats[type_]+=1
            
            et = ctime2time(event.reception_date)
            if et<1e9: 
              if not event.err: 
                self.warning('%s event time is 0!'%type_)
              et = t0
            self.debug('push_event(%s,err=%s,has_events=%s)'%(type_,event.err,self.isUsingEvents()))
            if event.err:
                self.last_error = event
                has_evs,is_polled = self.isUsingEvents(),self.isPollingActive()
                value = event.errors[0]
                reason = event.errors[0].reason
                self.info('push_event(%s,err=%s,has_events=%s,polled=%s)'%(type_,reason,has_evs,is_polled))
                
                if reason == 'API_EventPropertiesNotSet' and self.isUsingEvents():
                  #Nothing to do, other event types are already subscribed
                  return
                
                elif reason in EVENT_TO_POLLING_EXCEPTIONS:
                  if reason in EVENT_CONF_EXCEPTIONS and any(self.last_event.values()):
                    #Discard config exceptions if some other event is already working well
                    return
                  elif self.use_events and not is_polled:
                    self.warning('EVENTS_FAILED! (%s,%s,%s,%s): reactivating Polling'%(type_,reason,has_evs,is_polled))
                    self.setState('PENDING')
                    self.activatePolling()
                  return
                
                else:
                  if reason not in (NOT_PROPS,NOT_READY,REG_FAILED):
                    # If push_event is executed, attributes are being received
                    self.warning('ERROR in %s(%s): %s(%s)'%(self.full_name,type_,type(value),reason))
                    self.last_event_time = et or time.time() #A valid error is a valid event
                    self.setState('SUBSCRIBED')
                  else: 
                    #Ignore the event
                    return
                    
            elif isinstance(event,PyTango.AttrConfEventData):
                value = event.attr_conf
                self.decodeAttrInfoEx(value)
                #(Taurus sends here a read cache=False instead of AttrConf)
            else:
                self.last_event_time = et or time.time()
                self.setState('SUBSCRIBED')
                try:
                    self.attr_value = value = event.attr_value
                except:
                    self.warning('push_event(%s): no value in %s'%(type_,dir(event)))
                    self.attr_value = value = None

            if self.isPollingActive() and not self.isPollingForced():
                self.info('push_event(): Event received, deactivating polling')
                self.deactivatePolling()

            delay = t0-self.last_event_time
            if delay > 1e3 : self.warning('push_event was %f seconds late'%delay)
            self.last_event[type_] = event
            #Instead of firingEvent, I return and pass the value to the queue
            self.thread().put((self,type_,value))
        except:
            self.error(type(event),dir(event))
            traceback.print_exc()
            
###############################################################################

class TangoListener(EventListener):
    pass

class TangoAttribute(EventSource):
    pass
  
#For backwards compatibility
import fandango.tango
class CachedAttributeProxy(EventSource):
    pass
setattr(fandango.tango,'CachedAttributeProxy',CachedAttributeProxy)
  
def get_test_objects(model='controls02:10000/test/sim/tonto/Pressure',period=1.):
    """
    v,tl = fandango.callbacks.get_test_objects()
    """
    tv = TangoAttribute(model)
    tl = TangoListener('test')
    tv.setLogLevel('DEBUG')
    tl.setLogLevel('DEBUG')
    tv.thread().set_period(period)
    tv.thread().setLogLevel('DEBUG')
    #tv.addListener(tl,use_events=False)
    return tv,tl
    


###############################################################################
# OLD API, DEPRECATED

_EventsList = {}
_EventReceivers = {}
_StatesList = {}
_AttributesList = {}

class EventStruct():
    name = ''
    event = None
    receivers = []

class TAttr(EventStruct):
    """ 
    This class is used to keep information about events received, 
    example of usage inside device.DevChild 
    """
    def __init__(self,name,dev_name='',proxy=None,event_id=None):
        self.name=name
        self.event=None #This is the last event received
        self.event_id=event_id #This is the ID received when subscribing
        self.dp=proxy #This is the device proxy
        self.dev_name=dev_name
        self.receivers=[] #This is the list of composers that must receive this event
        self.attr_value=None
        self.State=PyTango.DevState.UNKNOWN
    def __str__(self):
        return str(name)+","+str(self.event)+","+TangoStates[self.State]+";"
    def set(self, event):
        self.event=event#copy(event)
        self.attr_value=self.event.attr_value

#def command_queue(cmd_list,args_list=[],timeout=5000,threads=10):
    #''' executes a set of commands asynchronously with the specified timeout
    #'''
    #from threading import Thread
    #from Queue import Queue
    #if args_list and len(cmd_list)!=len(args_list):
        #raise Exception,'cmd_list and args_list lengths differ!'
    #num_threads = max(len(cmd_list),max_threads)
    #queue = Queue()
    #results = {}
    ##wraps system ping command
    #def pinger(i, q, r):
        #"""Pings subnet"""
        #wait = threading.Event().wait
        #while True:
            #wait(.3)
            #ip = q.get()
            
            #r[ip] = (not ret)
            #q.task_done()
    ##Spawn thread pool
    #for i in range(num_threads):
        #worker = Thread(target=pinger, args=(i, queue,results))
        #worker.setDaemon(True)
        #worker.start()
    ##Place work in queue
    #for ip in ips:
        #queue.put(ip)
    ##Wait until worker threads are done to exit    
    #queue.join()
    #return results

###############################################################################
# OLD API, DEPRECATED

class EventCallback():
    """ 
    It provides persistent storage.
    lock.acquire and lock.release should be used to prevent threading problems!, 
    Use of the lists inside push_event is safe
    """  
    def __init__(self):
        self.lock=threading.RLock()
        self.TimeOutErrors=0
        self.NotifdExceptions=['OutOfSync','EventTimeout','NotificationServiceFailed']
    
    def push_event(self,event):
        self.lock.acquire()
        try:
            #Pruning tango:$TANGO_HOST and other tags
            attr_name = '/'.join(event.attr_name.split('/')[-4:])
            dev_name = hasattr(event.device,'name') and event.device.name() or event.device
            print "in EventCallback.push_event(",dev_name,": ",attr_name,")"
            if not event.err and event.attr_value is not None:
                print "in EventCallback.push_event(...): ",attr_name,"=", event.attr_value.value
                self.TimeOutErrors=0
                _EventsList[attr_name.lower()].set(event)
                if attr_name.lower().endswith('/state'):
                    _StatesList[dev_name.lower()]=event.attr_value.value
                _AttributesList[event.attr_name.lower()]=event.attr_value
            else:
                print 'in EventCallback.push_event(...): Received an Error Event!: ',event.errors
                _EventsList[attr_name.lower()].set(event)
                #if 'OutOfSync' in event.errors[0]['reason']: or 'API_EventTimeout' in event.errors[0]['reason']:
                #if [e for e in event.errors if hasattr(e,'keys') and 'reason' in e.keys() and any(re.search(exp,e['reason']) for exp in self.NotifdExceptions)]:
                reasons = [getattr(e,'reason',e.get('reason',str(e)) if hasattr(e,'get') else str(e)) for e in event.errors] #Needed to catch both PyTango3 and PyTango7 exceptions
                if any(n in r for n in self.NotifdExceptions for r in reasons):
                    print 'callbacks=> DISCARDED EVENT FOR NOTIFD REASONS!!! %s(%s)' \
                        %(dev_name,reasons)
                    self.TimeOutErrors+=1
                    self.lock.release()
                    return
                else: 
                    self.TimeOutErrors=0                
                    if attr_name.lower().endswith('/state'):
                        _StatesList[dev_name.lower()]=None #An unreaded State cannot be UNKNOWN, it must be None to notify that an exception occurred!
                    _AttributesList[attr_name.lower()]=None
            #Launching Device.push_event()                
            for rec in _EventsList[attr_name].receivers:
                if rec in _EventReceivers.keys(): _EventReceivers[rec].push_event(event)
                elif hasattr(rec,'push_event'): rec.push_event(_event)
                elif isinstance(rec,threading.Event): rec.set()
                elif callable(rec): rec()
                else: raise 'UnknownEventReceiverType'
        except Exception,e:
            print 'exception in EventCallback.push_event(): ',e, ";", getLastException()
        self.lock.release()

###############################################################################
# OLD API, DEPRECATED

#THIS IS THE EVENTS CALLBACK SINGLETONE:
GlobalCallback = EventCallback()

## @TODO ... implemented in addTAttr and addReceiver ... missing a dp attribute to finish the work
#def subscribeToAttribute(subscriber,att_name):
    #"""
    #subscriber: a DeviceImpl object or the name of an already subscribed object
    #attribute: the FULL_NAME of the attribute to subscribe
    #"""
    #if att_name.count('/')<3: raise 'subscribeToAttribute_IncompleteAttributeName'
    #if isinstance(subscriber,PyTango.DeviceImpl):
        #EventReceivers[subscriber.get_name()]=subscriber
    #elif isinstance(subscriber,str):
        #subscriber=_EventReceivers[subscriber]
    #else: raise 'subscribeToAttribute_UnknownSubscriberException'
    
    #if not att_name in _EventsList.keys():
        #print 'subscribeToAttribute(%s,%s)'%(subscriber.get_name(),att_name)
        #EventsList[att_name] = TAttr(att_name)
        #EventsList[att_name].receivers.append(subscriber)
        #EventsList[att_name].event_id = self.dp.subscribe_event(att,PyTango.EventType.CHANGE_EVENT,GlobalCallback,[],True)
        #EventsList[att_name].dev_name = att_name.rsplit('/',0)
        #AttributesList[att_name]=None #it could be done inside _EventsList?!?!? ... or could AttributeList substitute _EventsList?
        
        ##It will not be initialized here ... as it differs in DevChild an DevsList
        ##EventsList[att_name].dp = self.dp
        #if att=='State': #DevsList should substitute that
            #StatesList[_EventsList[att_name].dev_name]=PyTango.DevState.UNKNOWN
            
        #print "In ", self.get_name(), "::check_dp_attributes()", ": Listing Device/Attributes in _EventsList:"
        #for a,t in _EventsList.items(): print "\tAttribute: ",a,"\tDevice: ",t.dev_name,"\n"
    #else:
        #print "In ", self.get_name(), "::check_dp_attributes(",att_name,")", ": This attribute is already in the list, adding composer to receivers list."
        #if not subscriber.get_name() in _EventsList[att_name].receivers and not subscriber in _EventsList[att_name].receivers:
            #EventsList[att_name].receivers.append(subscriber)
    #pass5

###############################################################################
# OLD API, DEPRECATED

def inStatesList(devname):
    print 'In callbacks.inStatesList ...'
    GlobalCallback.lock.acquire()
    print 'Checking if %s in %s.'%(devname,str(_StatesList.keys()))
    value=bool(devname.lower() in _StatesList.keys())
    GlobalCallback.lock.release()
    return bool
        
def getStateFor(devname):
    print 'In callbacks.getStateFor     ...'
    GlobalCallback.lock.acquire()
    state = _StatesList[devname.lower()] if devname.lower() in _StatesList.keys() else None
    GlobalCallback.lock.release()
    return state

def setStateFor(devname,state):
    print 'In callbacks.setStateFor     ...'
    GlobalCallback.lock.acquire()
    _StatesList[devname.lower()]=state
    GlobalCallback.lock.release()
    return state

def setAttributeValue(attr_name,attr_value):
    print 'In callbacks.setAttributeValue(%s)'%attr_name
    GlobalCallback.lock.acquire()
    _AttributesList[attr_name.lower()]=attr_value
    GlobalCallback.lock.release()
    return attr_value    

def inAttributesList(attname):
    GlobalCallback.lock.acquire()
    value=bool(attname.lower() in _AttributesList.keys())
    GlobalCallback.lock.release()
    return bool

def getAttrValueFor(attname):
    GlobalCallback.lock.acquire()
    value=_AttributesList[attname.lower()]
    GlobalCallback.lock.release()
    return value

def inEventsList(attname):
    GlobalCallback.lock.acquire()
    value=bool(attname.lower() in _EventsList.keys())
    GlobalCallback.lock.release()
    return value

def getEventFor(attname):
    GlobalCallback.lock.acquire()
    event=_EventsList[attname.lower()]
    GlobalCallback.lock.release()
    return event

def getEventItems():
    GlobalCallback.lock.acquire()
    result = _EventsList.items()
    GlobalCallback.lock.release()
    return result

def getSubscribedItems(receiver):
    '''It returns a list with all devices managed by callbacks to which this receiver is effectively subscribed'''
    GlobalCallback.lock.acquire()
    result = []
    for ev in _EventsList.values():
        if receiver in ev.receivers:
            result.append (ev.dev_name)
    GlobalCallback.lock.release()
    return result

###############################################################################
# OLD API, DEPRECATED


def addTAttr(tattr):
    try:
        GlobalCallback.lock.acquire()        
        att_name = tattr.name.lower()
        _EventsList[att_name] = tattr
        _AttributesList[att_name]=None
        if att_name.endswith=='/state':
            _StatesList[tattr.dev_name.lower()]=None
    except: print traceback.format_exc()    
    finally: GlobalCallback.lock.release()
    return
    
def addReceiver(attribute,receiver):
    try:
        GlobalCallback.lock.acquire()        
        if not receiver.lower() in _EventsList[attribute.lower()].receivers:
            _EventsList[attribute.lower()].receivers.append(receiver.lower())
    except: print traceback.format_exc()
    finally: GlobalCallback.lock.release()
    return

def subscribeDeviceAttributes(self,dev_name,attrs):
    """ 
    This is how attributes were registered in the old PyStateComposer 
    """
    dev = PyTango.DeviceProxy(dev_name)
    dev.ping()                                
    # Initializing lists
    if dev_name not in callbacks._StatesList: callbacks._StatesList[dev_name] = PyTango.DevState.UNKNOWN
    if dev_name not in callbacks._AttributesList: callbacks._AttributesList[dev_name] = None
    
    for att in attrs:
        att_name = (dev_name+'/'+att).lower()
        if att not in dev.get_attribute_list():
            continue
        if not dev.is_attribute_polled(att) and self.ForcePolling:
            self.info('::AddDevice(): forcing %s polling to %s' % (att,argin))
            period = dev.get_attribute_poll_period(att) or 3000
            dev.poll_attribute(att,period)
            self.debug("%s.poll_attribute(%s,%s)" % (argin,att,period))
        #cb = self 
        cb = GlobalCallback
        
        if not att_name in callbacks._EventsList.keys():
            callbacks._EventsList[att_name] = self.TAttr(att_name)
            callbacks._EventsList[att_name].receivers.append(self.get_name())
            self.info('AddDevice: subscribing event for %s'  % att_name)
            event_id = dev.subscribe_event(att,PyTango.EventType.CHANGE,cb,[],True)
            # Global List
            callbacks._EventsList[att_name].dp = dev
            callbacks._EventsList[att_name].event_id = event_id
            callbacks._EventsList[att_name].dev_name = dev_name
            print "In ", self.get_name(), "::AddDevice()", ": Listing Device/Attributes in _EventsList:"
            for a,t in callbacks._EventsList.items(): print "\tAttribute: ",a,"\tDevice: ",t.dev_name,"\n"
        else:
            self.warning("::AddDevice(%s): This attribute is already in the list, adding composer to receivers list." % att_name)
            if not dev_name in callbacks._EventsList[att_name].receivers:
                callbacks._EventsList[att_name].receivers.append(self.get_name())
            if callbacks._EventsList[att_name].attr_value is not None:
                if att is 'State':
                    callbacks._StatesList[dev_name]=_EventsList[att_name].attr_value.value
                else: 
                    callbacks._AttributesList[dev_name]=_EventsList[att_name].attr_value.value    
    return

###############################################################################
# TESTING


def __test__(args):
    import fandango.callbacks as fb
    a = args and args[0] or 'test/events/1/currentime'
    es = fb.EventSource(a)
    es.thread().set_period_ms(1000.)
    es.thread().setLogLevel('DEBUG')
    es.thread().filtered = True
    #es.setLogLevel('DEBUG')
    es.KeepAlive = 10000.
    el = fb.EventListener('listener')
    el.setLogLevel('DEBUG')
    es.addListener(el)
    el.set_value_hook(
        lambda s,t,v:
            printf('Current: %s'%s.read().value)
        )
    if 'ipython' not in str(sys.argv):
      while (1):
        try: threading.Event().wait(1.)
        except: break
    
if __name__ == '__main__':
    #__test__(sys.argv[1:])
    pass
