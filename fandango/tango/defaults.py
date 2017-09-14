#!/usr/bin/env python

#############################################################################
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
provides tango utilities for fandango, like database search methods and 
emulated Attribute Event/Value types

This module is a light-weight set of utilities for PyTango.
Classes dedicated for device management will go to fandango.device
Methods for Astor-like management will go to fandango.servers

.. contents::

.

"""

#python imports
import time,re,os,traceback,threading

#pytango imports
import PyTango
from PyTango import AttrQuality,EventType,DevState,AttrDataFormat,\
  AttrWriteType,CmdArgType,AttributeProxy,DeviceProxy, AttReqType

if 'Device_4Impl' not in dir(PyTango):
    PyTango.Device_4Impl = PyTango.Device_3Impl

import fandango
import fandango.objects as objects
import fandango.dicts as dicts
from fandango.functional import *

from fandango.dicts import CaselessDefaultDict,CaselessDict,Enumeration
from fandango.objects import Object,Struct,Cached
from fandango.log import Logger,except2str,printf
from fandango.excepts import exc2str

#taurus imports, here USE_TAU is defined for all fandango
global TAU,USE_TAU,TAU_LOGGER
TAU,USE_TAU = None,False
def loadTaurus():
    print('%s fandango.tango.loadTaurus()'%time.ctime())
    global TAU,USE_TAU,TAU_LOGGER
    try:
        assert str(os.getenv('USE_TAU')).strip().lower() not in 'no,false,0'
        import taurus
        TAU = taurus
        USE_TAU=True
        TAU_LOGGER = taurus.core.util.Logger
        """USE_TAU will be used to choose between taurus.Device 
        and PyTango.DeviceProxy"""
    except:
        print('fandango.tango: USE_TAU disabled')
        TAU = None
        USE_TAU=False
        TAU_LOGGER = Logger
    return bool(TAU)


TANGO_STATES = \
  'ON OFF CLOSE OPEN INSERT EXTRACT MOVING STANDBY FAULT INIT RUNNING ALARM '\
      'DISABLE UNKNOWN'.split()
TANGO_COLORS = \
  'Lime White White Lime White Lime LightBlue Yellow Red Brown LightBlue'\
      ' Orange Magenta Grey'.split()

TANGO_STATE_COLORS = dict(zip(TANGO_STATES,TANGO_COLORS))

ATTR_ALARM = AttrQuality.ATTR_ALARM
ATTR_WARNING = AttrQuality.ATTR_WARNING
ATTR_VALID = AttrQuality.ATTR_VALID
ATTR_INVALID = AttrQuality.ATTR_INVALID

#Regular Expressions
metachars = re.compile('([.][*])|([.][^*])|([$^+\-?{}\[\]|()])')
#alnum = '[a-zA-Z_\*][a-zA-Z0-9-_\*]*' #[a-zA-Z0-9-_]+ #Added wildcards
alnum = '(?:[a-zA-Z0-9-_\*]|(?:\.\*))(?:[a-zA-Z0-9-_\*]|(?:\.\*))*'
no_alnum = '[^a-zA-Z0-9-_]'
no_quotes = '(?:^|$|[^\'"a-zA-Z0-9_\./])'
rehost = '(?:(?P<host>'+alnum+'(?:\.'+alnum+')?'+'(?:\.'+alnum+')?'\
    +'(?:\.'+alnum+')?'+'[\:][0-9]+)(?:/))' #(?:'+alnum+':[0-9]+/)?
redev = '(?P<device>'+'(?:'+'/'.join([alnum]*3)+'))' #It matches a device name
reattr = '(?:/(?P<attribute>'+alnum\
    +')(?:(?:\\.)(?P<what>quality|time|value|exception|history))?)'
    #reattr matches attribute and extension
retango = '(?:tango://)?'+(rehost+'?')+redev+(reattr+'?')+'(?:\$?)' 

AC_PARAMS = [
    'color',
    'display_unit',
    #'writable',
    'standard_unit',
    'quality',
    'unit',
    'string',
    'label',
    'min_alarm',
    'events',
    'description',
    #'data_type',
    'format',
    'max_alarm',
    #'device',
    #'name',
    #'database',
    #'data_format',
    #'value',
    #'polling',
    #'time',
    'alarms',
    #'model',
    #ALARMS
    'delta_t',
    'max_alarm',
    'min_warning',
    #'extensions',
    'delta_val',
    'min_alarm',
    'max_warning'
    #EVENTS
    #'extensions',
    'period',
    'archive_period',
    #'extensions',
    'archive_rel_change',
    'archive_abs_change',
    'rel_change',
    #'extensions',
    'abs_change',
    'per_event',
    'ch_event',
    'arch_event',
    ]


###############################################################################
##@name Access Tango Devices and Database

##TangoDatabase singletone
global TangoDatabase,TangoDevice,TangoProxies
TangoDatabase,TangoDevice,TangoProxies = None,None,None

def get_tango_host(dev_name='',use_db=False):
    """
    If device is a tango model, it will extract the host from the model URL
    If devicesis none, then environment variable or PyTango.Database are used 
    to extract the host
    If TANGO_HOST is not defined it will always fallback to PyTango.Database()
    """
    try:
        if dev_name:
            
            if isString(dev_name):
              dev_name = str(dev_name).replace('tango://','')
              m  = matchCl(rehost,dev_name)
            else: 
              m,use_db = None,dev_name
              
            return m.groups()[0] if m else get_tango_host(use_db=use_db)
        
        elif use_db:
            use_db = use_db if hasattr(use_db,'get_db_host') \
                            else get_database()
            host,port = use_db.get_db_host(),int(use_db.get_db_port())
            if (matchCl('.*[a-z].*',host.lower())
              #and PyTango.__version_number__ < 800):
              ): #The bug is back!!
                #Remove domain name
                host = host.strip().split('.')[0]
            return "%s:%d"%(host,port)
        else:
            host = os.getenv('TANGO_HOST') 
            return host or get_tango_host(use_db=True) 
    except:
        print('ERROR: get_tango_host(): '+traceback.format_exc())
        return 'localhost:10000'
    
def get_database(host='',port='',use_tau=False): 
    """
    Method to get a singleton instance of the Tango Database
    host/port can be a host,port tuple; a 'host:port' string or a taurus model.
    @TODO: host/port is checked only at first creation, once initialized 
    you can't change HOST
    """
    global TangoDatabase
    global TAU,USE_TAU
    if host in (True,False): 
        #For backwards compatibility
        use_tau,host,port = host,'','' 
    else:
      if '/' in host: 
        # Parsing a taurus model
        host = get_tango_host(host)
      if ':' in host: 
        # Parsing a host:port string
        host,port = host.split(':')
    args = [host,int(port)] if host and port else []
    
    ### DISABLED, CRUSHED WITH BAD_INV_ORDER CORBA in Tango8
    if False and not args and TangoDatabase:
        try:
            t = time.time()
            #TangoDatabase.get_info() #TOO SLOW TO BE A CHECK!
            #TangoDatabase.check_tango_host(TangoDatabase.get_db_host()\
                #+':'+TangoDatabase.get_db_port())
            #TangoDatabase.get_timeout_millis()
            print(time.time()-t)
            return TangoDatabase 
        except:
            #traceback.print_exc()
            pass #defaulting to Taurus/PyTango
    try: 
        if use_tau and not TAU: TAU = loadTaurus()
        if use_tau and TAU: print('LOADING TANGO DATABASE VIA TAURUS')
        db = (use_tau and TAU and TAU.Database(*args)) \
            or PyTango.Database(*args)
        if not args: TangoDatabase = db
        return db
    except:
        print(traceback.format_exc())
    return
        
def get_proxy(argin,use_tau=False,keep=False):
    """
    Returns attribute or device proxy depending on argin syntax
    """
    if argin.count('/')>(2+(':' in argin)):
        return PyTango.AttributeProxy(argin)
    else:
        return get_device(argin,use_tau,keep)

def get_device(dev,use_tau=False,keep=False): 
    if use_tau and not TAU: use_tau = loadTaurus()
    if isinstance(dev,basestring): 
        if dev.count('/')==1: dev = 'dserver/'+dev
        if use_tau and TAU: 
            return TAU.Device(dev)
        else:
            global TangoProxies
            if keep and TangoProxies is None: 
                TangoProxies = ProxiesDict(use_tau=use_tau)
            if TangoProxies and (dev in TangoProxies or keep):
                return TangoProxies[dev]
            else: 
                return PyTango.DeviceProxy(dev)
    elif isinstance(dev,PyTango.DeviceProxy) \
        or (use_tau and TAU and isinstance(dev,TAU.core.tango.TangoDevice)):
        return dev
    else:
        return None

def get_database_device(use_tau=False,db=None): 
    global TangoDevice
    td = TangoDevice
    #print('get_database_device(%s,use_tau=%s,db=%s)'%(td,use_tau,db))
    if db is None and td is not None:
      return td
    else:
        try:
           dev_name = (db or get_database(use_tau=use_tau)).dev_name()
           dev_name = get_tango_host(use_db=db)+'/'+dev_name \
               if db else dev_name
           td = get_device(dev_name,use_tau=use_tau)
        except: 
           print('get_database_device(%s,use_tau=%s,db=%s)'
                 %(dev_name,use_tau,db))
           traceback.print_exc()
        if db is None: 
          TangoDevice = td
    return td


###############################################################################
## A useful fake attribute value and event class
    
class fakeAttributeValue(object):
    """ 
    This class simulates a modifiable AttributeValue object 
        (not available in PyTango)
    It is the class used to read values from Dev4Tango devices 
        (valves, pseudos, composer, etc ...)
    It also has a read(cache) method to be used as a TaurusAttribute 
        or AttributeProxy (but it returns self if cache is not used)
    The cache is controlled by keeptime variable (milliseconds)
    :param parent: Apart of common Attribute arguments, 
        parent will be used to keep a proxy to the parent object (a DeviceProxy or DeviceImpl) 
    """
    def __init__(self,name,value=None,time_=0.,
                 quality=PyTango.AttrQuality.ATTR_VALID,
                 dim_x=1,dim_y=1,parent=None,device='',
                 error=False,keeptime=0):
        self.name=name
        self.device=device or (self.name.rsplit('/',1)[0] 
                               if '/' in self.name else '')
        self.set_value(value,dim_x,dim_y)
        self.set_date(time_ or time.time())
        self.write_value = self.wvalue = None
        self.quality=quality
        self.parent=parent
        self.error = self.err = error
        self.keeptime = keeptime*1e3 if keeptime<10. else keeptime
        self.lastread = 0
        self.type = type(value)
        
    def __repr__(self):
        return 'fakeAttributeValue(%s,%s,%s,%s,error=%s)'\
                %(self.name,fandango.log.shortstr(self.value),
                  time.ctime(self.get_time()),self.quality,self.error)

    __str__ = __repr__
        
    def get_name(self): return self.name
    def get_value(self): return self.value
    def get_date(self): return self.time
    def get_time(self): return self.time.totime()
    def get_quality(self): return self.quality
    
    def read(self,cache=True):
        #Method to emulate AttributeProxy returning an AttributeValue
        if not self.parent:
            self.parent = get_device(self.device,use_tau=False,keep=True)
        if not cache or 0<self.keeptime<(time.time()-self.read()):
            #it's important to pass self as argument so values will be kept
            import fandango.tango.methods as fmt
            return fmt.read_internal_attribute(self.parent,self) 
        return self 
    
    def throw_exception(self,msg=''):
        self.err = self.error = msg or traceback.format_exc()
        print('fakeAttributeValue(%s).throw_exception(%s)'
              %(self.name,self.error))
        #event_type = fakeEventType.lookup['Error']
        self.set_value(None)
        self.set_quality(PyTango.AttrQuality.ATTR_INVALID)
        raise Exception(self.error)
    
    def set_value(self,value,dim_x=1,dim_y=1,err=False):
        self.value = self.rvalue = value
        self.err = (err or 
              isinstance(self.value,(PyTango.DevFailed,PyTango.DevError)))
        
        if (dim_x,dim_y) == (1,1):
            if isSequence(value): 
                dim_x = len(value)
                if len(value)>1 and isSequence(value[0]):
                    dim_y = len(value[0])
                    
        self.dim_x = dim_x
        self.dim_y = dim_y
        self.set_date(time.time())
        self.lastread = time.time()
        
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
        self.write_value = self.wvalue = value
    def get_write_value(self,data = None):
        if data is None: data = []
        if isSequence(self.write_value):
            [data.append(v) for v in self.write_value]
        else:
            data.append(self.write_value)
        return data
        
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
        
###############################################################################
## The ProxiesDict class, to manage DeviceProxy pools

class ProxiesDict(CaselessDefaultDict,Object): 
    ''' Dictionary that stores PyTango.DeviceProxies
    It is like a normal dictionary but creates a new proxy each time 
        that the "get" method is called
    An earlier version is used in PyTangoArchiving.utils module
    This class must be substituted by Tau.Core.TauManager().getFactory()()
    '''
    def __init__(self,use_tau = False, tango_host = ''):
        self.log = Logger('ProxiesDict')
        self.log.setLogLevel('INFO')
        self.use_tau = TAU and use_tau
        self.tango_host = tango_host
        self.call__init__(CaselessDefaultDict,self.__default_factory__)

    def __default_factory__(self,dev_name):
        '''
        Called by defaultdict_fromkey.__missing__ method
        If a key doesn't exists this method is called and 
        returns a proxy for a given device.
        If the proxy caused an exception (usually because device 
        doesn't exists) a None value is returned
        '''
        
        if self.tango_host and ':' not in dev_name:
            dev_name = self.tango_host + '/' + dev_name
            
        if dev_name not in self.keys():
            self.log.debug( 'Getting a Proxy for %s'%dev_name)
            
            try:
                devklass,attrklass = (TAU.Device,TAU.Attribute) \
                    if self.use_tau else \
                    (PyTango.DeviceProxy,PyTango.AttributeProxy)
                dev = (attrklass if 
                    str(dev_name).count('/')==(4 if ':' in dev_name else 3) 
                    else devklass)(dev_name)
            except Exception,e:
                print('ProxiesDict: %s doesnt exist!'%dev_name)
                dev = None
        return dev
      
    def __getitem__(self,key):
        if self.tango_host and ':' not in key:
            key = self.tango_host + '/' + key
        return CaselessDefaultDict.__getitem__(self,key)
            
    def get(self,dev_name):
        return self[dev_name]
      
    def get_admin(self,dev_name):
        '''Adds to the dictionary the admin device for a given device name
        and returns a proxy to it.'''
        dev = self[dev_name]
        class_ = dev.info().dev_class
        admin = dev.info().server_id
        return self['dserver/'+admin]
      
    def pop(self,dev_name):
        '''Removes a device from the dict'''
        if self.tango_host and ':' not in dev_name:
            dev_name = self.tango_host + '/' + dev_name
        if dev_name not in self.keys(): return
        self.log.debug( 'Deleting the Proxy for %s'%dev_name)
        return CaselessDefaultDict.pop(self,dev_name)
        
