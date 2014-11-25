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

import PyTango
import sys
import os
import time
import threading
import re
from copy import *
from excepts import getLastException

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

