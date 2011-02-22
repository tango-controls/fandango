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
##      EventsList, EventReceivers, StatesList, AttributesList, GlobalCallback
##      ... EventReceivers must be substituted by DevicesList
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
@li EventsList[attr_name]  the last event received for each attribute
@li StatesList[dev_name] keeps the last State read for each device
@li AttributesList[dev_name] keeps the last AttributeValue struct for each attribute. 

@remarks Mostly used by PyStateComposer device

It provides persistent storage.
lock.acquire and lock.release should be used to prevent threading problems!, 
Use of the lists inside push_event is safe
"""

EventsList = {}
EventReceivers = {}
StatesList = {}
AttributesList = {}

class EventStruct():
	name = ''
	event = None
	receivers = []

class TAttr(EventStruct):
	""" 
    This class is used to keep information about events received, 
    example of usage inside device.DevChild 
    """
	def __init__(self,name):
		self.name=name
		self.event=None #This is the last event received
		self.event_id=None #This is the ID received when subscribing
		self.dp=None #This is the device proxy
		self.dev_name=''
		self.receivers=[] #This is the list of composers that must receive this event
		self.attr_value=None
		self.State=PyTango.DevState.UNKNOWN
	def __str__(self):
		return str(name)+","+str(self.event)+","+TangoStates[self.State]+";"
	def set(self, event):
		self.event=event#copy(event)
		self.attr_value=self.event.attr_value
	
class AsynchronousFunction(threading.Thread):
    '''This class executes a given function in a separate thread
    When finished it sets True to self.finished, a threading.Event object 
    Whether the function is thread-safe or not is something that must be managed in the caller side.
    If you want to autoexecute the method with arguments just call: 
    t = AsynchronousFunction(lambda:your_function(args),start=True)
    while True:
        if not t.isAlive(): 
            if t.exception: raise t.exception
            result = t.result
            break
        print 'waiting ...'
        threading.Event().wait(0.1)
    print 'result = ',result
    '''
    def __init__(self,function):
        """It just creates the function object, you must call function.start() afterwards"""
        self.function  = function
        self.result = None
        self.exception = None
        self.finished = threading.Event()
        self.finished.clear()
        threading.Thread.__init__(self)
        self.wait = self.finished.wait
        self.daemon = False
    def run(self):
        try:
            self.wait(0.01)
            self.result = self.function()
        except Exception,e:
            self.result = None            
            self.exception = e
        self.finished.set() #Not really needed, simply call AsynchronousFunction.isAlive() to know if it has finished
        

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
		self.PermittedExceptions=[]
	def push_event(self,event):
		print 'in EventCallback.push event'
		self.lock.acquire()
		try:
			print "in EventCallback.push_event(",event.device,": ",event.attr_name,")"
			if not event.err and event.attr_value is not None:
				print "Event: ",event.attr_name,"=", event.attr_value.value
				self.TimeOutErrors=0
				EventsList[event.attr_name.lower()].set(event)
				if event.attr_name.lower().endswith('/state'):
					StatesList[event.device.lower()]=event.attr_value.value
				AttributesList[event.attr_name.lower()]=event.attr_value
			else:
				print 'Received an Error Event!: ',event.errors
				EventsList[event.attr_name.lower()].set(event)
				if event.attr_name.lower().endswith('/state'):
					StatesList[event.device.lower()]=PyTango.DevState.UNKNOWN
				AttributesList[event.attr_name.lower()]=None
				#if 'OutOfSync' in event.errors[0]['reason']:
				if [e for e in event.errors 
					if hasattr(e,'keys') and 'reason' in e.keys() 
						and not any([re.findall(exp,e['reason'].lower()) for exp in self.PermittedExceptions])
					]:
					print 'callbacks=> DISCARDED EVENT %s.%s.%s FOR SAFETY REASONS!!!' \
						%(event.device,event.attr_name,e['reason'])
					self.TimeOutErrors+=1
					self.lock.release()
					return
				else: self.TimeOutErrors=0
			#Launching Device.push_event()				
			#dev = event.device
			for rec in EventsList[event.attr_name].receivers:
				if rec in EventReceivers.keys(): EventReceivers[rec].push_event(event)
				elif hasattr(rec,'push_event'): rec.push_event(_event)
				elif isinstance(rec,threading.Event): rec.set()
				elif callable(rec): rec()
				else: raise 'UnknownEventReceiverType'
		except Exception,e:
			print 'exception in EventCallback.push_event(): ',e, ";", getLastException()
		self.lock.release()

#THIS IS THE EVENTS CALLBACK SINGLETONE:
GlobalCallback = EventCallback()

def subscribeToAttribute(subscriber,att_name):
	"""
	subscriber: a DeviceImpl object or the name of an already subscribed object
	attribute: the FULL_NAME of the attribute to subscribe
	"""
	if att_name.count('/')<3: raise 'subscribeToAttribute_IncompleteAttributeName'
	if isinstance(subscriber,PyTango.DeviceImpl):
		EventReceivers[subscriber.get_name()]=subscriber
	elif isinstance(subscriber,str):
		subscriber=EventReceivers[subscriber]
	else: raise 'subscribeToAttribute_UnknownSubscriberException'
	
	if not att_name in EventsList.keys():
		print 'subscribeToAttribute(%s,%s)'%(subscriber.get_name(),att_name)
		EventsList[att_name] = TAttr(att_name)
		EventsList[att_name].receivers.append(subscriber)
		EventsList[att_name].event_id = self.dp.subscribe_event(att,PyTango.EventType.CHANGE_EVENT,GlobalCallback,[],True)
		EventsList[att_name].dev_name = att_name.rsplit('/',0)
		AttributesList[att_name]=None #it could be done inside EventsList?!?!? ... or could AttributeList substitute EventsList?
		
		#It will not be initialized here ... as it differs in DevChild an DevsList
		#EventsList[att_name].dp = self.dp
		if att=='State': #DevsList should substitute that
			StatesList[EventsList[att_name].dev_name]=PyTango.DevState.UNKNOWN
			
		print "In ", self.get_name(), "::check_dp_attributes()", ": Listing Device/Attributes in EventsList:"
		for a,t in EventsList.items(): print "\tAttribute: ",a,"\tDevice: ",t.dev_name,"\n"
	else:
		print "In ", self.get_name(), "::check_dp_attributes(",att_name,")", ": This attribute is already in the list, adding composer to receivers list."
		if not subscriber.get_name() in EventsList[att_name].receivers and not subscriber in EventsList[att_name].receivers:
			EventsList[att_name].receivers.append(subscriber)
	pass

def inStatesList(devname):
	print 'callbacks.inStatesList ...'
	GlobalCallback.lock.acquire()
	print 'Checking if %s in %s.'%(devname,str(StatesList.keys()))
	value=bool(devname.lower() in StatesList.keys())
	GlobalCallback.lock.release()
	return bool
		
def getStateFor(devname):
	print 'callbacks.getStateFor	 ...'
	GlobalCallback.lock.acquire()
	state = StatesList[devname.lower()] if devname.lower() in StatesList.keys() else None
	GlobalCallback.lock.release()
	return state

def setStateFor(devname,state):
	print 'callbacks.setStateFor	 ...'
	GlobalCallback.lock.acquire()
	StatesList[devname.lower()]=state
	GlobalCallback.lock.release()
	return state

def setAttributeValue(attr_name,attr_value):
	print 'callbacks.setAttributeValue(%s)'%attr_name
	GlobalCallback.lock.acquire()
	AttributesList[attr_name.lower()]=attr_value
	GlobalCallback.lock.release()
	return attr_value	

def inAttributesList(attname):
	GlobalCallback.lock.acquire()
	value=bool(attname.lower() in AttributesList.keys())
	GlobalCallback.lock.release()
	return bool

def getAttrValueFor(attname):
	GlobalCallback.lock.acquire()
	value=AttributesList[attname.lower()]
	GlobalCallback.lock.release()
	return value

def inEventsList(attname):
	GlobalCallback.lock.acquire()
	value=bool(attname.lower() in EventsList.keys())
	GlobalCallback.lock.release()
	return bool

def getEventFor(attname):
	GlobalCallback.lock.acquire()
	event=EventsList[attname.lower()]
	GlobalCallback.lock.release()
	return event

