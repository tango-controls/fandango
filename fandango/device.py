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


import sys,time,re
import threading,inspect,traceback,exceptions,operator

import log
from log import Logger
import excepts
from excepts import *
import callbacks
from callbacks import *

import servers
import functional as fun
from objects import Object,Struct
from dicts import CaselessDefaultDict,CaselessDict
from arrays import TimedQueue
from dynamic import DynamicDS

import PyTango
from PyTango import AttrQuality
if 'Device_4Impl' not in dir(PyTango):
    PyTango.Device_4Impl = PyTango.Device_3Impl
    
try:
    import tau
    USE_TAU=True
except:
    USE_TAU=False

####################################################################################################################
##@name Access Tango Devices and Database

##TangoDatabase singletone, This object is not thread safe, use TAU database if possible
global TangoDatabase,TangoDevice
TangoDatabase,TangoDevice = None,None

def get_database(): 
    global TangoDatabase
    if TangoDatabase is None:
        try: 
            TangoDatabase = USE_TAU and tau.Database() or PyTango.Database()
        except: pass
    return TangoDatabase

def get_device(dev): 
    #return USE_TAU and tau.core.TauManager().getFactory()().getDevice(dev) or PyTango.DeviceProxy(dev)
    return USE_TAU and tau.Device(dev) or PyTango.DeviceProxy(dev)

def get_database_device(): 
    global TangoDevice
    if TangoDevice is None:
        try:
           TangoDevice = get_device(TangoDatabase.dev_name())
        except: pass
    return TangoDevice

try:
    #TangoDatabase = USE_TAU and tau.core.TauManager().getFactory()().getDatabase() or PyTango.Database()
    TangoDatabase = get_database()
    TangoDevice = get_database_device()
except: pass
    
def add_new_device(server,klass,device):
    dev_info = PyTango.DbDevInfo()
    dev_info.name = device
    dev_info.klass = klass
    dev_info.server = server
    get_database().add_device(dev_info)    

####################################################################################################################
##@name Methods for searching the database with regular expressions
#@{

metachars = re.compile('([.][*])|([.][^*])|([$^+\-?{}\[\]|()])')

def parse_labels(text):
    if any(text.startswith(c[0]) and text.endswith(c[1]) for c in [('{','}'),('(',')'),('[',']')]):
        try:
            labels = eval(text)
            return labels
        except Exception,e:
            print 'ERROR! Unable to parse labels property: %s'%str(e)
            return []
    else:
        exprs = text.split(',')
        if all(':' in ex for ex in exprs):
            labels = [tuple(e.split(':',1)) for e in exprs]
        else:
            labels = [(e,e) for e in exprs]  
        return labels
        
def re_search_low(regexp,target): return re.search(regexp.lower(),target.lower())
def re_match_low(regexp,target): return re.match(regexp.lower(),target.lower())

def get_all_devices(expressions,limit=1000):
    ''' Returns the list of registered devices (including unexported) that match any of the given wildcars (Regexp not admitted!) '''
    results = []
    db = get_database()
    expressions = fun.toList(expressions)
    for target in expressions:
        if not target.count('/')>=2:
            print 'get_all_devices(%s): device names must have 2 slash characters'%target
            if len(expressions)>1: continue
            else: raise 'ThisIsNotAValidDeviceName'
        td,tf,tm = target.split('/')[:3]
        domains = db.get_device_domain(target)
        for d in domains:
            families = db.get_device_family(d+'/'+tf+'/'+tm)
            for f in families:
                members = db.get_device_member((d+'/'+f+'/'+tm))
                for m in members:
                    results.append('/'.join((d,f,m)))
    return results
                
def get_matching_devices(expressions,limit=1000):
    all_devs = list(get_database().get_device_name('*','*'))
    expressions = map(fun.toRegexp,fun.toList(expressions))
    return filter(lambda d: any(fun.matchCl(e+'$',d) for e in expressions),all_devs)

def get_matching_attributes(dev,expressions):
    """ Given a device name it returns the attributes matching any of the given expressions """
    expressions = map(fun.toRegexp,fun.toList(expressions))
    al = get_device(dev).get_attribute_list()
    result = [a for a in al for expr in expressions if fun.matchCl(expr,a)]
    return result

def get_matching_device_attributes(expressions,limit=1000):
    """ 
    Returns all matching device/attribute pairs. 
    regexp only allowed in attribute names
    :param express: like [domain_wild/family_wild/member_wild/attribute_regexp] 
    """
    attrs = []
    expressions = map(fun.partial(fun.toRegexp,terminate=True),fun.toList(expressions))
    for e in expressions:
        if e.count('/')==2: 
            dev,attr = e,'state'
        elif e.count('/')==3: 
            dev,attr = e.rsplit('/',1)
        else: 
            raise Exception('Expression must match domain/family/member/attribute shape!: %s'%e)
        for d in get_matching_devices(dev):
            try: 
                ats = get_matching_attributes(d,[attr])
                attrs.extend([d+'/'+a for a in ats])
                if len(attrs)>limit: break
            except: print 'Unable to get attributes for %s'%d
    return list(set(attrs))
    
def get_all_models(expressions,limit=1000):
    ''' It returns all the available Tango attributes matching any of a list of regular expressions.
    All devices matching expressions must be obtained.
    For each device only the good attributes are read.
    '''
    if isinstance(expressions,str): #evaluating expressions ....
        if any(re.match(s,expressions) for s in ('\{.*\}','\(.*\)','\[.*\]')): expressions = list(eval(expressions))
        else: expressions = expressions.split(',')
    elif isinstance(expressions,(USE_TAU and QtCore.QStringList or list,list,tuple,dict)):
        expressions = list(str(e) for e in expressions)
        
    print 'In get_all_models(%s:"%s") ...' % (type(expressions),expressions)
    db = get_database()
    if 'SimulationDatabase' in str(type(db)): #used by TauWidgets displayable in QtDesigner
      models = expressions
    else:
      all_devs = db.get_device_exported('*')
      models = []
      for exp in expressions:
          print 'evaluating exp = "%s"' % exp
          exp = str(exp)
          devs = []
          targets = []
          if exp.count('/')==3: device,attribute = exp.rsplit('/',1)
          else: device,attribute = exp,'State'
          
          if any(c in device for c in '.*[]()+?'):
              if '*' in device and '.*' not in device: device = device.replace('*','.*')
              devs = [s for s in all_devs if re_match_low(device,s)]
          else:
              devs = [device]
              
          print 'get_all_models(): devices matched by %s / %s are %d:' % (device,attribute,len(devs))
          print '%s' % (devs)
          for dev in devs:
              if any(c in attribute for c in '.*[]()+?'):
                  if '*' in attribute and '.*' not in attribute: attribute = attribute.replace('*','.*')
                  try: 
                      dp = get_device(dev)
                      attrs = [att.name for att in dp.attribute_list_query() if re_match_low(attribute,att.name)]
                      targets.extend(dev+'/'+att for att in attrs)
                  except Exception,e: print 'ERROR! Unable to get attributes for device %s: %s' % (dev,str(e))
              else: targets.append(dev+'/'+attribute)
          models.extend(targets)
    models = models[:limit]
    return models
              
#@}
########################################################################################    

########################################################################################
## Methods for managing device/attribute lists    
    
def attr2str(attr_value):
    att_name = '%s='%attr_value.name if hasattr(attr_value,'name') else ''
    if hasattr(attr_value,'value'):
        return '%s%s(%s)' %(att_name,type(attr_value.value).__name__,attr_value.value)
    else: 
        return '%s%s(%s)' %(att_name,type(attr_value).__name__,attr_value)
            
def get_distinct_devices(attrs):
    """ It returns a list with the distinct device names appearing in a list """
    return sorted(list(set(a.rsplit('/',1)[0] for a in attrs)))            
            
def get_distinct_domains(attrs):
    """ It returns a list with the distinc member names appearing in a list """
    return sorted(list(set(a.split('/')[0].split('-')[0] for a in attrs)))            

def get_distinct_families(attrs):
    """ It returns a list with the distinc member names appearing in a list """
    return sorted(list(set(a.split('/')[1].split('-')[0] for a in attrs)))            

def get_distinct_members(attrs):
    """ It returns a list with the distinc member names appearing in a list """
    return sorted(list(set(a.split('/')[2].split('-')[0] for a in attrs)))            

def get_distinct_attributes(attrs):
    """ It returns a list with the distinc attribute names (excluding device) appearing in a list """
    return sorted(list(set(a.rsplit('/',1)[-1] for a in attrs)))

def reduce_distinct(group1,group2):
    """ It returns a list of (device,domain,family,member,attribute) keys that appear in group1 and not in group2 """
    vals,rates = {},{}
    try:
        target = 'devices'
        k1,k2 = get_distinct_devices(group1),get_distinct_devices(group2)
        vals[target] = [k for k in k1 if k not in k2]
        rates[target] = float(len(vals[target]))/(len(k1))
    except: vals[target],rates[target] = [],0
    try:
        target = 'domains'
        k1,k2 = get_distinct_domains(group1),get_distinct_domains(group2)
        vals[target] = [k for k in k1 if k not in k2]
        rates[target] = float(len(vals[target]))/(len(k1))
    except: vals[target],rates[target] = [],0
    try:
        target = 'families'
        k1,k2 = get_distinct_families(group1),get_distinct_families(group2)
        vals[target] = [k for k in k1 if k not in k2]
        rates[target] = float(len(vals[target]))/(len(k1))
    except: vals[target],rates[target] = [],0
    try:
        target = 'members'
        k1,k2 = get_distinct_members(group1),get_distinct_members(group2)
        vals[target] = [k for k in k1 if k not in k2]
        rates[target] = float(len(vals[target]))/(len(k1))
    except: vals[target],rates[target] = [],0
    try:
        target = 'attributes'
        k1,k2 = get_distinct_attributes(group1),get_distinct_attributes(group2)
        vals[target] = [k for k in k1 if k not in k2]
        rates[target] = float(len(vals[target]))/(len(k1))
    except: vals[target],rates[target] = [],0
    return first((vals[k],rates[k]) for k,r in rates.items() if r == max(rates.values()))
 

########################################################################################
            
########################################################################################
## Methods for checking device/attribute availability
            
def get_db_device():
    return TangoDevice

def get_device_info(dev):
    """
    This method provides an alternative to DeviceProxy.info() for those devices that are not running
    """
    #vals = PyTango.DeviceProxy('sys/database/2').DbGetDeviceInfo(dev)
    vals = TangoDevice.DbGetDeviceInfo(dev)
    di = Struct([(k,v) for k,v in zip(('name','ior','level','server','host','started','stopped'),vals[1])])
    di.exported,di.PID = vals[0]
    return di

def get_device_host(dev):
    """
    Asks the Database device server about the host of this device 
    """
    return get_device_info(dev).host
   
def get_polled_attributes(dev):
    if isinstance(dev,PyTango.DeviceProxy): dp = dev
    else: dp = PyTango.DeviceProxy(dev)
    attrs = dp.get_attribute_list()
    periods = [(a,dp.get_attribute_poll_period(a)) for a in attrs]
    return dict((a,p) for a,p in periods if p)
   
def check_host(host):
    """
    Pings a hostname, returns False if unreachable
    """
    import fandango.linos
    print 'Checking host %s'%host
    return fandango.linos.ping(host)[host]

def check_starter(host):
    """
    Checks host's Starter server
    """
    if check_host(host):
        return check_device('tango/admin/%s'%(host.split('.')[0]))
    else:
        return False
    
def check_device(dev,attribute=None,command=None,full=False):
    """ 
    Command may be 'StateDetailed' for testing HdbArchivers 
    It will return True for devices ok, False for devices not running and None for unresponsive devices.
    """
    try:
        if full:
            info = get_device_info(dev)
            if not info.exported:
                return False
            if not check_host(info.host):
                return False
            if not check_device('dserver/%s'%info.server,full=False):
                return False
        dp = PyTango.DeviceProxy(dev)
        dp.ping()
    except:
        return False
    try:
        if attribute: dp.read_attribute(attribute)
        elif command: dp.command_inout(command)
        else: dp.state()
        return True
    except:
        return None            

def check_attribute(attr,readable=False,timeout=0):
    """ checks if attribute is available.
    :param readable: Whether if it's mandatory that the attribute returns a value or if it must simply exist.
    :param timeout: Checks if the attribute value have been effectively updated (check zombie processes).
    """
    try:
        #PyTango.AttributeProxy(attr).read()
        dev,att = attr.lower().rsplit('/',1)
        assert att in [str(s).lower() for s in PyTango.DeviceProxy(dev).get_attribute_list()]
        try: 
            attvalue = PyTango.AttributeProxy(attr).read()
            if readable and attvalue.quality == PyTango.AttrQuality.ATTR_INVALID:
                return None
            elif timeout and attvalue.time.totime()<(time.time()-timeout):
                return None
            else:
                return attvalue
        except Exception,e: 
            return None if readable else e
    except:
        return None    

def check_device_list(devices,attribute=None,command=None):
    """ 
    This method will check a list of devices grouping them by host and server; minimizing the amount of pings to do.
    """
    result = {}
    from collections import defaultdict
    hosts = defaultdict(lambda:defaultdict(list))
    for dev in devices:
        info = get_device_info(dev)
        if info.exported:
            hosts[info.host][info.server].append(dev)
        else:
            result[dev] = False
    for host,servs in hosts.items():
        if not check_host(host):
            print 'Host %s failed, discarding %d devices'%(host,sum(len(s) for s in servs.values()))
            result.update((d,False) for s in servs.values() for d in s)
        else:
            for server,devs in servs.items():
                if not check_device('dserver/%s'%server,full=False):
                    print 'Server %s failed, discarding %d devices'%(server,len(devs))
                    result.update((d,False) for d in devs)
                else:
                    for d in devs:
                        result[d] = check_device(d,attribute=attribute,command=command,full=False)
    return result
                    
####################################################################################################################
## The ProxiesDict class, to manage DeviceProxy pools

class ProxiesDict(CaselessDefaultDict,Object): #class ProxiesDict(dict,log.Logger):
    ''' Dictionary that stores PyTango.DeviceProxies
    It is like a normal dictionary but creates a new proxy each time that the "get" method is called
    An earlier version is used in PyTangoArchiving.utils module
    This class must be substituted by Tau.Core.TauManager().getFactory()()
    '''
    def __init__(self):
        self.log = Logger('ProxiesDict')
        self.log.setLogLevel('INFO')
        self.call__init__(CaselessDefaultDict,self.__default_factory__)
    def __default_factory__(self,dev_name):
        '''
        Called by defaultdict_fromkey.__missing__ method
        If a key doesn't exists this method is called and returns a proxy for a given device.
        If the proxy caused an exception (usually because device doesn't exists) a None value is returned
        '''        
        if dev_name not in self.keys():
            self.log.debug( 'Getting a Proxy for %s'%dev_name)
            try:
                devklass,attrklass = (tau.Device,tau.Attribute) if USE_TAU else (PyTango.DeviceProxy,PyTango.AttributeProxy)
                dev = (attrklass if str(dev_name).count('/')==3 else devklass)(dev_name)
            except Exception,e:
                self.log.warning('Device %s doesnt exist!'%dev_name)
                dev = None
        return dev
            
    def get(self,dev_name):
        return self[dev_name]   
    def get_admin(self,dev_name):
        '''Adds to the dictionary the admin device for a given device name and returns a proxy to it.'''
        dev = self[dev_name]
        class_ = dev.info().dev_class
        admin = dev.info().server_id
        return self['dserver/'+admin]
    def pop(self,dev_name):
        '''Removes a device from the dict'''
        if dev_name not in self.keys(): return
        self.log.debug( 'Deleting the Proxy for %s'%dev_name)
        return CaselessDefaultDict.pop(self,dev_name)
        
        
########################################################################################
## A useful fake attribute value and event class

def cast_tango_type(value_type):
    """ Returns the python equivalent to a Tango type"""
    if value_type in (PyTango.DevBoolean,): 
        return bool
    elif value_type in (PyTango.DevDouble,PyTango.DevFloat): 
        return float
    elif value_type in (PyTango.DevState,PyTango.DevShort,PyTango.DevInt,PyTango.DevLong,PyTango.DevLong64,PyTango.DevULong,PyTango.DevULong64,PyTango.DevUShort,PyTango.DevUChar): 
        return int
    else: 
        return str

class fakeAttributeValue(object):
    """ This class simulates a modifiable AttributeValue object (not available in PyTango)"""
    def __init__(self,name,value=None,time_=0.,quality=PyTango.AttrQuality.ATTR_VALID,dim_x=1,dim_y=1):
        self.name=name
        self.value=value
        self.write_value = None
        self.time=time_ or time.time()
        self.quality=quality
        self.dim_x=dim_x
        self.dim_y=dim_y
        
    def get_name(self): return self.name
    def get_value(self): return self.value
    def get_date(self): return self.date
    def get_quality(self): return self.quality
    
    def set_value(self,value,dim_x=1,dim_y=1):
        self.value = value
        self.dim_x = dim_x
        self.dim_y = dim_y
        #if fun.isSequence(value):
            #self.dim_x = len(value)
            #if value and fun.isSequence(value[0]):
                #self.dim_y = len(value[0])
        self.set_date(time.time())
    def set_date(self,timestamp):
        if not isinstance(timestamp,PyTango.TimeVal): 
            timestamp=PyTango.TimeVal(timestamp)
        self.time=timestamp
    def set_quality(self,quality):
        self.quality=quality
        
    def set_value_date(self,value,date):
        self.set_value(value)
        self.set_date(date)
    def set_value_date_quality(self,value,date,quality):
        self.set_value_date(value,date)
        self.set_quality(quality)
        
    def set_write_value(self,value):
        self.write_value = value
    def get_write_value(self,data = None):
        if data is None: data = []
        if fun.isSequence(self.write_value):
            [data.append(v) for v in self.write_value]
        else:
            data.append(self.write_value)
        return data
        
        
from dicts import Enumeration
fakeEventType = Enumeration(
    'fakeEventType', (
        'Change',
        'Config',
        'Periodic',
        'Error'
    ))
    
class fakeEvent(object):
    def __init__(self,device,attr_name,attr_value,err,errors):
        self.device=device
        self.attr_name=attr_name
        self.attr_value=attr_value
        self.err=err
        self.errors=errors    

########################################################################################
## Device servers template

class Dev4Tango(PyTango.Device_4Impl,log.Logger):
    """
    This class provides several new features to TangoDevice implementations.
    By including log.Logger it also includes objects.Object as parent class.
    It allows to use call__init__(self, klass, *args, **kw) to avoid multiple inheritance from same parent problems.
    Therefore, use self.call__init__(PyTango.Device_4Impl,cl,name) instead of PyTango.Device_4Impl.__init__(self,cl,name)
    
    It also allows to connect several devices within the same server or not usint tau.core
    """

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
        return self._state
    
    def dev_state(self):
        #@Tango7
        #This have been overriden to avoid device servers with states managed by qualities
        return self._state
    
    def State(self):
        """ State redefinition is required to keep independency between 
        attribute configuration (max/min alarms) and the device State """
        #return self.get_state()
        return self._state
    
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
        """ Returns a dictionary like {attr_name:period} """
        polled_attrs = {}
        for st in admin.DevPollStatus(name):
            lines = st.split('\n')
            try: polled_attrs[lines[0].split()[-1]]=lines[1].split()[-1]
            except: pass
        return polled_attrs
            
    def set_polled_attribute(self,name,period,type_='attribute'):
        args = [[period],[self.get_name(),type_,name]]
        admin = self.get_admin_device()
        if aname in self.get_polled_attrs(): 
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
        if not hasattr(self,'PollingCycle'): self.PollingCycle = 5000
        if not hasattr(self,'last_event_received'): self.last_event_received = 0
        device = device.lower()
        deviceObj = neighbours.get(device,None)
        if deviceObj is None:         
            from tau import Attribute,Device
            from tau.core import TauEventType            
            for attribute in attributes: #Done in two loops to ensure that all Cache objects are available
                self.info ('::init_device(%s): Configuring TauAttribute for %s' % (self.get_name(),device+'/'+attribute))
                aname = (device+'/'+attribute).lower()
                at = Attribute(aname)
                self.debug('Adding Listener ...')
                at.addListener(self.event_received)
                self.debug('Changing polling period ...')
                at.changePollingPeriod(self.PollingCycle)
                self.ExternalAttributes[aname] = at
        else: #Managing attributes from internal devices
            self.info('===========> Subscribing attributes from an internal device')
            for attribute in attributes:
                self.ExternalAttributes[(device+'/'+attribute).lower()] = fakeAttributeValue(attribute,None)
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
            from tau import Attribute
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
            from tau import Device
            Device(device).write_attribute(attribute,data)
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
            from tau import Device
            return Device(device).command_inout(target,argin)
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
                self.debug('====> updating values from %s.%s'%(device,attribute))
                deviceObj = self.get_devs_in_server().get(device,None)
                event_type = fakeEventType.lookup['Periodic']
                try:                                
                    if attr.name.lower()=='state': 
                        if hasattr(deviceObj,'last_state'): attr.set_value(deviceObj.last_state)
                        else: attr.set_value(deviceObj.get_state())
                    else: 
                        if isinstance(deviceObj,DynamicDS): 
                            method = 'read_dyn_attr'
                            deviceObj.myClass.DynDev = deviceObj
                        else: 
                            method = 'read_%s'%attr.name.lower()                         
                            
                        alloweds = [c for c in dir(deviceObj) if c.lower()=='is_%s_allowed'%attr.name.lower()]
                        is_allowed = not alloweds or getattr(deviceObj,alloweds[0])(PyTango.AttReqType.READ_REQ)
                        if is_allowed:
                            methods = [c for c in dir(deviceObj) if c.lower()==method]
                            if not methods: self.error('%s.read_%s method not found!!!'%(device,attr.name))
                            elif isinstance(deviceObj,DynamicDS): getattr(deviceObj,methods[0])(deviceObj,attr)
                            else: getattr(deviceObj,methods[0])(attr)
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
        #self.info,debug,error,warning should not be used here to avoid conflicts with tau.core logging
        def log(prio,s): print '%s %s %s: %s' % (prio.upper(),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),self.get_name(),s)
        self.last_event_received = time.time()
        log('info','In Dev4Tango.event_received(%s(%s),%s,%s) at %s'%(type(source).__name__,source,fakeEventType[type_],type(attr_value).__name__,self.last_event_received))
        return
        
    ##@}        
        

##############################################################################################################
## Tango formula evaluation
import dicts

class TangoEval(object):
    """ Class with methods copied from PyAlarm """
    def __init__(self,formula='',launch=True,trace=False, proxies=None, attributes=None):
        self.formula = formula
        self.variables = []
        self.proxies = proxies or dicts.defaultdict_fromkey(tau.Device) if USE_TAU else ProxiesDict()
        self.attributes = attributes or dicts.defaultdict_fromkey(tau.Attribute if USE_TAU else PyTango.AttributeProxy)
        self.previous = dicts.CaselessDict()
        self.last = dicts.CaselessDict()
        self.result = None
        self.trace = trace
        if self.formula and launch: 
            self.eval()
            if not self.trace: 
                print 'TangoEval: result = %s' % self.result
        return
        
    def parse_variables(self,formula):
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
        redev = '(?P<device>(?:'+alnum+':[0-9]+/)?(?:'+'/'.join([alnum]*3)+'))' #It matches a device name
        reattr = '(?:/(?P<attribute>'+alnum+')(?:(?:\\.)(?P<what>quality|time|value|exception))?)?' #Matches attribute and extension
        retango = redev+reattr#+'(?!/)'
        regexp = no_quotes + retango + no_quotes #Excludes attr_names between quotes
        #print regexp
        idev,iattr,ival = 0,1,2 #indexes of the expression matching device,attribute and value
        if '#' in formula:
            formula = formula.split('#',1)[0]
        if ':' in formula and not re.match('^',redev):
            tag,formula = formula.split(':',1)
        self.formula = formula
        ##@var all_vars list of tuples with (device,/attribute) name matches
        #self.variables = [(s[idev],s[iattr],s[ival] or 'value') for s in re.findall(regexp,formula) if s[idev]]
        self.variables = [s for s in re.findall(regexp,formula)]
        if self.trace: print 'TangoEval.parse_variables(%s): %s'%(formula,self.variables)
        return self.variables
        
    def read_attribute(self,device,attribute,what='value',_raise=True):
        """
        Executes a read_attribute and returns the value requested
        :param _raise: if attribute is empty or 'State' exceptions will be rethrown
        """
        if self.trace: print 'TangoEval.read_attribute(%s/%s.%s)'%(device,attribute,what)
        aname = (device+'/'+attribute).lower()
        try:
            if aname not in self.attributes:
                dp = self.proxies[device]
                dp.ping()
                # Disabled because we want DevFailed to be triggered
                #attr_list = [a.name.lower()  for a in dp.attribute_list_query()]
                #if attribute.lower() not in attr_list: #raise Exception,'TangoEval_AttributeDoesntExist_%s'%attribute
            value = self.attributes[aname].read()
            value = value if what=='all' else (False if what=='exception' else getattr(value,what))
            if self.trace: print 'TangoEval: Read %s.%s = %s' % (aname,what,value)
        except Exception,e:
            if _raise and attribute.lower() in ['','state']:
                raise e
            if isinstance(e,PyTango.DevFailed) and what=='exception':
                return True
            print 'TangoEval: ERROR(%s)! Unable to get %s for attribute %s/%s: %s' % (type(e),what,device,attribute,e)
            value = None
        return value
    
    def eval(self,formula=None,previous=None,_locals=None ,_raise=True):
        ''' 
        Evaluates the given formula
        :param _raise: if attribute is empty or 'State' exceptions will be rethrown
        '''
        self.formula = (formula or self.formula).strip()
        for x in ['or','and']: #Check for case-dependent operators
            self.formula = self.formula.replace(' '+x.upper()+' ',' '+x+' ')
        self.formula = self.formula.replace(' || ',' or ')
        self.formula = self.formula.replace(' && ',' and ')
        self.previous = previous or self.previous
        
        findables = re.findall('FIND\(([^)]*)\)',self.formula)
        for target in findables:
            res = str([d.lower() for d in get_matching_device_attributes([target.replace('"','').replace("'",'')])])
            self.formula = self.formula.replace("FIND(%s)"%target,res).replace('"','').replace("'",'')
            if self.trace: print 'TangoEval: Replacing with results for %s ...%s'%(target,res)
        
        self.parse_variables(self.formula)
        if self.trace: print 'TangoEval: variables in formula are %s' % self.variables
        source = self.formula #It will be modified on each iteration
        self.last.clear()
        for device,attribute,what in self.variables:
            target = device + (attribute and '/%s'%attribute) + (what and '.%s'%what)
            var_name = target.replace('/','_').replace('-','_').replace('.','_').replace(':','_').lower()
            if self.trace: print 'TangoEval(): %s => %s'%(target,var_name)
            self.previous[var_name] = self.read_attribute(device,attribute or 'State',what or 'value')
            self.last[target] = self.previous[var_name] #Used from alarm messages
            source = source.replace(target,var_name,1)

        if self.trace: print 'TangoEval: formula = %s; Values = %s' % (source,dict(self.last))
        _locals = _locals and dict(_locals) or {}
        [_locals.__setitem__(str(v),v) for v in PyTango.DevState.values.values()]
        [_locals.__setitem__(str(q),q) for q in PyTango.AttrQuality.values.values()]
        _locals['str2epoch'] = lambda *args: time.mktime(time.strptime(*args))
        _locals['time'] = time
        _locals['now'] = time.time()
        if self.trace: print 'TangoEval(%s,%s)'%(source,self.previous)
        self.result = eval(source,dict(self.previous),_locals)
        if self.trace: print 'TangoEval: result = %s' % self.result
        return self.result
    pass

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
    
    