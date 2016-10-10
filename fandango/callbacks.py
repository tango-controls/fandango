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
from tango import PyTango,EventType,fakeAttributeValue, CachedAttributeProxy
from threads import ThreadedObject,Queue
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

class EventListener(Logger,Object):
    
    def __init__(self, name, parent=None):
        self.name, self.parent = name,parent
        #self.call__init__(Logger,name=name, parent=parent)

    def eventReceived(self, src, type_, value):
        """ 
        Method to implement the event notification
        Source will be an object, type a PyTango EventType, evt_value an AttrValue
        """
        if getattr(value,'error',False):
            print('%s: eventReceived(%s,ERROR,%s)'%(self.name,src,value))
        else:
            print('%s: eventReceived(%s,%s,%s)'%(self.name,src,type_,type(value)))
    
class EventManager(ThreadedObject):
    """
    All listeners should implement eventReceived method
    All sources must have a listeners list
    Filters are not implemented
    """
    DefaultPolling = 3000.
    KeepAlive = 15000.
    MinWait = 5e-4
    EVENT_POLLING_RATIO = 100 #How many events to process before checking polled attributes
    
    def __init__(self):
        self.queue = Queue.Queue()
        #self.listeners = CaselessDefaultDict(lambda k:CaselessList())
        self.sources = CaselessDict()
        self.event = threading.Event()
        self.counters = CaselessDefaultDict(int)
        
        ThreadedObject.__init__(self,target=self.process,period=self.MinWait)
        
    def put(self,*args): self.queue.put(*args)
    def get(self,*args,**kwargs):  return self.queue.get(*args,**kwargs)

    def get_source(self,source): 
        if isString(source):
            name = source
        else:
            name = getattr(source,'name',getattr(source,'model',''))
            self.sources[name] = source
        return name
    
    def get_object(self,source):
        return self.sources.get(source,None) if isString(source) else source

    def process(self):
        """ 
        Currently, this implementation will process 1 event and one polling
        each time as max.
        """
        #print('ProcessingEvent').
        WAS_EMPTY = False
        for i in range(self.EVENT_POLLING_RATIO):
            try:
                data = self.queue.get(block=False)
                if isSequence(data):
                    source,args = data[0],data[1:]
                else: 
                    source,args = data,[]
                name = self.get_source(source)
                source = self.get_object(source)
                source.last_poll = time.time()
                self.fireEvent(source,*args)
            except Queue.Empty,e:
                WAS_EMPTY = True
                break
            except Exception,e:
                #The queue is empty, long period attributes can be processed
                if 'empty' not in str(e).lower():
                    traceback.print_exc()
                #WAS_EMPTY = True
                break
       
        #print('Executing polling')
        now = time.time()
        pollings = []
        for s in self.sources.values():
            nxt = s.last_poll+(s.polling_period if s.isPollingEnabled() else self.KeepAlive)/1e3
            pollings.append((nxt,s))
            
        for nxt,source in reversed(sorted(pollings)):
            if now > nxt and (s.isPollingEnabled() or WAS_EMPTY):
                try: 
                    source.poll()
                except Exception,e:
                    traceback.print_exc()
                    if WAS_EMPTY: break
                source.last_poll = now
                break
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
        
    def addListener(self,source,listener):
        source,name = self.get_object(source),self.get_name(source)
        if name not in self.sources:
            self.sources[name] = source
        source.addListener(listener)
            
    def removeListener(self,source,listener=None):
        source,name = self.get_object(source),self.get_name(source)
        source.removeListener(listener)
        if not source.hasListeners(): self.sources.pop(name)
        
    #def addAttributeToPolling(...)
    
    #def removeAttributeFromPolling(...)

class EventSource(Logger,Object):
    """ 
    Simplified implementation of Taurus Attribute/Model classes 
    
    Polling will be always enabled, as a KeepAlive is always kept reading
    the attribute values at an slow rate.
    
    In this implementation, just a faster polling will be enabled if the 
    attribute provides no events. But the slow polling will never be fully disabled.
    
    It will also subscribe to all attribute events, not only CHANGE and CONFIG
    
    All types are: 'CHANGE_EVENT,PERIODIC_EVENT,QUALITY_EVENT,ARCHIVE_EVENT,ATTR_CONF_EVENT,DATA_READY_EVENT,USER_EVENT'
    
    @TODO: Listeners should be assignable to only one type of eventl.
    @TODO: read(cache=False) should trigger fireEvent if not called from poll()
    """
    
    DftTimeToLive = 10000  # 10s
    QUEUE = None
    
    #States
    UNSUBSCRIBED = 0
    PENDING = 1
    SUBSCRIBING = 2
    SUBSCRIBED = 3
    FAILED = -1
     
    def __init__(self, name, parent=None, **kwargs):
        self.call__init__(Object)        
        self.simple_name = name.split('/')[-1]
        # just to keep it alive
        if not parent and '/' in name:
            parent = name.rsplit('/',1)[0]
        if isString(parent):
            self.device = parent
            self.proxy = PyTango.DeviceProxy(parent)
        else:
            try:
                self.device = parent.name()
                self.proxy = parent
            except:
                raise Exception('A valid device name is needed')
        self.full_name = self.device + '/' + self.simple_name
        self.call__init__(Logger,self.full_name)
        self.setLogLevel('DEBUG')
        
        assert self.proxy,'A valid device name is needed'
        
        self.attr_value = None
        self.attr_time = 0
        self.listeners = []       
        self.event_ids = dict() # An {EventType:ID} dict      

        self.state = self.UNSUBSCRIBED
        # Indicates if the attribute is being polled periodically
        self.forced = kwargs.get('enablePolling', False)
        self.polled = self.forced
        # current polling period
        self.polling_period = kwargs.get("pollingPeriod", EventManager.DefaultPolling)
        # stores if polling has been forced by user API
        self.last_event = None
        self.last_error = None
        self.err_count = 0
        self.last_poll = 0
        self.counters = defaultdict(int)
                          
        if kwargs.get('enablePolling', False):
            self.activatePolling()
            
    def __del__(self):
        self.cleanUp()
        
    def cleanUp(self):
        self.info("cleanUp")
        self.deactivatePolling()
        self.unsubscribeEvents()
        
    @staticmethod
    def manager():
        if EventSource.QUEUE is None:
            EventSource.QUEUE = EventManager()
        return EventSource.QUEUE            

    def write(self, value, with_read=True):
        self.counters['write']+=1
        self.proxy.write_attribute(self.simple_name,value)
        if with_read:
            return self.read(cache=False)

    def read(self, cache=True):
        
        if cache:
            if self.attr_value is not None:
                return self.attr_value
            else:
                self.info('Attribute first reading (no events received yet)')
        
        self.counters['read']+=1
        self.attr_value = self.proxy.read_attribute(self.simple_name)
        return self.attr_value
    
    def getValueObj(self):
        return self.attr_value

    def poll(self):
        self.counters['poll']+=1
        now = time.time()
        self.debug('poll(+%s): %s'%(now-self.last_poll,self.counters['poll']))
        if self.state == self.SUBSCRIBING:
            self.manager().lasts[self.full_name] = self.last_poll = now
            return
        try:
            prev = self.attr_value and self.attr_value.value
            self.attr_value = self.read(cache=False) #(self.attr_value is not None))
            if self.state == self.SUBSCRIBED and prev != self.attr_value.value:
                self.err_count+=1
                if self.err_count > 3:
                    self.warning('Value differred after KeepAlive period, reactivating Polling')
                    self.activatePolling()
        except Exception,e:
            # fakeAttributeValue initialized with full_name
            traceback.print_exc()
            self.attr_value = fakeAttributeValue(self.full_name,value=e,error=e)
        self.last_poll = now
        self.fireEvent(EventType.PERIODIC_EVENT,self.attr_value)

    def subscribeEvents(self):
        self.debug('subscribeEvents(state=%s)'%(self.state))
        if self.state == self.SUBSCRIBED:
            raise Exception('AlreadySubscribed!')
        
        self.state = self.SUBSCRIBING
        for type_ in EventType.names.values():
            try:
                if self.event_ids.get(type_) is not None:
                    self.debug('\tevent %s already subscribed'%type_)
                    continue
                self.event_ids[type_] = self.proxy.subscribe_event(
                    self.simple_name,type_,self,[],False)
                self.state = self.SUBSCRIBED
            except:
                self.debug('\tevent %s not subscribed'%type_)
        
        if not self.state == self.SUBSCRIBED:
            self.debug('event subscribing failed, switching to polling')
            self.state = self.PENDING
            self.activatePolling()
            for type_ in (EventType.CHANGE_EVENT,EventType.ATTR_CONF_EVENT):
                self.event_ids[type_] = self.proxy.subscribe_event(
                    self.simple_name,type_,self,[],True)
                
    def unsubscribeEvents(self):
        for type_,ID in  self.event_ids.items():
            try:
                self.proxy.unsubscribe_event(ID)
                self.event_ids.pop(type_)
            except:
                pass
        if not self.hasListeners() and not self.isPollingForced:
            self.deactivatePolling()
        self.state = self.UNSUBSCRIBED

    def isUsingEvents(self):
        return self.state == self.SUBSCRIBED
    
    def enablePolling(self):
        self.activatePolling()

    def disablePolling(self):
        self.deactivatePolling()

    def isPollingEnabled(self):
        return self.isPollingActive()

    def activatePolling(self,period = None):
        self.polling_period = period or self.polling_period
        self.polled = True
        print('activatePolling(%s,%s)'%(self.full_name,self.polling_period))
        if self.isUsingEvents():
            self.forced = True
        if not self.manager().get_started(): self.manager().start()
        #self.factory().addAttributeToPolling(self, self.getPollingPeriod())

    def deactivatePolling(self):
        print('deactivatePolling(%s,%s)'%(self.full_name,self.state))        
        self.polled = False
        self.forced = False
        #self.factory().removeAttributeFromPolling(self)

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

    def _listenerDied(self, weak_listener):
        try:
            self.listeners.remove(weak_listener)
        except Exception, e:
            pass

    def addListener(self, listener):
        self.debug('addListener(%s)'%listener)
        if not self.manager().get_started():
            self.manager().start()
        if self.full_name not in self.manager().sources:
            self.manager().sources[self.full_name] = self
            self.last_poll = time.time()
        if self.state == self.UNSUBSCRIBED:
            self.subscribeEvents()
        import weakref
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
    
    def decodeAttrInfoEx(self,attr_conf):
        pass
    
    def push_event(self,event):
        #source,type_,value):
        try:           
            self.counters['total_events']+=1
            now = time.time()
            type_ = event.event       
            self.counters[type_]+=1
            delay = now-ctime2time(event.reception_date)
            if delay > 1e3 : print('push_event was %f seconds late'%delay)            
            self.state = self.SUBSCRIBED

            if event.err:
                self.last_error = event
                value = event.errors[0]
                reason = event.errors[0].reason
                print('ERROR in %s(%s): %s(%s)'%(self.full_name,type_,type(value),reason))
                if reason in EVENT_TO_POLLING_EXCEPTIONS:
                    self.state = self.PENDING
                    self.activatePolling()
                    return
            elif isinstance(event,PyTango.AttrConfEventData):
                value = event.attr_conf
                self.decodeAttrInfoEx(value)
                #(Taurus sends here a read cache=False instead of AttrConf)
            else:
                try:
                    value = event.attr_value
                except:
                    self.warning('push_event(%s): no value in %s'%(type_,dir(event)))
                    value = None

            if self.isPollingActive() and not self.isPollingForced():
                self.deactivatePolling()
            self.last_event = event    
            #Instead of firingEvent, I return and pass the value to the queue
            self.manager().put((self,type_,value))
        except:
            print(type(event),dir(event))
            traceback.print_exc()

    def fireEvent(self, event_type, event_value, listeners=None):
        """sends an event to all listeners or a specific one"""
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
                
class TangoEventSource(EventSource):
        pass

###############################################################################

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
    #pass

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

if __name__ == '__main__':
    import fandango.callbacks as fb
    es = fb.EventSource('test/events/1/currenttime')
    el = fb.EventListener('tester')
    es.addListener(el)
    
