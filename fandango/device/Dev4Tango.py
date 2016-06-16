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

This module is used to have all those classes used inside DeviceServers or to control/configure them 
and are not part of the Astor api (ServersDict)
"""

#pytango imports
import PyTango
import types
#fandango imports
import fandango as fun
from fandango.log import Logger,except2str,printf
from fandango.excepts import *
from fandango.callbacks import *
import fandango.tango as tango #Double import to avoid ambiguous naming of some methods
from fandango.tango import * #USE_TAU imported here, get_polled_attrs and other useful methods
from fandango.dicts import CaselessDefaultDict,CaselessDict
from fandango.arrays import TimedQueue
from fandango.dynamic import DynamicDS,USE_STATIC_METHODS


########################################################################################
## Device servers template

class Dev4Tango(PyTango.Device_4Impl,log.Logger):
    """
    This class provides several new features to TangoDevice implementations.
    By including log.Logger it also includes objects.Object as parent class.
    It allows to use call__init__(self, klass, *args, **kw) to avoid multiple inheritance from same parent problems.
    Therefore, use self.call__init__(PyTango.Device_4Impl,cl,name) instead of PyTango.Device_4Impl.__init__(self,cl,name)
    
    It also allows to connect several devices within the same server or not usint taurus.core
    """

    def trace(self,prio,s):
        printf( '4T.%s %s %s: %s' % (prio.upper(),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),self.get_name(),s))
            
    ##@name State Machine methods
    #@{
    
    def is_Attr_allowed(self, req_type): 
        """ This method is a template for any Attribute allowed control. """
        self.info( 'In is_Attr_allowed ...' )
        return bool( self.get_state() not in [PyTango.DevState.UNKNOWN,PyTango.DevState.INIT] )
    
    def set_state(self,state):
        self._state = state
        type(self).mro()[type(self).mro().index(Dev4Tango)+1].set_state(self,state)
        
    def get_state(self):
        #@Tango6
        #This have been overriden as it seemed not well managed when connecting devices in a same server
        if not hasattr(self,'_state'): self._state = PyTango.DevState.INIT
        if getattr(self,'UpdateAttributesThread',None) and 0<getattr(self,'last_update',0)<(time.time()-10*self.PollingCycle/1e3):
            #raise Exception('PollingThreadIsDead')
            self.set_state(PyTango.DevState.UNKNOWN)
            msg = 'Dev4Tango.PollingThreadIsDead!, last updated at %s'%time.ctime(getattr(self,'last_update',0))
            self.error(msg)
            self.set_status(msg)
        return self._state
    
    def dev_state(self):
        #@Tango7
        #This have been overriden to avoid device servers with states managed by qualities
        return self.get_state()
    
    def State(self):
        """ State redefinition is required to keep independency between 
        attribute configuration (max/min alarms) and the device State """
        #return self.get_state()
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
        
    ##@}
    
    ##@name Device management methods
    #@{
    
    def init_my_Logger(self):
        """ A default initialization for the Logger class """ 
        print 'In %s.init_my_Logger ...'%self.get_name()
        try:
            #First try to use Tango Streams
            if False: #hasattr(self,'error_stream'):
                self.error,self.warning,self.info,self.debug = self.error_stream,self.warn_stream,self.info_stream,self.debug_stream
            #Then Check if this class inherits from Logger
            elif isinstance(self,log.Logger): 
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
        return all([getattr(self,p,None) for p in props_list])        
    
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
                if not fun.isSequence(value):
                    value = [value]
                elif not isinstance(value,list):
                    value = list(value)
                if value==default:
                    missing_properties[k]=value
        if missing_properties:
            try:
                self.info('In Dev4Tango.get_device_properties(%s): initializing default property values: %s' % (self.get_name(),missing_properties))
                get_database().put_device_property(self.get_name(),missing_properties)
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
            if fun.isSequence(value) and not isinstance(value,list):
                value = list(value)
            self.db.put_device_property(self.get_name(),{key:isinstance(value,list) and value or [value]})                
    ##@}
    
    ##@name Advanced tools
    #@{
    def get_devs_in_server(self,MyClass=None):
        """
        Method for getting a dictionary with all the devices running in this server
        """
        MyClass = MyClass or self.get_device_class()
        if not hasattr(MyClass,'_devs_in_server'):
            MyClass._devs_in_server = tango.get_internal_devices()
        return MyClass._devs_in_server
                    
    def get_admin_device(self):
        U = PyTango.Util.instance()
        return U.get_dserver_device()
    
    def get_polled_attrs(self):
        """ 
        Returns a dictionary like {attr_name:period} 
        @TODO: Tango8 has its own get_polled_attr method; check for incompatibilities
        """
        return tango.get_polled_attrs(self)
            
    def set_polled_attribute(self,name,period,type_='attribute'):
        args = [[period],[self.get_name(),type_,name]]
        admin = self.get_admin_device()
        if name in self.get_polled_attrs(): 
            if period: admin.upd_obj_polling_period(args)
            else: admin.rem_obj_polling([self.get_name(),type_,name])
        else: admin.add_obj_polling(args)
            
    def set_polled_command(self,command,period):
        self.set_polled_attribute(command,period,type_='command')
        
    ##@}
    
    ##@name DevChild like methods
    #@{    
    
    def subscribe_external_attributes(self,device,attributes,use_tau=False):
        neighbours = self.get_devs_in_server()
        self.info('In subscribe_external_attributes(%s,%s): Devices in the same server are: %s'%(device,attributes,neighbours.keys()))
        if not hasattr(self,'ExternalAttributes'): self.ExternalAttributes = CaselessDict()
        if not hasattr(self,'PollingCycle'): self.PollingCycle = 3000
        if not hasattr(self,'last_event_received'): self.last_event_received = 0
        if not hasattr(self,'_state'): self._state = PyTango.DevState.INIT
        if not hasattr(self,'events_error'): self.events_error = ''
        if not hasattr(self,'last_update'): self.last_update = 0
        device = device.lower()
        deviceObj = neighbours.get(device,None)
        self.use_tau = getattr(self,'use_tau',TAU and use_tau)
        if self.use_tau and deviceObj is None:
            for attribute in attributes: #Done in two loops to ensure that all Cache objects are available
                self.info ('::init_device(%s): Configuring %s.Attribute for %s' % (self.get_name(),str(TAU.__name__),device+'/'+attribute))
                aname = (device+'/'+attribute).lower()
                at = TAU.Attribute(aname)
                self.debug('Adding Listener to %s ...'%type(at))
                at.addListener(self.event_received)
                self.debug('Changing polling period ...')
                at.changePollingPeriod(self.PollingCycle)
                self.ExternalAttributes[aname] = at
        else: #Managing attributes from internal devices
            self.info('===========> Subscribing attributes from an internal or non-tau device')
            for attribute in attributes:
                self.ExternalAttributes[(device+'/'+attribute).lower()] = fakeAttributeValue(attribute,None,parent=deviceObj,device=device)
            import threading
            if not hasattr(self,'Event'): self.Event = threading.Event()
            if not hasattr(self,'UpdateAttributesThread'):
                self.UpdateAttributesThread = threading.Thread(target=self.update_external_attributes)
                self.UpdateAttributesThread.setDaemon(True)
                self.UpdateAttributesThread.start()
            pass
        self.info('Registered attributes are: %s'%self.ExternalAttributes.keys())    
        
    def unsubscribe_external_attributes(self):
        try:
            if hasattr(self,'Event'):
                self.Event.set()
            if hasattr(self,'UpdateAttributesThread'):
                self.UpdateAttributesThread.join(getattr(self,'PollingCycle',3000.))            
            if getattr(self,'use_tau',False):
                from taurus import Attribute
                for at in self.ExternalAttributes.values():
                    if isinstance(at,Attribute):
                        at.removeListener(self.event_received)
        except Exception,e:
            self.error('Dev4Tango.unsubscribe_external_attributes() failed: %s'%e)
        return
        
    def write_external_attribute(self,device,attribute,data):
        self.info('===================> In write_external_attribute(%s,%s,%s)'%(device,attribute,str(data)[:40]))
        device,attribute = device.lower(),attribute.lower()
        deviceObj = self.get_devs_in_server().get(device,None)
        if deviceObj is None:
            if getattr(self,'use_tau',False):
                from taurus import Device
                Device(device).write_attribute(attribute,data)
            else:
                aname = str(device+'/'+attribute).lower()
                attr = self.ExternalAttributes[aname]
                if attr.parent is None: attr.parent = PyTango.DeviceProxy(device)
                attr.parent.write_attribute(attribute,data)
        else:
            if isinstance(deviceObj,DynamicDS): 
                method = 'write_dyn_attr'
                deviceObj.myClass.DynDev = deviceObj
            else: 
                method = 'write_%s'%attribute
            alloweds = [c for c in dir(deviceObj) if c.lower()=='is_%s_allowed'%attribute]
            is_allowed = not alloweds or getattr(deviceObj,alloweds[0])(PyTango.AttReqType.WRITE_REQ)            
            if is_allowed:
                aname = (device+'/'+attribute).lower()            
                attr = self.ExternalAttributes.get(aname,fakeAttributeValue(attribute))
                attr.set_write_value(data)
                methods = [c for c in dir(deviceObj) if c.lower()==method]
                if methods: 
                    method = getattr(deviceObj,methods[0])
                    #if isinstance(deviceObj,DynamicDS) and USE_STATIC_METHODS:
                    if isinstance(method,types.FunctionType): 
                        #method is staticmethod
                        method(deviceObj,attr)
                    else: method(attr)
                else: raise Exception('AttributeNotFound_%s!'%(device+'/'+attribute))
            else:
                raise Exception('WriteNotAllowed_%s!'%(device+'/'+attribute))
        
    def launch_external_command(self,device,target,argin=None):
        self.info('===================> In launch_external_command(%s,%s,%s)'%(device,target,argin))
        device,target = device.lower(),target.lower()
        deviceObj = self.get_devs_in_server().get(device,None)
        if deviceObj is None: 
            if getattr(self,'use_tau',False):
                from taurus import Device
                return Device(device).command_inout(target,argin)
            else:
                PyTango.DeviceProxy(device).command_inout(target,argin)
        else:
            alloweds = [c for c in dir(deviceObj) if c.lower()=='is_%s_allowed'%target]
            is_allowed = not alloweds or getattr(deviceObj,alloweds[0])() 
            if is_allowed:
                command = [c for c in dir(deviceObj) if c.lower()==target]
                if command: getattr(deviceObj,command[0])(argin)
                else: raise Exception('CommandNotFound_%s/%s!'%(device,target))
            else:
                raise Exception('CommandNotAllowed_%s!'%(device+'/'+target))
        
    def update_external_attributes(self):
        """ This thread replaces TauEvent generation in case that the attributes are read from a device within the same server. """
        while not self.Event.isSet():
            waittime = 3.
            try:
                serverAttributes = [a for a,v in self.ExternalAttributes.items() if isinstance(v,fakeAttributeValue)]
                waittime = 1e-3*self.PollingCycle/(len(serverAttributes)+1)
                for aname in serverAttributes:
                    self.last_update = time.time()
                    try:
                        if self.Event.isSet():
                            self.events_error = 'Thread finished by Event.set()'
                            break
                        attr = self.ExternalAttributes[aname]
                        device,attribute = aname.rsplit('/',1)
                        self.debug('====> updating values from %s(%s.%s) after %s s'%(type(attr.parent),device,attribute,waittime))
                        event_type = fakeEventType.lookup['Periodic']
                        try:
                            attr.read(cache=False)
                        except Exception,e:
                            print '#'*80
                            event_type = fakeEventType.lookup['Error']
                            self.events_error = except2str(e) #traceback.format_exc()
                            print self.events_error
                            
                        self.info('Sending fake event: %s/%s = %s(%s)' % (device,attr.name,event_type,attr.value))
                        self.event_received(device+'/'+attr.name,event_type,attr)
                    except: 
                        self.events_error = traceback.format_exc()
                        print 'Exception in %s.update_attributes(%s): \n%s' % (self.get_name(),attr.name,self.events_error)
                    self.Event.wait(waittime)
                    #End of for
                self.Event.wait(waittime)
            except:
                self.events_error = traceback.format_exc()
                self.Event.wait(3.)
                print self.events_error
                print 'Exception in %s.update_attributes()' % (self.get_name())
            #End of while
        self.info('%s.update_attributes finished')
        if not self.events_error.replace('None','').strip():
            self.events_error = traceback.format_exc()
        return         
                      
    def event_received(self,source,type_,attr_value):
        """
        This method manages the events received from external attributes.
        This method must be overriden in child classes.
        """
        #self.info,debug,error,warning should not be used here to avoid conflicts with taurus.core logging
        def log(prio,s): print '%s %s %s: %s' % (prio.upper(),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),self.get_name(),s)
        self.last_event_received = time.time()
        log('info','In Dev4Tango.event_received(%s(%s),%s,%s) at %s'%(type(source).__name__,source,fakeEventType[type_],type(attr_value).__name__,self.last_event_received))
        return
        
    ##@}        
        
##############################################################################################################
## DevChild ... DEPRECATED and replaced by Dev4Tango + TAU

class DevChild(Dev4Tango):
    pass

