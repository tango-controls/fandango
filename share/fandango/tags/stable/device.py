#!/usr/bin/env python2.5
""" @if gnuheader
#############################################################################
##
## file :       device.py
##
## description : CLASS FOR Enhanced TANGO DEVICE SERVERs
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
@endif
@package device
@brief provides Dev4Tango, StateQueue, DevChild
@todo @warning IMPORTING THIS MODULE IS CAUSING SOME ERRORS WHEN CLOSING PYTHON DEVICE SERVERS,  BE CAREFUL!
"""

import PyTango
import sys
import inspect
import threading
import time
import traceback
import exceptions
import operator
from PyTango import AttrQuality
import log
import excepts
from excepts import *
import callbacks
from callbacks import *

if 'Device_4Impl' not in dir(PyTango):
    PyTango.Device_4Impl = PyTango.Device_3Impl

#TangoDatabase singletone
try:
    TangoDatabase = PyTango.Database()
except:
    TangoDatabase = None

class Dev4Tango(PyTango.Device_4Impl,log.Logger):
    """
    This class provides several new features to TangoDevice implementations.
    By including log.Logger it also includes objects.Object as parent class.
    It allows to use call__init__(self, klass, *args, **kw) to avoid multiple inheritance from same parent problems.
    Therefore, use self.call__init__(PyTango.Device_4Impl,cl,name) instead of PyTango.Device_4Impl.__init__(self,cl,name)
    """

    ##@name State Machine methods
    #@{
    
    def is_Attr_allowed(self, req_type): 
        """ This method is a template for any Attribute allowed control. """
        self.info( 'In is_Attr_allowed ...' )
        return bool( self.get_state() not in [PyTango.DevState.UNKNOWN,PyTango.DevState.INIT] )
    
    def State(self):
        """ State redefinition is required to keep independency between 
        attribute configuration (max/min alarms) and the device State """
        return self.get_state()
    
    # DON'T TRY TO OVERLOAD STATUS(), It doesn't work that way.    
    #def Status(self):
    #    print '... IN ',str(self.__class__.__bases__),'.STATUS ...'
    #    # BE CAREFUL!: dev_status() executes Status() in a recursive way!!!!
    #    return str(self.get_status())
    
    def default_status(self):
        """ Default status """
        return 'Device is in %s State'%str(self.get_state())
      
    def read_ShortStatus(self):
        """ This reduced Status allows Status attribute to be archived (a ShortStatus attribute must exist) """
        return self.get_status()[:128]
        
    ##@}
    
    ##@name Attribute hacking methods
    #@{

    def getAttributeTime(self,attr_value):
        """ AttributeValue.time is of Type TimeVal={tv_sec,tv_usec,...}, not accepted by set_attribute_value_date_quality method of DeviceImpl """
        if type(attr_value) is float: return attr_value
        elif type(attr_value.time) is float: return attr_value.time  
        else: return float(attr_value.time.tv_sec)+1e-6*float(attr_value.time.tv_usec)
        
    class forcedAttributeValue(object):
        """ This class simulates a modifiable AttributeValue object (not available in PyTango)"""
        def __init__(self,name,value,time_=0.,quality=PyTango.AttrQuality.ATTR_VALID,dim_x=1,dim_y=1):
            self.name=name
            self.value=value
            self.time=time_ or time.time()
            self.quality=quality
            self.dim_x=dim_x
            self.dim_y=dim_y
            
    ##@}
    
    ##@name Device management methods
    #@{
    
    def init_my_Logger(self):
        """ A default initialization for the Logger class """ 
        print 'In %s.init_my_Logger ...'%self.get_name()
        try:
            #Check if this class inherits from Logger
            if isinstance(self,log.Logger):
                self.call__init__(log.Logger,self.get_name(),format='%(levelname)-8s %(asctime)s %(name)s: %(message)s')
                if hasattr(self,'LogLevel'): self.setLogLevel(self.LogLevel)
                self.info('Logger streams initialized (error,warning,info,debug)')
            else:
                raise Exception('LoggerNotInBaseClasses')
        except Exception,e:
            print '*'*80
            print 'Exception at init_my_Logger!!!!'
            print str(e)        
            print '*'*80
            #so, this class is not a new style class and doesn't have __bases__
            self.error = lambda s: sys.stderr.write('ERROR:\t%s\n'%s)
            self.warning= lambda s: sys.stdout.write('WARNING:\t%s\n'%s)
            self.info= lambda s: sys.stdout.write('INFO:\t%s\n'%s)
            self.debug= lambda s: sys.stdout.write('DEBUG:\t%s\n'%s)            
            pass
        #if init_fun is not None: self.init_fun()
    
    def check_Properties(self,props_list):
        """ It verifies that all properties has been initialized """
        print 'In check_Properties ...'
        if not all([hasattr(self,p) for p in props_list]): return False
        else: return all([getattr(self,p) for p in props_list])        
    
    def get_device_properties(self,myclass):
        self.debug('In Dev4Tango.get_device_properties(%s) ...' % str(myclass))
        PyTango.Device_4Impl.get_device_properties(self,myclass)
        #self.get_device_properties(self.get_device_class())
        missing_properties = {}
        for k in myclass.device_property_list.keys():
            default = myclass.device_property_list[k][2] #this value is always a list!
            if k not in dir(self):
                missing_properties[k]=default
            else:
                value = self.__dict__[k]
                if not isinstance(value,list): value = [value]
                if value==default:
                    missing_properties[k]=value
        if missing_properties:
            try:
                TangoDatabase.put_device_property(self.get_name(),missing_properties)
            except Exception,e:
                print 'Exception in Dev4Tango.get_device_properties():\n'+str(e)
                
    def update_properties(self,property_list = []):
        property_list = property_list or self.get_device_class().device_property_list.keys()
        self.debug('In Dev4Tango.update_properties(%s) ...' % property_list)        
        #self.db = self.prop_util.db
        if not hasattr(self,'db') or not self.db: self.db = PyTango.Database()
        props = dict([(key,getattr(self,key)) for key in property_list if hasattr(self,key)])
        for key,value in props.items():
            print 'Updating Property %s = %s' % (key,value)
            self.db.put_device_property(self.get_name(),{key:isinstance(value,list) and value or [value]})                
    ##@}
        
class TimedQueue(list):
    """ A FIFO that keeps all the values introduced at least for a given time.
    Applied to some device servers, to force States to be kept at least a minimum time.
    Previously named as device.StateQueue
    pop(): The value is removed only if delete_time has been reached.
    at least 1 value is always kept in the list
    """
    def __init__(self,arg=None):
        """ Initializes the list with a sequence or an initial value. """
        if arg is None:
            list.__init__(self)
        elif operator.isSequenceType(arg):
            list.__init__(self,arg)
        else:
            list.__init__(self)
            self.append(arg,1)
    def append(self,obj,keep=15):
        """ Inserts a tuple with (value,insert_time,delete_time=now+keep) """
        now=time.time()
        l=(obj,now,now+keep)
        list.append(self,l)
    def pop(self,index=0):
        """ Returns the indicated value, or the first one; but removes only if delete_time has been reached.
        All values are returned at least once.
        When the queue has only a value, it is not deleted.
        """
        if not self: return None #The list is empty
        now=time.time()
        s,t1,t2 = self[index]
        if now<t2 or len(self)==1:
            return s
        else:
            return list.pop(self,index)[0]
    def index(self,obj):
        for i in range(len(self)): 
            if self[i][0]==obj: return i
        return None
    def __contains__(self,obj):
        for t in self: 
            if t[0]==obj: return True
        return False
    pass

class DevChild(Dev4Tango):
    """
    Inherit from this class, it provides EventManagement, Dev4Tango, log.Logger, objects.Object and more ...
    To take profit of event management, the Child Class should redeclare its own PushEvent method!!!
    
    ADD THIS LINE TO YOUR always_executed_hook METHOD:
        DevChild.always_executed_hook(self)
    """
    def init_DevChild(self, ParentName=None, ParentAttributes=None, EventHook=None,Wait=15, ForcePolling=False, MAX_ERRORS=10):
        """ Initialize your eventReceiver device:
            ParentName: device from which attributes are read
            ParentAttributes: list of attributes to keep updated
            EventHook: method to be called for each event; is not being used, push_event is called by default and must be redefined
            Wait: time between DeviceProxy.ping() executions    
            ForcePolling: forces polling in all attributes listed, it can be directly the period to force
        call this method once the properties self.ParentName and self.ParentAttributes has been verified """
        print "In %s.init_DevChild ..." % self.get_name()
        if not self.check_Properties(['ParentName','ParentAttributes']) and all([ParentName,ParentAttributes]):
            self.ParentName=ParentName
            self.ParentAttributes=ParentAttributes
        EventReceivers[self.get_name()]=self
        #The eventHook is not being used, push_event is called by default and must be redefined
        #self.EventHook=EventHook
        self.dp=None
        self.dp_event=threading.Event()
        self.dp_stopEvent=threading.Event()
        self.dp_lock=threading.Lock()
        self.stop_threads=False
        self.dp_wait=Wait
        self.dp_force_polling=ForcePolling
        self.ParentPolledAttributes=[]
        #Add this line to always_executed_hook: if hasattr(self,'ForceParentPolling') and self.ForceParentPolling and not self.ParentPolledAttributes: self.force_ParentAttributes_polling()
        self.MAX_ERRORS=MAX_ERRORS
        self.dp_errors = 0
        
        self.lastcomm=''
        self.lasttime=0. #Time of last communication
        
        self.last_updates={} #This dictionary records the last time() when each attribute was read
        self.last_retries={} #This dictionary records the last retry (succeded or failed)
        self.MIN_PERIOD=3.0 #This is the min period between read_attribute executions
        
        self.check_dp_thread=threading.Thread(None,self.check_ParentProxy,'check_dp')
        self.check_dp_thread.setDaemon(True)
        self.GARBANZO = None        
        #self.check_dp_thread.start()
        
    def delete_device(self):
        print "[Device delete_device method] for DevChild"
        self.dp_stopEvent.set()
        self.dp_event.set() #Wake up threads
        del self.dp
        
        
    def always_executed_hook(self):
        self.info('In DevChiled.always_executed_hoot()')
        if hasattr(self,'ForceParentPolling') and self.ForceParentPolling and not self.ParentPolledAttributes:
            self.force_ParentAttributes_polling()
        if not self.check_dp_thread.isAlive():
            self.info('In DevChiled.always_executed_hook(): CheckProxy thread is not Alive!')
            self.check_dp_thread.start()
        
    def comms_report(self):        
        return     '\n'.join([','.join(self.ParentAttributes)+' Attributes acquired from '+self.ParentName+' Device. ',
                'Last communication was "'+self.lastcomm+'" at '+time.ctime(self.lasttime)+'.'])
    
    def check_ParentProxy(self):
        ''' This method performs the parent's device proxy checking
        It changes the state to Unknown if there's no connection to the device
        The state is set to INIT when the connection is restablished
        stop_threads and dp_event help to control the deletion of the thread
        '''
        #signal.signal(signal.SIGTRAP,self.delete_device)
        #signal.signal(signal.SIGABRT,self.delete_device)
        #signal.signal(signal.SIGKILL,self.delete_device)
        while not self.dp_stopEvent.isSet():
            self.info('*'*80)
            self.info('in check_ParentProxy, ...')
            self.info('*'*80)
            #The dp_event.wait(60) is done at the end of the loop
            try:
                self.dp_lock.acquire(False)
                if self.get_state()==PyTango.DevState.UNKNOWN:
                    self.warning('in check_ParentProxy, self.DevState is UNKNOWN')
                    try:
                        self.dp = PyTango.DeviceProxy(self.ParentName)
                        self.Parent = self.dp #Parent is an Alias for the device proxy
                        self.dp.set_timeout_millis(1000)
                        self.set_state(PyTango.DevState.INIT)
                        self.dp.ping()
                        self.check_dp_attributes()
                        self.dp_errors=0
                        self.lasttime=time.time()                    
                        self.info("In check_ParentProxy(): proxy to %s device initialized."%self.ParentName)
                    except Exception,e:
                        self.error('EXCEPTION in check_ParentProxy():, %s Proxy Initialization failed! %s'%(self.ParentName,getLastException()))
                        self.set_state(PyTango.DevState.UNKNOWN)                    
                        self.dp_errors+=1
                        #del self.dp; self.dp=None
                else:
                    try:
                        self.dp.ping()
                        self.check_dp_attributes_epoch()
                    except Exception,e:
                        self.error('EXCEPTION in check_ParentProxy(), Ping to device %s failed!: %s'%(self.ParentName,getLastException()))
                        self.set_state(PyTango.DevState.UNKNOWN)
                        self.dp_errors+=1
                        #del self.dp; self.dp=None
            except Exception,e:
                self.error('Something failed in check_ParentProxy()!: %s'%traceback.format_exc)
            finally:
                self.dp_lock.release()
                self.dp_event.wait(self.dp_wait)
        self.info('*'*80)
        self.info('check_ParentProxy, THREAD EXIT!')
        self.info('*'*80)
        #if self.dp: del self.dp
        
    def getParentProxy(self):
        return self.Parent
        
    def check_dp_attributes(self):
        self.info("In check_dp_attributes ...")
        attrs = self.dp.get_attribute_list()
        for att in [pa.lower() for pa in self.ParentAttributes]:
            if att not in [a.lower() for a in attrs]:
                self.info("In check_dp_attributes(): "+self.ParentName+" doesn't have "+att+" attribute!")
                raise Exception('MissingParentAttribute_%s'%att)
            elif att not in self.last_updates.keys():
                self.last_updates[att]=0
                
        #Configure the attribute polling
            if not self.dp.is_attribute_polled(att) and self.dp_force_polling:
                ''' OJO!
                Absolute and relative changes should be set previously!!!!
                '''
                print '*'*80
                print self.get_name(),'.check_dp_attributes(): forcing ',att,' polling to ',argin
                print '*'*80
                period = self.dp.get_attribute_poll_period(att) or (int(self.dp_force_polling)>1000 or 3000)
                self.dp.poll_attribute(att,period)
                print self.get_name(),".poll_attribute(",att_name,",",period,")"
                
            try:
                GlobalCallback.lock.acquire()
                if self.dp.is_attribute_polled(att):
                    #
                    # CONFIGURING EVENTS
                    #
                    att_name = att if len(att.split('/'))>2 else ('/'.join([self.ParentName,att])).lower()
                    if not att_name in EventsList.keys():
                        self.info('check_dp_attributes: subscribing event for %s'%att_name)
                        EventsList[att_name] = TAttr(att_name)
                        EventsList[att_name].receivers.append(self.get_name())
                        if 'CHANGE_EVENT' not in dir(PyTango.EventType): PyTango.EventType.CHANGE_EVENT = PyTango.EventType.CHANGE
                        event_id = self.dp.subscribe_event(att,PyTango.EventType.CHANGE_EVENT,GlobalCallback,[],True)
                        #This last argument subscribe to not-running devices
                        # Global List
                        EventsList[att_name].dp = self.dp
                        EventsList[att_name].event_id = event_id
                        EventsList[att_name].dev_name = self.ParentName
                        AttributesList[att_name]=None
                        if att=='State':
                            StatesList[dev_name]=PyTango.DevState.UNKNOWN
                        self.info("In check_dp_attributes()\n Listing Device/Attributes in EventsList:")
                        for a,t in EventsList.items(): self.info("\tAttribute: %s\tDevice: %s"%(a,t.dev_name))
                    else:
                        self.info("In check_dp_attributes(%s) This attribute is already in the list, adding composer to receivers list."%att_name)
                        if not self.get_name() in EventsList[att_name].receivers:
                            EventsList[att_name].receivers.append(self.get_name())
                        # IT MUST BE DONE BY CALLBACK, NOT HERE
                        #if EventsList[att_name].attr_value is not None:
                        #    if att is 'State':
                        #        StatesList[dev_name]=EventsList[att_name].attr_value.value
                        #    else: 
                        #        AttributesList[dev_name]=EventsList[att_name].attr_value.value
                else:
                    #
                    # HERE POLLING SHOULD BE CONFIGURED
                    #
                    pass
            except Exception,e:
                self.error('Something failed in check_dp_attributes()!: %s'%traceback.format_exc)
                raise e
            finally:
                GlobalCallback.lock.release()
            
    def getParentState(self,dev_name=None):
        dev_name = dev_name or self.ParentName
        dState=callbacks.getStateFor(dev_name)
        if dState is not None:
            self.info('In DevChild(%s).getParentState(%s)=%s ... parent state read from callbacks'%(self.get_name(),dev_name,str(dState)))
        else:
            #print 'In DevChild(%s).getParentState(%s) ... Forcing an State Reading in the parent device.'%(self.get_name(),dev_name)
            try:
                attvalue=self.force_Attribute_reading('state')
                dState=attvalue.value
                self.info('In DevChild(%s).getParentState(%s)=%s, forced reading'%(self.get_name(),dev_name,str(dState)))
            except Exception,e:
                print 'In DevChild(%s).getParentState(%s) ... UNABLE TO READ PARENT STATE! (%s)'%(self.get_name(),dev_name,str(excepts.getLastException()))
                self.set_state(PyTango.DevState.UNKNOWN)
        return dState
    
    def force_Attribute_reading(self,att):
        now=time.time()
        attvalue=None
        last_update=self.getLastAttributeUpdate(att)
        self.info('In force_Attribute_reading ...'': Last update of attribute %s was at %s, just %s seconds ago.'%(att,time.ctime(last_update),str(now-last_update)))
        try:
            if att in self.last_retries.keys() and self.MIN_PERIOD>(self.last_retries[att]):
                self.info('DevChild.force_Attribute_reading at %s: read_attribute is not allowed with a frequency < 3 seconds (last was at %s)'%(time.ctime(now),time.ctime(self.lasttime)))
            else:
                #These variables should be recorded first, if it isn't an exception will ignore it!
                #Last update is recorded even if reading is not possible, to avoid consecutive retries
                self.last_retries[att]=now
                self.lasttime=now
                self.dp.ping()
                attvalue=self.dp.read_attribute(att)
                if attvalue: 
                    self.lastcomm='DeviceProxy.read_attribute(%s,%s)'%(att,str(attvalue.value))            
                    print 'Parent.%s was succesfully read: %s'%(att,str(attvalue.value))
                    if att=='state':
                        callbacks.setStateFor(self.ParentName,attvalue.value)
                    else:
                        callbacks.setAttributeValue(self.ParentName.lower()+'/'+att.lower(),attvalue)
                self.setLastAttributeUpdate(att,self.getAttributeTime(attvalue))
                return attvalue
        except PyTango.DevFailed,e:
            print 'PyTango.Exception at force_Attribute_reading: ',str(getLastException())
            err = e.args[0]
            PyTango.Except.throw_exception(str(err.reason),str(err.desc),str(err.origin))
        except Exception,e:
            print 'Exception at force_Attribute_reading: ',str(getLastException())
            PyTango.Except.throw_exception('DevChild_force_Attribute_readingException',str(e),'DevChild.force_Attribute_reading')
        pass
            
    class forcedEvent(object):
        def __init__(self,device,attr_name,attr_value,err,errors):
            self.device=device
            self.attr_name=attr_name
            self.attr_value=attr_value
            self.err=err
            self.errors=errors
            
    def check_dp_attributes_epoch(self):
        print '-'*80
        self.info('In check_dp_attributes_epoch() ...')
        print '-'*80
        now = time.time()
        for k,v in self.last_updates.items():
            self.debug('Last update of %s attribute was at %s'%(k,time.ctime(v)))
            if v < now-self.dp_wait: #If the last_update of the attribute is too old, it forces an error event
                print '*'*80
                print 'FORCING EVENT FOR ATTRIBUTE %s, after %s seconds delay'%(k,str(v-now))
                print '*'*80
                try:
                    GlobalCallback.lock.acquire()
                    #This is a recursive call, the push_event will schedule a future forceAttributeReading
                    event = self.forcedEvent(self.ParentName,self.ParentName+'/'+k,None,True,[
                        {'reason':'DevChild_PushEventForced','desc':'Attribute not updated in the last %s seconds'%self.dp_wait,'origin':'DevChild.check_dp_attributes_epoch'}])
                    self.push_event(event)
                except Exception,e: raise e
                finally: GlobalCallback.lock.release()
        pass

    #This is the only method that must be declared in the Child device side
    def push_event(self,event):
        try:
            self.error('THIS IS DevChild(',self.get_name(),').push_event(',event.device,".",event.attr_name,'=',str(event.attr_value),')!!!, It should have been redefined inside inheriting classes!')
            #att_name=(self.ParentName+'/'+self.ParentAttributes[0]).lower()
            #print "att_name is %s, event value is %s, attributelist is %s"%(att_name,event.attr_value and event.attr_value.value or 'None',AttributesList[att_name].value)        
            if att_name not in AttributesList.keys(): 
                raise Exception('DevChild_%sAttributeNotRegistered'%self.ParentAttributes[0])
        except Exception,e:
            print 'exception in push_event(): ',e, ";", traceback.format_exc()
            
    def setLastAttributeUpdate(self,att,date):
        self.last_updates[att]=date
        
    def getLastAttributeUpdate(self,att):
        return self.last_updates[att] if att in self.last_updates.keys() else 0.0
    
    def getLastUpdates(self):
        report=''
        for k,v in self.last_updates.items():
            report='\n'.join([report,'%s updated at %s'%(k,time.ctime(v))])
        return report
    
    def force_ParentAttributes_polling(self):
        #ForceParentPolling should be created as a DevVarStringArray Property before
        self.info("In force_ParentAttributes_polling()")                    
        if hasattr(self,'ForceParentPolling') and self.ForceParentPolling:
            if self.ForceParentPolling[0].isdigit():
                    period = int(self.ForceParentPolling[0])
                    # Forcing the period to be between 3.5 seconds and 1 minute, 3.5 seconds is the minimum to avoid modbus timeout to provoke a PollThreadOutOfSync_Exception
                    period = period<3500 and 3500 or period>60000 and 60000 or period
                    dev = PyTango.DeviceProxy(self.ParentName)
                    if len(self.ForceParentPolling)>1:
                        self.ParentPolledAttributes=self.ForceParentPolling[1:]
                    else:
                        al = dev.get_attribute_list()
                        pl = {}                            
                        for a in al:
                            pl[a]=dev.get_attribute_poll_period(a)
                            #print 'Parent Polled Attribute %s: %d'%(a,pl[a])
                        self.ParentPolledAttributes=[k for k,v in pl.items() if v>0 and v!=period]
                    #self.PolledAttributes=['CPUStatus']+self.ForcePolling[1:]
                    print 'ParentPolledAttributes=',str(self.ParentPolledAttributes)
                    for att in self.ParentPolledAttributes:
                        if att not in dev.get_attribute_list():
                            continue
                        try:                                
                            self.debug(self.get_name()+'.forceAutoPolling(): forcing '+att+' polling to '+str(period))
                            #ap = PyTango.AttributeProxy('/'.join([self.get_name(),att]))
                            #if ap.is_polled() : ap.stop_poll()
                            #ap.poll(period)
                            if dev.is_attribute_polled(att):
                                dev.stop_poll_attribute(att)
                            dev.poll_attribute(att,period)
                            #dev.read_attribute(att)
                        except PyTango.DevFailed,e:
                            err = e.args[0]
                            PyTango.Except.throw_exception(str(err.reason),str(err.desc),str(err.origin))
                        except Exception,e:
                            print 'Exception at force_ParentAttributes_polling: ',str(getLastException())
                            PyTango.Except.trhow_exception('DevChild_PollingParentAttributesException',str(e),'DevChild.force_ParentAttributes_polling')
                            #print str(e)
                            #raise e 
                        
                    if not self.ParentPolledAttributes: self.ParentPolledAttributes=[None]
                    del dev
        self.debug("In force_ParentAttributes_polling(), finished"%self.get_name())                            
    pass
    
    