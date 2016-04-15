#!/usr/bin/env python2.5
"""
#############################################################################
##
## file :       devslist.py
##
## description : see below
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

There's two things that must be done in this module:

    Keep a list with all the devices within a device server, or used by a device server
        Objects will be instances of Device3_Impl or DeviceProxy
        
    The AttributeProxy must have a list of all attributes, and the subscribers for them!
        And attribute must be checked before adding it to the list.
        Firing of events must be thread-safe (threading.Event, threading.Lock)
"""
"""
#---------------------------------------------------------------------------
# THIS CLASS IS A DUPLICATION OF WHAT IS DONE IN CALLBACKS?
# Not if it is use to manage the duality Instance/DProxy for devices that run in the same server or others
# It should replace the calls to DeviceProxy done inside device.DevChild or PyStateComposer
#---------------------------------------------------------------------------

To this class should be added all the devices in a device server, and all the devices that are referenced from them.
It includes all the Parent devices for those abstract devices running in the server.
It will centralize the DeviceProxy access, and will avoid its use when internal communication is possible.
"""

import PyTango
import threading
import objects

#These objects will be used by DeviceServer to create PyTango.PyUtil and PyTango.Util and keep servers data
#py = None
#U = None

class DeviceList(dict):
    ''' 
    DevicesList is a dictionary that provides some additional elements to be used with Tango Devices:
        The dictionary can be used to link a device name to any type of object, but additional methods are used to manage DeviceProxies
            isProxy(name): returns True if the object is a DeviceProxy
            subscribe(name,_event): each device has a list of 'subscribers', this method allows to add a new object to the list
            
    __subscribers will keep a list of methods to be called each time that a device receives an event
    
    * __len__( self)
    * __getitem__( self, key)
    * __setitem__( self, key, value)
    * __delitem__( self, key)
    * __iter__( self)
    * __contains__( self, item)

    '''
    MAX_ERRORS=10.0
    MIN_PERIOD=3.0 #This is the min period between read_attribute executions
    TIME_WAIT=15.0 #Time to wait between check_proxies execution
    
    def __init__(self,_dict={}):
        dict.__init__(self,_dict)
        self.__db = PyTango.Database()
        self.state=PyTango.DevState.INIT
        
        self.dp_event=threading.Event()
        self.dp_stopEvent=threading.Event()
        self.dp_lock=threading.Lock()

        #Add this line to always_executed_hook:
        #     if hasattr(self,'ForceParentPolling') and self.ForceParentPolling and not self.ParentPolledAttributes: self.force_ParentAttributes_polling()
        #self.dp_force_polling=ForcePolling
        #self.ParentPolledAttributes=[]
        
        #self.MAX_ERRORS=MAX_ERRORS
        #self.MIN_PERIOD=3.0 

        self.dp_errors = 0
        
        self.check_dp_thread=threading.Thread(None,self.check_proxies,'check_proxies')
        self.check_dp_thread.setDaemon(False)

        #The Thread must be started once all the listeners have been initialized ... in always_executed_hook?
        #if not self.check_dp_thread.isAlive():
            #self.check_dp_thread.start()        
        
        pass
    
    def __setitem__(self,key,value):
        dict.__setitem__(self,key,innerDevice(value))
    
    def append(self,value):
        if isinstance(value,PyTango.DeviceImpl): key=value.get_name()
        elif isinstance(value,PyTango.DeviceProxy): key=value.name()
        elif isinstance(value,str): key=value
        self.__setitem__(key,value)
    def add(self,value): self.append(value)
    
    def init_proxy(self,key,value):
        self.__setitem__(key,value)

    def get_state(self): return self.state
    def set_state(self,_state): self.state=_state

    
    def isAlive(self): return self.check_dp_thread.isAlive()
    def start(self): 
        if not self.isAlive(): 
            self.check_dp_thread.start()
        
    def check_proxies(self):
        ''' This method performs the parent's device proxy checking
        It changes the state to Unknown if there's no connection to the device
        The state is set to INIT when the connection is restablished
        stop_threads and dp_event help to control the deletion of the thread
        '''
        #signal.signal(signal.SIGTRAP,self.delete_device)
        #signal.signal(signal.SIGABRT,self.delete_device)
        #signal.signal(signal.SIGKILL,self.delete_device)
        while not self.dp_stopEvent.isSet():
            for dname,idev in self.iteritems():
                if self.dp_stopEvent.isSet(): break
                print '*'*80
                print 'in DevsList.check_proxies, ...'
                print '*'*80
                
                self.dp_lock.acquire()
                if self[dname].State==PyTango.DevState.UNKNOWN:
                    print 'in DevsList.check_proxies, [%s] is UNKNOWN'%dname
                    try:
                        idev.dp = PyTango.DeviceProxy(dname)
                        idev.dp.set_timeout_millis(1000)
                        idev.State=PyTango.DevState.INIT
                        idev.dp.ping()
                        #idev.check_dp_attributes()
                        idev.dp_errors=0
                        idev.last_time=time.time()                    
                        print "In DevsList.check_proxies: proxy to "+self.ParentName+" device initialized."
                    except Exception,e:
                        print 'EXCEPTION in DevsList.check_proxies:, %s Proxy Initialization failed!'%dname,getLastException()
                        idev.State=PyTango.DevState.UNKNOWN
                        idev.dp_errors+=1
                        #del self.dp; self.dp=None
                else:
                    try:
                        idev.dp.ping()
                        #idev.check_dp_attributes_epoch()
                    except Exception,e:
                        print 'EXCEPTION in DevsList.check_proxies, Ping to device ',self.ParentName,' failed!: ',getLastException()
                        idev.State=PyTango.DevState.UNKNOWN
                        self.dp_errors+=1
                        #del self.dp; self.dp=None
                
                if all([v.State==UNKNOWN for v in self.values()]):
                    self.set_state(PyTango.DevState.UNKNOWN)
                elif idev.State==PyTango.DevState.INIT:
                    self.set_state(PyTango.DevState.INIT)
                elif idev.State!=PyTango.DevState.UNKNOWN:
                    self.set_state(PyTango.DevState.RUNNING)

                self.dp_lock.release()
                self.dp_event.wait(self.MIN_PERIOD)
            
            self.dp_event.wait(self.TIME_WAIT)
        
        #if self.dp: del self.dp
    pass
                
#ListOfDevices=DevicesList()
DeviceList=DeviceList()
                
class innerDevice(objects.Object):
    def __init__(self,device):
        if isinstance(device,PyTango.DeviceProxy):
            self.dp=proxy
        elif isinstance(device,PyTango.DeviceImpl):
            if hasattr(device,'myProxy'):
                self.dp=device.myProxy
            else:
                self.dp=PyTango.DeviceProxy(device.get_name())
                device.myProxy=self.dp
        elif isinstance(device,str):
            self.dp=PyTango.DeviceProxy(device)
        else:
            raise 'innerDevice_UnknownArgumentType'
        
        self.State=PyTango.DevState.UNKNOWN
        self.name=self.dp.name()
        self.admin=self.dp.adm_name()
        self.subscribers=[] #This will be a list of objects, each being a device, a threading.Event or a method to be called
        self.last_comm=''
        self.last_time=0. #Last succesful communication
        self.last_retry=0. #Last communication retry
        self.last_update={} #Dictionary with the last update time for each attribute
        self.dp_errors=0
        self.attributeList=[]
        pass
    def isProxy(self): 
        return isinstance(self.dp,PyTango.DeviceProxy)
    def push_event(self,_event):
        for rec in self.subscribers:
            if hasattr(rec,'push_event'): rec.push_event(_event)
            elif isinstance(rec,threading.Event): rec.set()
            elif callable(rec): rec()
    pass

#class innerDevProxy(objects.Object):
    #""" This class will be used to simulate a PyTango.DeviceProxy for those devices running within the same device server """
    #def __init__(self,DI=None):
        #self.DevImpl=DI
        #pass
    #def __del__(self):
        #pass
    #def ping(self):
        #return True
        #pass
    #def state(self): return self.DevImpl.get_state()
    #def get_name(self): return self.DevImpl.get_name()
    
    #def command_inout(self,comm,argin): return getattr(self.DevImpl,comm)(argin)

    #def read_attribute(self,aname):
        ##attlist=self.get_attribute_list()
        #multiattr=self.get_device_attr()
        #attr=multiattr.get_attr_by_name(aname)
        #if isinstance(self.DevImpl,dynamic.DynamicDS) and aname in self.DevImpl.get_dyn_attr_list()::
            #return self.DevImpl.read_dyn_attr(attr)
        #else: return getattr(self.DevImpl,'read_'+attr.get_name())(attr)
    #def write_attribute(self,attribute,attvalue): 
        #raise 'innerDevProxyException_READONLY'
        
    #def subscribe_event(self):
        #pass
    #def get_attribute_list(self,All=True):
        #attr_list = []
        #if All: attr_list = self.DevImpl.get_device_class().attr_list.keys()
        #if isinstance(self.DevImpl,dynamic.DynamicDS):
            #attr_list = attr_list + self.DevImpl.get_dyn_attr_list()
        #pass
    #pass

#class AttributesList(dict):
    #def addAttribute(self,dev):
        #''' It returns a threading.Event that will be set each'''
        #event=threading.Event() 
        #return event
        #pass
    #def updateAttribute(self,dev):
        
        #pass
    #pass