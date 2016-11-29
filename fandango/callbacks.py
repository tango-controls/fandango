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

from excepts import getLastException
from objects import *
from functional import *
from dicts import *
from tango import PyTango,EventType,fakeAttributeValue, CachedAttributeProxy, get_full_name
from threads import ThreadedObject,Queue,timed_range,wait
from log import Logger

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
    'API_EventPropertiesNotSet',
    'API_CommandNotFound')

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

class EventListener(Object): #Logger,
    """
    The EventListener class accepts 3 event hooks:
        self.set_event_hook()
        self.set_error_hook()
        self.set_value_hook()
        
    All of them need a callable accepting three arguments: src,type,value
    
    In the case of value_hook it will not pass the event object but event.value/rvalue
    """
    
    def __init__(self, name, parent=None,source=False,loglevel=2):
        """ 
        Pass name and parent object for logging.
        If source is True or an object, this listener will subscribe for source or parent events.
        If False, then subscription will have to be done using EventSource.addListener(EventListener)
        """
        self.name, self.parent,self.source = name,parent,source
        self.loglevel = loglevel
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
        now = time.time()
        inc = now - self.last_event_time
        delay = int(1e3*(now-(ctime2time(value.time) if hasattr(value,'time') else now)))
        
        if getattr(value,'error',False):
            if self.loglevel:
                print('%s: eventReceived(%s,ERROR,%s): +%s(+%s ms)'%(self.name,src,value,inc,delay))
            if self.error_hook is not None:
                try: self.error_hook(src,type_,value)
                except: traceback.print_exc()
        else:
            value = getattr(value,'value',getattr(value,'rvalue',type(value)))
            if self.loglevel>2:
                print('%s: eventReceived(%s,%s,%s): +%s(+%s ms)'%(self.name,src,type_,value,inc,delay))
            if value is not None and self.value_hook is not None:
              try:self.value_hook(src,type_,value)
              except: traceback.print_exc()
        if self.event_hook:
            try: self.event_hook(src,type_,value)
            except: traceback.print_exc()
        self.last_event_time = now
    
class EventThread(ThreadedObject):
    """
    This class processes both Events and Polling.
    All listeners should implement eventReceived method
    All sources must have a listeners list
    Filters are not implemented
    """
    MinWait = 1e-4 #Event processing limited to 10KHz maximum (rest are queued)
    EVENT_POLLING_RATIO = 100 #How many events to process before checking polled attributes
    
    def __init__(self):
        self.queue = Queue.Queue()
        #self.listeners = CaselessDefaultDict(lambda k:CaselessList())
        self.sources = CaselessDict()
        self.event = threading.Event()
        self.counters = CaselessDefaultDict(int)
        
        ThreadedObject.__init__(self,target=self.process,period=self.MinWait)
        
    def put(self,*args): 
        self.queue.put(*args)
    def get(self,*args,**kwargs):  
        return self.queue.get(*args,**kwargs)
    def wait(self,tout=None):
        self.event.wait(tout or self.MinWait)

    def register(self,source):
        print('EventThread.register(%s)'%source)
        if not self.get_started():
            self.start()
        if source.full_name not in self.sources:
            self.sources[source.full_name] = source
            source.last_read_hw = time.time()
            
    def get_source(self,source): 
        if isString(source):
            name = source
        else:
            name = getattr(source,'full_name',getattr(source,'model',''))
            self.sources[name] = source
        return name
    
    def get_object(self,source):
        return self.sources.get(source,None) if isString(source) else source

    def process(self):
        """ 
        Currently, this implementation will process 1 event and one polling
        each time as max.
        """
        #print('Processing Events')
        WAS_EMPTY = False
        for i in range(self.EVENT_POLLING_RATIO):
            try:
                #@TODO: Event Filters should be implemented here 
                #including removal of PERIODIC events if a change event is already in queue
                data = self.get(block=False)
                if isSequence(data):
                    source,args = data[0],data[1:]
                else: 
                    source,args = data,[]
                name = self.get_source(source)
                source = self.get_object(source)
                source.last_read_hw = time.time()
                self.fireEvent(source,*args)
                self.wait(0)
            except Queue.Empty,e:
                WAS_EMPTY = True
                break
            except Exception,e:
                #The queue is empty, long period attributes can be processed
                if 'empty' not in str(e).lower():
                    traceback.print_exc()
                #WAS_EMPTY = True
                break
       
        ## print('Executing pollings')
        now = time.time()
        pollings = []
        for s in self.sources.values():
            s.checkEvents(tdiff=2e-3*s.polling_period)
            if s.getEventsMode():
                    nxt = s.last_read_hw+(s.polling_period if s.isPollingEnabled() 
                               else s.KeepAlive)/1e3
                    pollings.append((nxt,s))
            
        for nxt,source in reversed(sorted(pollings)):
            if now > nxt and (s.isPollingEnabled() or WAS_EMPTY):
                try:
                  t0 = time.time()
                  source.poll()
                except:
                  traceback.print_exc()
                  if WAS_EMPTY: break
                source.last_read_hw = now
                
        ## print('Check pending HW asynch requests')
        asynch_hw = [s[1] for s in pollings if getattr(s,'pending_request',None) is not None]
        for source in randomize(asynch_hw):
            try: 
              source.asynch_hook() #<<<< THIS SHOULD BE ASYNCHRONOUS!
            except Exception,e:
              traceback.print_exc()
            source.last_read_hw = now #<<< DO NOT UPDATE THAT HERE; DO IT ON ASYNCH()
            break
          
        self.wait(0)
        return
                
    def fireEvent(self,source,*args):
        """ 
        It just retriggers every EventSource fireEvent method 
        If there's no method nor listeners, a callable is launched
        """
        try:
            if hasattr(source,'fireEvent'):
                source.fireEvent(*args)
            elif hasattr(source,'listeners'):
                for l in source.listeners:
                    try: getattr(l,'eventReceived',l)(*([source]+list(args))) 
                    except: traceback.print_exc()
                    finally: self.event.wait(self.MinWait/len(source.listeners))
            elif isCallable(source):
                source(*data[1:0])        
        except:
            print('fireEvent',source,args)
            traceback.print_exc()


class EventSource(Logger,Object):
    """ 
    Simplified implementation of Taurus Attribute/Model classes 
    
    Documentation at doc/recipes/EventsAndCallbacks.rst
    
    Slow Polling will be always enabled, as a KeepAlive is always kept reading
    the attribute values at an slow rate.
    
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
    - keepTime (1/50.) min. time between HW reads
    - tango_asynch = True/False ; to use asynchronous Tango reading
    - listeners = a list of listeners to be added at startup
    
    Keep in mind that if tango_asynch=True; you will not get the latest value 
    when doing  read(cache=False). You must use read(cache=False,asynch=False) instead.
    
    @TODO: Listeners should be assignable to only one type of eventl.
    @TODO: read(cache=False) should trigger fireEvent if not called from poll()
    """
    
    EVENT_TIMEOUT = 1800  # 10s
    QUEUE = None
    DefaultPolling = 3000.
    KeepAlive = 15000.
    INSTANCES = []
    
    #States
    UNSUBSCRIBED = 0 #Not using events at all
    PENDING = 1 #Polled, waiting for first event
    SUBSCRIBING = 2 #In the process of subscribing
    SUBSCRIBED = 3 #Using events only
    FORCED = 4 #Polling forced, interlaced with events
    FAILED = -1 #Not working at all
    
    #Modes
    SYNCHRONOUS = 0
    EVENTS = 1
    POLLED = 2
     
    def __init__(self, name, parent=None, **kwargs):
        """ Arguments: loglevel, tango_asynch, pollingPeriod, keepTime, enablePolling """

        self.simple_name = name.split('/')[-1]
        if not parent and '/' in name: 
            parent = name.rsplit('/',1)[0]
            
        if isString(parent):
            self.device = parent # just to keep it alive
            self.proxy = PyTango.DeviceProxy(parent)
        else:
            try:
                self.device = parent.name()
                self.proxy = parent
            except:
                raise Exception('A valid device name is needed')
              
        self.full_name = get_full_name('/'.join((self.device,self.simple_name)))
        self.normal_name = '/'.join(self.device.split('/')[-3:]+[self.simple_name])
        self.call__init__(Logger,self.full_name)
        self.setLogLevel(kwargs.get('loglevel','WARNING'))
        self.info('Init()')
        assert self.proxy,'A valid device name is needed'
        
        self.attr_value = None
        self.attr_time = 0
        self.listeners = []       
        self.event_ids = dict() # An {EventType:ID} dict      

        self.state = self.UNSUBSCRIBED
        self.tango_asynch = kwargs.get('tango_asynch',False)
        
        # Indicates if the attribute is being polled periodically
        # stores if polling has been forced by user API
        self.forced = kwargs.get('enablePolling', False)
        self.polled = self.forced #Forced is permanent, polled may change
        # current polling period
        self.polling_period = kwargs.get("pollingPeriod", self.DefaultPolling)
        self.keep_time = kwargs.get("keepTime", 1/50.)
        # force tango events usage
        self.use_events = kwargs.get("use_events",False)

        self.last_event = None
        self.last_event_time = 0
        self.last_error = None
        self.last_read_hw = 0
        self.pending_request = None
        self.counters = defaultdict(int)
        EventSource.INSTANCES.append(weakref.ref(self))
                          
        if self.forced:
            self.activatePolling()

        listeners = toList(kwargs.get('listeners',[]))
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
          self.removeListener(self.listeners.pop(0))
        if self.isPollingEnabled():
          self.deactivatePolling()
        if self.state in (self.SUBSCRIBED,self.PENDING):
          self.unsubscribeEvents()
        
    @staticmethod
    def thread():
        if EventSource.QUEUE is None:
            EventSource.QUEUE = EventThread()
        return EventSource.QUEUE         
    
    @staticmethod
    def start_thread():
        th = EventSource.thread()
        if not th.get_started(): 
            th.start()
            
    def getEventsMode(self):
        m = (self.use_events and 1) or (self.forced and 2) or (self.polled and 3)
        return int(m)

    def isUsingEvents(self):
        return self.state == self.SUBSCRIBED
    
    def enablePolling(self,forced=False):
        if forced: self.activatePolling(forced)
        
    def forcePolling(self, period = None):
        self.activatePolling(period,force=True)

    def disablePolling(self):
        self.deactivatePolling() # DON'T STOP THREADS HERE!

    def isPollingEnabled(self):
        return self.isPollingActive()

    def activatePolling(self,period = None, forced = False):
        #self.factory().addAttributeToPolling(self, self.getPollingPeriod())      
        self.polling_period = period or self.polling_period
        self.polled = True
        self.info('activatePolling(%s,%s)'%(self.full_name,self.polling_period))
        self.forced = forced
        self.start_thread()

    def deactivatePolling(self):
        #self.factory().removeAttributeFromPolling(self)
        self.info('deactivatePolling(%s,%s)'%(self.full_name,self.state))        
        self.polled = False
        self.forced = False

    def isPollingActive(self):
        return self.polled

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
            self.listeners.remove(weak_listener)
        except Exception, e:
            pass

    def addListener(self, listener,use_events=True,use_polling=False):
        self.debug('addListener(%s,use_events=%s,polled=%s)'%(listener,use_events,use_polling))
        self.use_events = self.use_events or use_events
        self.forced = self.forced or use_polling
        self.thread().register(self)
        if self.use_events and self.state == self.UNSUBSCRIBED:
            self.subscribeEvents()
        if self.forced and not self.polled:
            self.activatePolling()        
        weak = weakref.ref(listener,self._listenerDied)
        if weak not in self.listeners:
            self.listeners.append(weak)
            return True
        else:
            return False

    def removeListener(self, listener):
        weak = weakref.ref(listener,self._listenerDied)
        try:
            self.listeners.remove(weak)
        except Exception, e:
            return False
        if not self.listeners:
            self.unsubscribeEvents()
        return True

    def hasListeners(self):
        """ returns True if anybody is listening to events from this attribute """
        if self.listeners is None:
            return False
        return len(self.listeners) > 0
      
    def fireEvent(self, event_type, event_value, listeners=None):
        """sends an event to all listeners or a specific one"""
        self.debug('fireEvent(...)')
        listeners = listeners or self.listeners

        for l in listeners:
            try:
                if isinstance(l, weakref.ref):
                    l = l()
                if hasattr(l,'eventReceived'):
                    l.eventReceived(self, event_type, event_value)
                elif isCallable(l):
                    l(self, event_type, event_value)
            except:
                traceback.print_exc()
                
    # TANGO RELATED METHODS
    
    def subscribeEvents(self):
        self.debug('subscribeEvents(state=%s)'%(self.state))
        self.use_events = True
        if self.state == self.SUBSCRIBED:
            raise Exception('AlreadySubscribed!')
        
        self.state = self.SUBSCRIBING
        self.last_event_time = now()
        self.thread().stop()
        for type_ in EventType.names.values():
            try:
                if self.event_ids.get(type_) is not None:
                    self.debug('\tevent %s already subscribed'%type_)
                else:
                  self.event_ids[type_] = self.proxy.subscribe_event(
                      self.simple_name,type_,self,[],True)
                  self.debug('\tevent %s SUBSCRIBED'%type_)
                  #self.state = self.SUBSCRIBED
            except:
                self.debug('\tevent %s not subscribed'%type_)

        ## State will be kept in SUBSCRIBING until an event is received
        ## If nothing arrives after N seconds, polling will be activated
        self.start_thread()

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
            if tdiff and (self.state == self.SUBSCRIBING or (vdiff and self.state == self.SUBSCRIBED)):
                self.warning('Event subscribing failed (tdiff=%s,vdiff=%s) switching to polling'%(tdiff,vdiff))
                if self.state==self.SUBSCRIBING:
                    self.state = self.PENDING
                r = False

        if self.listeners:
            if not self.polled and (self.forced or self.use_events and self.state != self.SUBSCRIBED):
                self.activatePolling()    
            
        else:
            if self.polled:
                self.deactivatePolling()
            if self.state == self.SUBSCRIBED:
                self.unsubscribeEvents()

        return r
                
    def unsubscribeEvents(self):
        self.info('unsubscribeEvents(...)')
        for type_,ID in  self.event_ids.items():
            try:
                self.proxy.unsubscribe_event(ID)
                self.event_ids.pop(type_)
            except Exception,e:
                self.debug('Error unsubscribing %s events: %s'%(type_,e))
        if not self.hasListeners() and not self.isPollingForced():
            self.deactivatePolling()
        self.state = self.UNSUBSCRIBED    
    
    def decodeAttrInfoEx(self,attr_conf):
        pass
      
    def write(self, value, with_read=True):
        self.debug('write(...)')
        self.counters['write']+=1
        self.proxy.write_attribute(self.simple_name,value)
        if with_read:
            return self.read(cache=False)

    def read(self, cache=True,asynch=None):
        """ 
        Read last value acquired, 
        if cache = False or not polled it will trigger
        a proxy.read_attribute() call.
        
        If asynch=True/False, self.tango_asynch will be overriden for this call.
        """
        self.debug('read(cache=%s,asynch=%s)'%(cache,asynch))
        asynch = notNone(asynch,self.tango_asynch)
        now = time.time()
        
        # If not polled, force HW reading
        if not any((self.isPollingEnabled(),self.isUsingEvents())):
            cache = False
        # If it was just updated, return cache
        elif hasattr(self.attr_value,'time') and \
          self.keep_time>(time.time()-ctime2time(self.attr_value.time)):
            cache = True

        if cache:
            self.asynch_hook() # Check for pending asynchronous results
            if self.attr_value is not None:
                return self.attr_value
            elif self.state != self.UNSUBSCRIBED:
                self.info('Attribute first reading (no events received yet)')
        
        self.counters['read']+=1
        self.debug('%s.read_attribute(%s,%s,%s)'%(self.device,self.simple_name,self.tango_asynch,self.pending_request))

        try:
            ## Do not merge these IF's, order matters
            if asynch:
                if self.pending_request is not None:
                    self.attr_value = notNone(self.asynch_hook(),self.attr_value)
                else:
                    self.pending_request = self.proxy.read_attribute_asynch(self.simple_name),time.time()
                    self.attr_value = notNone(self.asynch_hook(),self.attr_value)
            else:
                self.attr_value = self.proxy.read_attribute(self.simple_name)
        except Exception,e:
            # fakeAttributeValue initialized with full_name
            traceback.print_exc()
            self.attr_value = fakeAttributeValue(self.full_name,value=e,error=e)
        self.last_read_hw = now
        self.fireEvent(EventType.PERIODIC_EVENT,self.attr_value)
            
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
        now = time.time()
        self.debug('poll(+%s): %s'%(now-self.last_read_hw,self.counters['poll']))
        self.counters['poll']+=1
        if self.state == self.SUBSCRIBING:
            self.thread().lasts[self.full_name] = self.last_read_hw = now
            return
        try:
            prev = self.attr_value and self.attr_value.value
            ## The read() call will trigger a fireEvent()
            self.attr_value = self.read(cache=False) #(self.attr_value is not None))
            av = getattr(self.attr_value,'value',self.attr_value)
            diff = prev != av
            self.checkEvents(vdiff=diff)
        except Exception,e:
            # fakeAttributeValue initialized with full_name
            traceback.print_exc()
            #self.attr_value = fakeAttributeValue(self.full_name,value=e,error=e)
        #self.last_read_hw = now
        #self.fireEvent(EventType.PERIODIC_EVENT,self.attr_value)
    
    def push_event(self,event):
        #source,type_,value):
        try:           
            self.counters['total_events']+=1
            now = time.time()
            type_ = event.event
            self.counters[type_]+=1
            self.last_event_time = ctime2time(event.reception_date)
            delay = now-self.last_event_time
            if delay > 1e3 : self.warning('push_event was %f seconds late'%delay)
            self.state = self.SUBSCRIBED

            if event.err:
                self.last_error = event
                value = event.errors[0]
                reason = event.errors[0].reason
                
                if reason in EVENT_TO_POLLING_EXCEPTIONS:
                    if not self.isPollingEnabled():
                      self.warning('EVENTS_FAILED! (%s): reactivating Polling'%(reason))
                      self.state = self.PENDING
                      self.activatePolling()
                    return
                else:
                    print('ERROR in %s(%s): %s(%s)'%(self.full_name,type_,type(value),reason))
                    
            elif isinstance(event,PyTango.AttrConfEventData):
                value = event.attr_conf
                self.decodeAttrInfoEx(value)
                #(Taurus sends here a read cache=False instead of AttrConf)
            else:
                try:
                    self.attr_value = value = event.attr_value
                except:
                    self.warning('push_event(%s): no value in %s'%(type_,dir(event)))
                    self.attr_value = value = None

            if self.isPollingActive() and not self.isPollingForced():
                self.deactivatePolling()
            self.last_event = event    
            #Instead of firingEvent, I return and pass the value to the queue
            self.thread().put((self,type_,value))
        except:
            print(type(event),dir(event))
            traceback.print_exc()

                
class TangoEventSource(EventSource):
        pass


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
    """ This is how attributes were registered in the old PyStateComposer """
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
    es = fb.EventSource('test/events/1/currenttime')
    es.setLogLevel('DEBUG')
    es.KeepAlive = 5000.
    el = fb.EventListener('tester')
    es.addListener(el)
    if 'ipython' not in str(sys.argv):
      while (1):
        try: threading.Event().wait(1.)
        except: break
    
if __name__ == '__main__':
    __test__(sys.argv[1:])
