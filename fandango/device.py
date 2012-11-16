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

#python imports
import os,threading,traceback

#pytango imports
import PyTango

#fandango imports
from fandango import log,excepts,callbacks,tango,objects,dicts,arrays,dynamic
from fandango import functional as fun
from log import Logger,except2str,printf
from excepts import *
from callbacks import *
import fandango.tango as tango
from tango import * #USE_TAU imported here, get_polled_attrs and other useful methods
from objects import Object,Struct
from dicts import CaselessDefaultDict,CaselessDict
from arrays import TimedQueue
from dynamic import DynamicDS,USE_STATIC_METHODS


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
                if not isinstance(value,list): value = [value]
                if value==default:
                    missing_properties[k]=value
        if missing_properties:
            try:
                self.info('In Dev4Tango.get_device_properties(%s): initializing default property values: %s' % (self.get_name(),missing_properties))
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
    
    ##@name Advanced tools
    #@{
    def get_devs_in_server(self,MyClass=None):
        """
        Method for getting a dictionary with all the devices running in this server
        """
        MyClass = MyClass or self.get_device_class()
        if not hasattr(MyClass,'_devs_in_server'):
            MyClass._devs_in_server = {} #This dict will keep an access to the class objects instantiated in this Tango server
        if not MyClass._devs_in_server:
            U = PyTango.Util.instance()
            for klass in U.get_class_list():
                print 'Getting devices from %s' % str(klass)
                for dev in U.get_device_list_by_class(klass.get_name()):
                    #if isinstance(dev,DynamicDS):
                    print '\tAdding device %s'%dev.get_name()
                    MyClass._devs_in_server[dev.get_name().lower()]=dev
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
            if period: admin.UpdObjPollingPeriod(args)
            else: admin.RemObjPolling([self.get_name(),type_,name])
        else: admin.AddObjPolling(args)
            
    def set_polled_command(self,command,period):
        self.set_polled_attribute(command,period,type_='command')
        
    ##@}
    
    ##@name DevChild like methods
    #@{    
    
    def subscribe_external_attributes(self,device,attributes):
        neighbours = self.get_devs_in_server()
        self.info('In subscribe_external_attributes(%s,%s): Devices in the same server are: %s'%(device,attributes,neighbours.keys()))
        if not hasattr(self,'ExternalAttributes'): self.ExternalAttributes = CaselessDict()
        if not hasattr(self,'PollingCycle'): self.PollingCycle = 3000
        if not hasattr(self,'last_event_received'): self.last_event_received = 0
        if not hasattr(self,'_state'): self._state = PyTango.DevState.INIT
        device = device.lower()
        deviceObj = neighbours.get(device,None)
        if USE_TAU and deviceObj is None:
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
            if USE_TAU: 
                from taurus import Attribute
                for at in self.ExternalAttributes.values():
                    if isinstance(at,Attribute):
                        at.removeListener(self.event_received)
        except Exception,e:
            self.error('Dev4Tango.unsubscribe_external_attributes() failed: %s'%e)
        return
        
    def write_external_attribute(self,device,attribute,data):
        self.info('===================> In write_external_attribute(%s,%s)'%(device,attribute))
        device,attribute = device.lower(),attribute.lower()
        deviceObj = self.get_devs_in_server().get(device,None)
        if deviceObj is None:
            if USE_TAU: 
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
                    if isinstance(deviceObj,DynamicDS): getattr(deviceObj,methods[0])(deviceObj,attr)
                    else: getattr(deviceObj,methods[0])(attr)
                else: raise Exception('AttributeNotFound_%s!'%(device+'/'+attribute))
            else:
                raise Exception('WriteNotAllowed_%s!'%(device+'/'+attribute))
        
    def launch_external_command(self,device,target,argin=None):
        self.info('===================> In launch_external_command(%s,%s,%s)'%(device,target,argin))
        device,target = device.lower(),target.lower()
        deviceObj = self.get_devs_in_server().get(device,None)
        if deviceObj is None: 
            if USE_TAU:
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
            serverAttributes = [a for a,v in self.ExternalAttributes.items() if isinstance(v,fakeAttributeValue)]
            for aname in serverAttributes:
                if self.Event.isSet(): break
                attr = self.ExternalAttributes[aname]
                device,attribute = aname.rsplit('/',1)
                self.debug('====> updating values from %s(%s.%s)'%(type(attr.parent),device,attribute))
                event_type = fakeEventType.lookup['Periodic']
                try:
                    if attr.parent is None: attr.parent = PyTango.DeviceProxy(device)
                    if attr.name.lower()=='state': 
                        if isinstance(attr.parent,PyTango.DeviceProxy): attr.set_value(attr.parent.state())
                        elif hasattr(attr.parent,'last_state'): attr.set_value(attr.parent.last_state)
                        else: attr.set_value(attr.parent.get_state())
                    else: 
                        if isinstance(attr.parent,PyTango.DeviceProxy):
                            self.info('Dev4Tango.update_external_attributes(): calling DeviceProxy(%s).read_attribute(%s)'%(attr.device,attr.name))
                            is_allowed = True
                            #val = lambda obj,val: setattr(val,'value',obj.read_attribute(val.name))
                            #method(attr.parent,attr)
                            val = attr.parent.read_attribute(attr.name)
                            attr.set_value_date_quality(val.value,val.date,val.quality)
                        else:
                            f = [s for s in dir(attr.parent) if s.lower()=='is_%s_allowed'%attr.name.lower()]
                            if not f: is_allowed = True
                            else:
                                self.info('Dev4Tango.update_external_attributes(): calling %s.is_%s_allowed()'%(attr.device,attr.name))
                                is_allowed = getattr(attr.parent,f[0])(PyTango.AttReqType.READ_REQ)
                            if is_allowed:
                                methods = [c for c in dir(attr.parent) if c.lower()=='read_%s'%attr.name.lower()]
                                if not methods: 
                                    if isinstance(attr.parent,DynamicDS): 
                                        self.info('Dev4Tango.update_external_attributes(): calling %s(%s).read_dyn_attr(%s)'%(attr.parent.myClass,attr.device,attr.name))
                                        if attr.parent.myClass:
                                            attr.parent.myClass.DynDev = attr.parent
                                            if USE_STATIC_METHODS: attr.parent.read_dyn_attr(attr.parent,attr)
                                            else: attr.parent.read_dyn_attr(attr)
                                        else: self.warning('\t%s is a dynamic device not initialized yet.'%attr.device)
                                    else:
                                        self.error('%s.read_%s method not found!!!\n%s'%(device,attr.name,[d for d in dir(attr.parent) if not a.startswith('_')]))
                                else: 
                                    self.info('Dev4Tango.update_external_attributes(): calling %s.read_%s()'%(attr.device,attr.name))
                                    getattr(attr.parent,methods[0])(attr)
                            else:
                                self.info('%s.read_%s method is not allowed!!!'%(device,attr.name))
                                event_type = fakeEventType.lookup['Error']
                            
                    self.info('Sending fake event: %s/%s = %s(%s)' % (device,attr.name,event_type,attr.value))
                    self.event_received(device+'/'+attr.name,event_type,attr)
                except: 
                    print 'Exception in %s.update_attributes(%s): \n%s' % (self.get_name(),attr.name,traceback.format_exc())                
                
                self.Event.wait(1e-3*(self.PollingCycle/len(serverAttributes)))                    
                #End of for
            #End of while
        self.info('%s.update_attributes finished')
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
## Tango formula evaluation
import dicts

class TangoEval(object):
    """ 
    Class for Tango formula evaluation
    Class with methods copied from PyAlarm 
    All tango-like variables are parsed.
    Any variable in _locals is evaluated or explicitly replaced in the formula if matches $(); e.g. FIND($(VARNAME)/*/*)
    """
    def __init__(self,formula='',launch=True,timeout=1000,trace=False, proxies=None, attributes=None, cache=0):
        self.formula = formula
        self.variables = []
        self.timeout = timeout
        self.proxies = proxies or dicts.defaultdict_fromkey(taurus.Device) if USE_TAU else ProxiesDict()
        self.attributes = attributes or dicts.defaultdict_fromkey(taurus.Attribute if USE_TAU else PyTango.AttributeProxy)
        self.previous = dicts.CaselessDict() #Keeps last values for each variable
        self.last = dicts.CaselessDict() #Keeps values from the last eval execution only
        self.cache_depth = cache
        self.cache = dicts.CaselessDefaultDict(lambda k:list()) if self.cache_depth else None#Keeps [cache]
        self.result = None
        self._trace = trace
        self._defaults = dict([(str(v),v) for v in PyTango.DevState.values.values()]+[(str(q),q) for q in PyTango.AttrQuality.values.values()])
        self._defaults['str2epoch'] = lambda *args: time.mktime(time.strptime(*args))
        self._defaults['time'] = time
        self._locals = dict(self._defaults) #Having 2 dictionaries to reload defaults when needed
        
        if self.formula and launch: 
            self.eval()
            if not self._trace: 
                print 'TangoEval: result = %s' % self.result
        return
            
    def trace(self,msg):
        if self._trace: print 'TangoEval: %s'%str(msg)
        
    def set_timeout(self,timeout):
        self.timeout = int(timeout)
        self.trace('timeout: %s'%timeout)
        
    def parse_formula(self,formula,_locals=None):
        """ This method just removes comments and expands FIND() searches in the formula; no tango check, no value replacement """
        _locals = _locals or {}
        _locals.update(self._locals)
        if '#' in formula:
            formula = formula.split('#',1)[0]
        if ':' in formula and not re.match('^',redev):
            tag,formula = formula.split(':',1)            
        if _locals and '$(' in formula: #explicit replacement of env variables if $() used
            for l,v in _locals.items():
                formula = formula.replace('$(%s)'%str(l),str(v))
        findables = re.findall('FIND\(([^)]*)\)',formula)
        for target in findables:
            res = str(sorted(d.lower() for d in get_matching_attributes([target.replace('"','').replace("'",'')])))
            formula = formula.replace("FIND(%s)"%target,res.replace('"','').replace("'",''))
            self.trace('Replacing with results for %s ...%s'%(target,res))
        return formula
        
    def parse_variables(self,formula,_locals=None):
        ''' This method parses attributes declarated in formulas with the following formats:
        TAG1: dom/fam/memb/attrib >= V1 #A comment
        TAG2: d/f/m/a1 > V2 and d/f/m/a2 == V3
        TAG3: d/f/m.quality != QALARM #Another comment
        TAG4: d/f/m/State ##A description?, Why not
        :return: 
            - a None value if the alarm is not parsable
            - a list of (device,attribute,value/time/quality) tuples
        '''            
        #operators = '[><=][=>]?|and|or|in|not in|not'
        #l_split = re.split(operators,formula)#.replace(' ',''))
        alnum = '[a-zA-Z0-9-_]+'
        no_alnum = '[^a-zA-Z0-9-_]'
        no_quotes = '(?:^|$|[^\'"a-zA-Z0-9_\./])'
        #redev = '(?:^|[^/a-zA-Z0-9_])(?P<device>(?:'+alnum+':[0-9]+/)?(?:'+'/'.join([alnum]*3)+'))' #It matches a device name
        redev = '(?P<device>(?:'+alnum+':[0-9]+/{1,2})?(?:'+'/'.join([alnum]*3)+'))' #It matches a device name
        reattr = '(?:/(?P<attribute>'+alnum+')(?:(?:\\.)(?P<what>quality|time|value|exception|delta|all))?)?' #Matches attribute and extension
        retango = redev+reattr#+'(?!/)'
        regexp = no_quotes + retango + no_quotes.replace('\.','') #Excludes attr_names between quotes, accepts value type methods
        #self.trace( regexp)
        idev,iattr,ival = 0,1,2 #indexes of the expression matching device,attribute and value
        
        formula = self.parse_formula(formula,_locals)
        
        ##@var all_vars list of tuples with (device,/attribute) name matches
        #self.variables = [(s[idev],s[iattr],s[ival] or 'value') for s in re.findall(regexp,formula) if s[idev]]
        variables = [s for s in re.findall(regexp,formula)]
        self.trace('parse_variables(%s): %s'%(formula,variables))
        return variables
        
    def get_vtime(self,value):
        #Gets epoch for a Tango value
        return getattr(value.time,'tv_sec',value.time)
        
    def read_attribute(self,device,attribute,what='value',_raise=True, timeout=None):
        """
        Executes a read_attribute and returns the value requested
        :param _raise: if attribute is empty or 'State' exceptions will be rethrown
        """
        self.trace('read_attribute(%s/%s.%s)'%(device,attribute,what))
        timeout = timeout or self.timeout
        aname = (device+'/'+attribute).lower()
        try:
            if aname not in self.attributes:
                dp = self.proxies[device]
                try: dp.set_timeout_millis(timeout)
                except: self.trace('unable to set %s proxy timeout to %s ms: %s'%(device,timeout,except2str()))
                dp.ping()
                # Disabled because we want DevFailed to be triggered
                #attr_list = [a.name.lower()  for a in dp.attribute_list_query()]
                #if attribute.lower() not in attr_list: #raise Exception,'TangoEval_AttributeDoesntExist_%s'%attribute
            value = self.attributes[aname].read()
            if self.cache_depth and not any(self.get_vtime(v)==self.get_vtime(value) for v in self.cache[aname]):
                while len(self.cache[aname])>=self.cache_depth: self.cache[aname].pop(-1)
                self.cache[aname].insert(0,value)
            if what == 'all': pass
            elif what == 'time': value = self.get_vtime(value)
            elif what == 'exception': value = False
            else: value = getattr(value,what)
            self.trace('Read %s.%s = %s' % (aname,what,value))
        except Exception,e:
            if isinstance(e,PyTango.DevFailed) and what=='exception':
                return True
            elif _raise:
                raise e
            self.trace('TangoEval: ERROR(%s)! Unable to get %s for attribute %s/%s: %s' % (type(e),what,device,attribute,e))
            #print traceback.format_exc()
            value = None
        return value
                
    def update_locals(self,dct=None):
        if dct:
            if not hasattr(dct,'keys'): dct = dict(dct)
            self._locals.update(dct)
            self.trace('update_locals(%s)'%dct.keys())
        self._locals['now'] = time.time()
        return self._locals
            
    def parse_tag(self,target,wildcard='_'):
        return target.replace('/',wildcard).replace('-',wildcard).replace('.',wildcard).replace(':',wildcard).replace('_',wildcard).lower()
    
    def eval(self,formula=None,previous=None,_locals=None ,_raise=False):
        ''' 
        Evaluates the given formula.
        Previous can be used to add extra local values, or predefined values for attributes ({'a/b/c/d':1} that would override its reading
        Any variable in locals is evaluated or explicitly replaced in the formula if appearing with brackets (e.g. FIND({VARNAME}/*/*))
        :param _raise: if attribute is empty or 'State' exceptions will be rethrown
        '''
        self.formula = (formula or self.formula).strip()
        previous = previous or {}
        _locals = _locals or {}
        for x in ['or','and','not','in','is','now']: #Check for case-dependent operators
            self.formula = self.formula.replace(' '+x.upper()+' ',' '+x+' ')
        self.formula = self.formula.replace(' || ',' or ')
        self.formula = self.formula.replace(' && ',' and ')
        self.update_locals(_locals)
        #self.previous.update(previous or {}) #<<< Values passed as eval locals are persistent, do we really want that?!?
        
        self.formula = self.parse_formula(self.formula) #Replacement of FIND(...), env variables and comments.
        variables = self.parse_variables(self.formula)
        self.trace('>'*80)
        self.trace('eval(): variables in formula are %s' % variables)
        source = self.formula #It will be modified on each iteration
        targets = [(device + (attribute and '/%s'%attribute) + (what and '.%s'%what),device,attribute,what) for device,attribute,what in variables]
        self.last.clear()
        #self.last.update(dict((v[0],'') for v in targets))
        ## NOTE!: It is very important to keep the same order in which expressions were extracted
        for target,device,attribute,what in targets: 
            var_name = self.parse_tag(target)
            self.trace('\t%s => %s'%(target,var_name))
            try:
                #Reading or Overriding attribute value, if overriden value will not be kept for future iterations
                self.previous[var_name] = previous.get(target,
                    self.read_attribute(device,
                        attribute or 'State',
                        what if what and what!='delta' else 'value',
                        _raise=_raise if not any(d==device and a==attribute and w=='exception' for t,d,a,w in targets) else False
                        ))
                if what=='delta':
                    cache = self.cache.get((device+'/'+attribute).lower())
                    self.previous[var_name] = 0 if (not self.cache_depth or not cache) else (cache[0].value-cache[-1].value)
                self.previous.pop(target,None)
                source = source.replace(target,var_name,1) #Every occurrence of the attribute is managed separately, read_attribute already uses caches within polling intervals
                self.last[target] = self.previous[var_name] #Used from alarm messages
            except Exception,e:
                self.last[target] = e
                raise e
        self.trace('formula = %s' % (source))
        self.trace('previous.items():\n'+'\n'.join(str((str(k),str(i))) for k,i in self.previous.items()))
        self.trace('locals.items():\n'+'\n'.join(str((str(k),str(i))) for k,i in self._locals.items() if k not in self._defaults))
        self.result = eval(source,dict(self.previous),self._locals)
        self.trace('result = %s' % self.result)
        return self.result
    pass
        
##############################################################################################################
## Tango Command executions

class TangoCommand(object):
    """
    This class encapsulates a call to a Tango Command, it manages asynchronous commands in a background thread or process.
    It also allows to setup a "feedback" condition to validate that the command has been executed.
    
    The usage would be like::
    
      tc = TangoCommand('move',DeviceProxy('just/a/motor'),asynch=True,process=False)
      
      #In this example the value of the command will be returned once the state will change
      result = tc(args,feedback='state',expected=PyTango.DevState.MOVING,timeout=10000)
      
      #In this other example, it will be the value of the state what will be returned
      result = tc(args,feedback='state',timeout=10000)
      
    :param command: the name of a tango command; or a callable
    :param device: a device that can be an string, a DeviceProxy or a TaurusDevice
    :param timeout: when using asynchronous commands default timeout can be overriden
    :param feedback: attribute, command or callable to be executed
    :param expected: if not None, value that feedback must have to consider the command successful
    :param wait: time to wait for feedback (once command has been executed)
    :param asynch: to perform the wait in a different thread instead of blocking
    :param process: whether to use a different process to execute the command (if CPU intensive or trhead-blocking)
    :
    """
    
    class CommandException(Exception): pass
    class CommandTimeout(Exception): pass
    class BadResult(Exception): pass
    class BadFeedback(Exception): pass
    Proxies = ProxiesDict()
    
    def __init__(self,command,device=None,timeout=None,feedback=None,expected=None,wait=3.,asynch=True,process=False):
        
        self.device = device
        self.proxy = TangoCommand.Proxies[self.device]
        if isinstance(command,basestring):
            if '/' in command:
                d,self.command = command.rsplit('/',1)
                if not self.device: self.device = d
            else: self.command = command
            self.info = self.proxy.command_query(self.command)
        else: #May be a callable
            self.command,self.info = command,None
            
        self.timeout = timeout or 3.
        self.feedback = feedback and self._parse_feedback(feedback)
        self.expected = expected
        self.wait = wait
        self.asynch = asynch
        self.process = process
        
        self.event = threading.Event()
        if process:
            import fandango.threads
            self.process = fandango.threads.WorkerThread(device+'/'+command,process=True)
        else:
            self.process = None
        pass
        
    def trace(self,msg,severity='DEBUG'):
        print '%s %s fandango.TangoCommand: %s'%(severity,time.ctime(),msg)
    
    def _parse_feedback(self,feedback):
        if fun.isCallable(feedback):
            self.feedback = feedback
        elif isinstance(feedback,basestring):
            if '/' in feedback:
                device,target = feedback.rsplit('/',1) if feedback.count('/')>=(4 if ':' in feedback else 3) else (feedback,state)
            else:
                device,target = self.device,feedback
            proxy = TangoCommand.Proxies[device]
            attrs,comms = proxy.get_attribute_list(),[cmd.cmd_name for cmd in proxy.command_list_query()]
            if fun.inCl(target,comms):
                self.feedback = (lambda d=device,c=target: TangoCommand.Proxies[d].command_inout(c))
            elif fun.inCl(target,attrs):
                self.feedback = (lambda d=device,a=target: TangoCommand.Proxies[d].read_attribute(a).value)
            else:
                raise TangoCommand.CommandException('UnknownFeedbackMethod_%s'%feedback)
        return self.feedback

    def __call__(self,*args,**kwargs):
        self.execute(*args,**kwargs)
    
    def execute(self,args=None,timeout=None,feedback=None,expected=None,wait=None,asynch=None):
        self.trace('%s/%s(%s)'%(self.device,self.command,args or ''))
        #args = (args or []) #Not convinient
        timeout = fun.notNone(timeout,self.timeout)
        if feedback is not None:
            feedback = self._parse_feedback(feedback)
        else:
            feedback = self.feedback
        expected = fun.notNone(expected,self.expected)
        wait = fun.notNone(wait,self.wait)
        asynch = fun.notNone(asynch,self.asynch)
        t0 = time.time()
        result = None
        
        if fun.isString(self.command):
            if not asynch:
                if args: result = self.proxy.command_inout(self.command,args)
                else: result = self.proxy.command_inout(self.command)
            else:
                self.trace('Using asynchronous commands')
                if args: cid = self.proxy.command_inout_asynch(self.command,args)
                else: cid = self.proxy.command_inout_asynch(self.command)
                while timeout > (time.time()-t0):
                    self.event.wait(.025)
                    try: 
                        result = self.proxy.command_inout_reply(cid)
                        break
                    except PyTango.DevFailed,e:
                        if 'AsynReplyNotArrived' in str(e): 
                            pass
                        #elif any(q in str(e) for q in ('DeviceTimedOut','BadAsynPollId')):
                        else:
                            #BadAsynPollId is received once the command is discarded
                            raise TangoCommand.CommandException(str(e).replace('\n','')[:100])
        elif fun.isCallable(self.command):
            result = self.command(args)
            
        t1 = time.time()
        if t1 > (t0+self.timeout): 
            raise TangoCommand.CommandTimeout(str(self.timeout*1000)+' ms')
        if feedback is not None:
            self.trace('Using feedback: %s'%feedback)
            tt,tw = min((timeout,(t1-t0+wait))),max((0.025,wait/10.))
            now,got = t1,None
            while True:
                self.event.wait(tw)
                now = time.time()
                got = type(expected)(feedback())
                if not wait or expected is None or got==expected:
                    self.trace('Feedback (%s) obtained after %s s'%(got,time.time()-t0))
                    break
                if now > (t0+timeout):
                    raise TangoCommand.CommandTimeout(str(self.timeout*1000)+' ms')
                if now > (t1+wait):
                    break
            if expected is None:
                return got
            elif got==expected:
                self.trace('Result (%s,%s==%s) verified after %s s'%(result,got,expected,time.time()-t0))
                return (result if result is not None else got)
            else:
                raise TangoCommand.BadFeedback('%s!=%s'%(got,expected))
        elif expected is None or result == expected:
            self.trace('Result obtained after %s s'%(time.time()-t0))
            return result
        else:
            raise TangoCommand.BadResult(str(result))
        if self.timeout < time.time()-t0: 
            raise TangoCommand.CommandTimeout(str(self.timeout*1000)+' ms')
        return result
    
   
##############################################################################################################
## DevChild ... DEPRECATED and replaced by Dev4Tango + TAU

class DevChild(Dev4Tango):
    pass
    #"""
    #Inherit from this class, it provides EventManagement, Dev4Tango, log.Logger, objects.Object and more ...
    #To take profit of event management, the Child Class should redeclare its own PushEvent method!!!
    
    #ADD THIS LINE TO YOUR always_executed_hook METHOD:
        #DevChild.always_executed_hook(self)
    #"""
    #def init_DevChild(self, ParentName=None, ParentAttributes=None, EventHook=None,Wait=15, ForcePolling=False, MAX_ERRORS=10):
        #""" Initialize your eventReceiver device:
            #ParentName: device from which attributes are read
            #ParentAttributes: list of attributes to keep updated
            #EventHook: method to be called for each event; is not being used, push_event is called by default and must be redefined
            #Wait: time between DeviceProxy.ping() executions    
            #ForcePolling: forces polling in all attributes listed, it can be directly the period to force
        #call this method once the properties self.ParentName and self.ParentAttributes has been verified """
        #if not self.check_Properties(['ParentName','ParentAttributes']) and all([ParentName,ParentAttributes]):
            #self.ParentName=ParentName
            #self.ParentAttributes=ParentAttributes
        #print "In %s.init_DevChild(%s,%s) ..." % (self.get_name(),self.ParentName,self.ParentAttributes)            
        
        #EventReceivers[self.get_name()]=self
        ##The eventHook is not being used, push_event is called by default and must be redefined
        ##self.EventHook=EventHook
        
        #self.dp=None
        #self.dp_event=threading.Event()
        #self.dp_stopEvent=threading.Event()
        #self.dp_lock=threading.Lock()
        #self.stop_threads=False
        #self.dp_wait=Wait
        #self.dp_force_polling=ForcePolling
        #self.ParentPolledAttributes=[]
        ##Add this line to always_executed_hook: if hasattr(self,'ForceParentPolling') and self.ForceParentPolling and not self.ParentPolledAttributes: self.force_ParentAttributes_polling()
        #self.MAX_ERRORS=MAX_ERRORS
        #self.dp_errors = 0
        
        #self.lastcomm=''
        #self.lasttime=0. #Time of last communication
        
        #self.last_updates={} #This dictionary records the last time() when each attribute was read
        #self.last_retries={} #This dictionary records the last retry (succeded or failed)
        #self.MIN_PERIOD=3.0 #This is the min period between read_attribute executions
        
        #self.check_dp_thread=threading.Thread(None,self.check_ParentProxy,'check_dp')
        #self.check_dp_thread.setDaemon(True)
        
    #def delete_device(self):
        #print "[Device delete_device method] for DevChild"
        #self.dp_stopEvent.set()
        #self.dp_event.set() #Wake up threads
        #del self.dp
        
    #class forcedAttributeValue(object):
        #""" This class simulates a modifiable AttributeValue object (not available in PyTango)"""
        #def __init__(self,name,value,time_=0.,quality=PyTango.AttrQuality.ATTR_VALID,dim_x=1,dim_y=1):
            #self.name=name
            #self.value=value
            #self.time=time_ or time.time()
            #self.quality=quality
            #self.dim_x=dim_x
            #self.dim_y=dim_y
                    
    #def always_executed_hook(self):
        #self.info('In DevChild.always_executed_hook()')
        #if self.get_state()!=PyTango.DevState.UNKNOWN and hasattr(self,'ForceParentPolling') and self.ForceParentPolling and not self.ParentPolledAttributes:
            #self.force_ParentAttributes_polling()
        #if not self.check_dp_thread.isAlive():
            #self.info('In DevChild.always_executed_hook(): CheckProxy thread is not Alive!')
            #self.check_dp_thread.start()
        
    #def comms_report(self):        
        #return     '\n'.join([','.join(self.ParentAttributes)+' Attributes acquired from '+self.ParentName+' Device. ',
                #'Last communication was "'+self.lastcomm+'" at '+time.ctime(self.lasttime)+'.'])
    
    #def check_ParentProxy(self):
        #''' This method performs the parent's device proxy checking
        #It changes the state to Unknown if there's no connection to the device
        #The state is set to INIT when the connection is restablished
        #stop_threads and dp_event help to control the deletion of the thread
        #'''
        ##signal.signal(signal.SIGTRAP,self.delete_device)
        ##signal.signal(signal.SIGABRT,self.delete_device)
        ##signal.signal(signal.SIGKILL,self.delete_device)
        #while not self.dp_stopEvent.isSet():
            ##print '*'*20 + 'in check_ParentProxy, ...'+'*'*20
            #self.info('*'*20 + 'in check_ParentProxy, ...'+'*'*20 )
            ##The dp_event.wait(60) is done at the end of the loop
            #try:
                #self.dp_lock.acquire(False)
                #if self.get_state()==PyTango.DevState.UNKNOWN: #If the device is not connected to parent, then connection is restarted and attributes subscribed
                    #self.warning('in check_ParentProxy, self.DevState is UNKNOWN')
                    #try:
                        #if not TangoDatabase.get_device_exported(self.ParentName):
                            #raise Exception,'%s device is not exported!'%self.ParentName
                        #self.dp = PyTango.DeviceProxy(self.ParentName)
                        #self.Parent = self.dp #Parent is an Alias for the device proxy
                        #self.dp.set_timeout_millis(1000)
                        #self.dp.ping()
                        #self.set_state(PyTango.DevState.INIT)                        
                        #self.check_dp_attributes()
                        #self.dp_errors=0
                        #self.lasttime=time.time()                    
                        #self.info("In check_ParentProxy(): proxy to %s device initialized."%self.ParentName)
                    #except Exception,e:
                        #self.error('EXCEPTION in check_ParentProxy():, %s Proxy Initialization failed! %s'%(self.ParentName,getLastException()))
                        #self.set_state(PyTango.DevState.UNKNOWN)                    
                        #self.dp_errors+=1

                #else: #If the device was already connected, timestamp for attributes is verified
                    #try:
                        #self.dp.ping()
                        #self.check_dp_attributes_epoch()
                    #except Exception,e:
                        #self.error('EXCEPTION in check_ParentProxy(), Ping to device %s failed!: %s'%(self.ParentName,getLastException()))
                        #self.set_state(PyTango.DevState.UNKNOWN)
                        #self.dp_errors+=1
                        ##del self.dp; self.dp=None
                #self.info('*'*20 + 'in check_ParentProxy, end of loop'+'*'*20 )                        
            #except Exception,e:
                #self.error('Something failed in check_ParentProxy()!: %s'%traceback.format_exc)
            #finally:
                #self.dp_lock.release()
                #self.dp_event.wait(self.dp_wait)
        #self.info('*'*20 + 'check_ParentProxy, THREAD EXIT!'+'*'*20 )                        
        ##if self.dp: del self.dp
        
    #def getParentProxy(self):
        #return self.Parent
        
    #def check_dp_attributes(self):
        #""" This method subscribes to the attributes of the Parent device, it is executed only at reconnecting. """
        #self.info("In check_dp_attributes(%s)"%self.ParentAttributes)
        #attrs = self.dp.get_attribute_list()
        #for att in [pa.lower() for pa in self.ParentAttributes]:
            #if att not in [a.lower() for a in attrs]:
                #self.info("In check_dp_attributes(): "+self.ParentName+" doesn't have "+att+" attribute!")
                #raise Exception('MissingParentAttribute_%s'%att)
            #elif att not in self.last_updates.keys():
                #self.last_updates[att]=0
                
        ##Configure the attribute polling
            #if not self.dp.is_attribute_polled(att) and self.dp_force_polling:
                ### OJO! Absolute and relative changes should be set previously!!!!
                #print '*'*80
                #print self.get_name(),'.check_dp_attributes(): forcing ',att,' polling to ',argin
                #print '*'*80
                #period = self.dp.get_attribute_poll_period(att) or (int(self.dp_force_polling)>1000 or 3000)
                #self.dp.poll_attribute(att,period)
                #print self.get_name(),".poll_attribute(",att_name,",",period,")"
            #try:
                #if self.dp.is_attribute_polled(att):
                    ##
                    ## CONFIGURING EVENTS
                    ##
                    #att_name = att.lower() if len(att.split('/'))>2 else ('/'.join([self.ParentName,att])).lower()
                    #self.debug('In check_dp_attributes(...): checking %s' % att_name)
                    #if not callbacks.inEventsList(att_name):
                        #self.info('In check_dp_attributes: subscribing event for %s'%att_name)
                        #if 'CHANGE_EVENT' not in dir(PyTango.EventType): PyTango.EventType.CHANGE_EVENT = PyTango.EventType.CHANGE
                        #event_id = self.dp.subscribe_event(att,PyTango.EventType.CHANGE_EVENT,GlobalCallback,[],True) #This last argument subscribe to not-running devices
                        #tattr = TAttr(att_name,dev_name=self.ParentName.lower(),proxy=self.dp,event_id=event_id)
                        #callbacks.addTAttr(tattr)
                        #self.info("In check_dp_attributes()\n Listing Device/Attributes in EventsList:")
                        #for a,t in callbacks.getEventItems(): self.info("\tAttribute: %s\tDevice: %s"%(a,t.dev_name))
                    #callbacks.addReceiver(att_name,self.get_name()) #This method checks if receiver was already in the list of not
                #else:
                    #self.info('In check_dp_attributes: attribute %s is not polled and will be not managed by callbacks, use check_dp_attributes_epoch instead'%att)
                    ##
                    ## HERE POLLING SHOULD BE CONFIGURED
                    ##
                    #pass
            #except Exception,e:
                #self.error('Something failed in check_dp_attributes()!: %s'%traceback.format_exc())
                #raise e
        #self.info("Out of check_dp_attributes ...")
            
    #def getParentState(self,dev_name=None):
        #dev_name = dev_name or self.ParentName
        #dState=callbacks.getStateFor(dev_name)
        #if dState is not None:
            #self.info('In DevChild(%s).getParentState(%s)=%s ... parent state read from callbacks'%(self.get_name(),dev_name,str(dState)))
        #else:
            #try:
                #attvalue=self.force_Attribute_reading('state')
                #dState=attvalue.value
                #self.info('In DevChild(%s).getParentState(%s)=%s, forced reading'%(self.get_name(),dev_name,str(dState)))
            #except Exception,e:
                #print 'In DevChild(%s).getParentState(%s) ... UNABLE TO READ PARENT STATE! (%s)'%(self.get_name(),dev_name,str(excepts.getLastException()))
                #self.set_state(PyTango.DevState.UNKNOWN)
        #return dState
    
    #def force_Attribute_reading(self,att):
        #now=time.time()
        #attvalue=None
        #last_update=self.getLastAttributeUpdate(att)
        #self.info('In force_Attribute_reading(%s): last update at %s, %s s ago.'%(att,time.ctime(last_update),str(now-last_update)))
        #try:
            #if att in self.last_retries.keys() and self.MIN_PERIOD>(self.last_retries[att]):
                #self.info('DevChild.force_Attribute_reading at %s: read_attribute retry not allowed in < 3 seconds'%(time.ctime(now)))
            #else:
                ##These variables should be recorded first, if it isn't an exception will ignore it!
                ##Last update is recorded even if reading is not possible, to avoid consecutive retries
                #self.last_retries[att]=now
                #self.lasttime=now
                #self.dp.ping()
                #attvalue=self.dp.read_attribute(att)
                #if attvalue: 
                    #self.lastcomm='DeviceProxy.read_attribute(%s,%s)'%(att,str(attvalue.value))            
                    #self.info('Parent.%s was succesfully read: %s'%(att,str(attvalue.value)))
                    #if att=='state':
                        #callbacks.setStateFor(self.ParentName,attvalue.value)
                    #else:
                        #callbacks.setAttributeValue(self.ParentName.lower()+'/'+att.lower(),attvalue)
                #self.setLastAttributeUpdate(att,self.getAttributeTime(attvalue))
                #return attvalue
        #except PyTango.DevFailed,e:
            #print 'PyTango.Exception at force_Attribute_reading: ',str(getLastException())
            #err = e.args[0]
            #PyTango.Except.throw_exception(str(err.reason),str(err.desc),str(err.origin))
        #except Exception,e:
            #print 'Exception at force_Attribute_reading: ',str(getLastException())
            #PyTango.Except.throw_exception('DevChild_force_Attribute_readingException',str(e),'DevChild.force_Attribute_reading')
        #pass
            
    #class forcedEvent(object):
        #def __init__(self,device,attr_name,attr_value,err,errors):
            #self.device=device
            #self.attr_name=attr_name
            #self.attr_value=attr_value
            #self.err=err
            #self.errors=errors
            
    #def check_dp_attributes_epoch(self):
        #""" This method is executed periodically once the Parent device have been connected. """
        #self.info('In check_dp_attributes_epoch(%s)' % self.last_updates.keys())
        #now = time.time()
        #for k,v in self.last_updates.items():
            #self.debug('-> Last update of %s attribute was at %s'%(k,time.ctime(v)))
            #if v < now-self.dp_wait: #If the last_update of the attribute is too old, it forces an error event
                #self.info('='*10+'> FORCING EVENT FOR ATTRIBUTE %s, after %s seconds delay'%(k,str(v-now)))
                #try:
                    #GlobalCallback.lock.acquire()
                    ##This is a recursive call, the push_event will schedule a future forceAttributeReading
                    #event = self.forcedEvent(self.ParentName,self.ParentName+'/'+k,None,True,[
                        #{'reason':'DevChild_PushEventForced','desc':'Attribute not updated in the last %s seconds'%self.dp_wait,'origin':'DevChild.check_dp_attributes_epoch'}])
                    #self.push_event(event)
                #except Exception,e: 
                    #self.error('Error in check_dp_attributes_epoch(%s):\n%s' % (k,traceback.format_exc()))
                #finally: GlobalCallback.lock.release()
        #pass

    ##This is the only method that must be declared in the Child device side
    #def push_event(self,event):
        #try:
            #self.error('THIS IS DevChild(',self.get_name(),').push_event(',event.device,".",event.attr_name,'=',str(event.attr_value),')!!!, It should have been redefined inside inheriting classes!')
            ##att_name=(self.ParentName+'/'+self.ParentAttributes[0]).lower()
            ##print "att_name is %s, event value is %s, attributelist is %s"%(att_name,event.attr_value and event.attr_value.value or 'None',AttributesList[att_name].value)        
            #if att_name not in AttributesList.keys(): 
                #raise Exception('DevChild_%sAttributeNotRegistered'%self.ParentAttributes[0])
        #except Exception,e:
            #print 'exception in push_event(): ',e, ";", traceback.format_exc()
            
    #def setLastAttributeUpdate(self,att,date):
        #self.last_updates[att]=date
        
    #def getLastAttributeUpdate(self,att):
        #return self.last_updates[att] if att in self.last_updates.keys() else 0.0
    
    #def getLastUpdates(self):
        #report=''
        #for k,v in self.last_updates.items():
            #report='\n'.join([report,'%s updated at %s'%(k,time.ctime(v))])
        #return report
    
    #def force_ParentAttributes_polling(self):
        ##ForceParentPolling should be created as a DevVarStringArray Property before
        #self.info("In force_ParentAttributes_polling()")                    
        #if hasattr(self,'ForceParentPolling') and self.ForceParentPolling:
            #if self.ForceParentPolling[0].isdigit():
                    #period = int(self.ForceParentPolling[0])
                    ## Forcing the period to be between 3.5 seconds and 1 minute, 3.5 seconds is the minimum to avoid modbus timeout to provoke a PollThreadOutOfSync_Exception
                    #period = period<3500 and 3500 or period>60000 and 60000 or period
                    #dev = PyTango.DeviceProxy(self.ParentName)
                    #if len(self.ForceParentPolling)>1:
                        #self.ParentPolledAttributes=self.ForceParentPolling[1:]
                    #else:
                        #al = dev.get_attribute_list()
                        #pl = {}                            
                        #for a in al:
                            #pl[a]=dev.get_attribute_poll_period(a)
                            ##print 'Parent Polled Attribute %s: %d'%(a,pl[a])
                        #self.ParentPolledAttributes=[k for k,v in pl.items() if v>0 and v!=period]
                    ##self.PolledAttributes=['CPUStatus']+self.ForcePolling[1:]
                    #print 'ParentPolledAttributes=',str(self.ParentPolledAttributes)
                    #for att in self.ParentPolledAttributes:
                        #if att not in dev.get_attribute_list():
                            #continue
                        #try:                                
                            #self.debug(self.get_name()+'.forceAutoPolling(): forcing '+att+' polling to '+str(period))
                            ##ap = PyTango.AttributeProxy('/'.join([self.get_name(),att]))
                            ##if ap.is_polled() : ap.stop_poll()
                            ##ap.poll(period)
                            #if dev.is_attribute_polled(att):
                                #dev.stop_poll_attribute(att)
                            #dev.poll_attribute(att,period)
                            ##dev.read_attribute(att)
                        #except PyTango.DevFailed,e:
                            #err = e.args[0]
                            #PyTango.Except.throw_exception(str(err.reason),str(err.desc),str(err.origin))
                        #except Exception,e:
                            #print 'Exception at force_ParentAttributes_polling: ',str(getLastException())
                            #PyTango.Except.trhow_exception('DevChild_PollingParentAttributesException',str(e),'DevChild.force_ParentAttributes_polling')
                            ##print str(e)
                            ##raise e 
                        
                    #if not self.ParentPolledAttributes: self.ParentPolledAttributes=[None]
                    #del dev
        #self.debug("In force_ParentAttributes_polling(), finished"%self.get_name())                            
    #pass
    
    