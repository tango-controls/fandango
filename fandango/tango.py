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
@package tango
@brief provides tango utilities for fandango, like database search methods and emulated Attribute Event/Value types
@todo @warning IMPORTING THIS MODULE IS CAUSING SOME ERRORS WHEN CLOSING PYTHON DEVICE SERVERS,  BE CAREFUL!
"""

#python imports
import time,re,os

#pytango imports
import PyTango
from PyTango import AttrQuality
if 'Device_4Impl' not in dir(PyTango):
    PyTango.Device_4Impl = PyTango.Device_3Impl

#tau imports
try:
    assert str(os.getenv('USE_TAU')).strip().lower() not in 'no,false,0'
    try: 
        import taurus
        tau = TAU = taurus
    except:
        import tau
        TAU = tau
    USE_TAU=True
    """USE_TAU will be used to choose between taurus.Device and PyTango.DeviceProxy"""
except:
    print 'fandango.device: USE_TAU flag is disabled'
    USE_TAU=False

from . import objects
from . import functional as fun
from objects import Object,Struct

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
    
def get_attribute_label(target):
    ap = PyTango.AttributeProxy(target)
    cf = ap.get_config()
    return cf.label

def set_attribute_label(target,label='',unit=''):
    ap = PyTango.AttributeProxy(target)
    cf = ap.get_config()
    if label: cf.label = label
    if unit: cf.unit = unit
    ap.set_config(cf)
    
def property_undo(dev,prop,epoch):
    db = get_database()
    his = db.get_device_property_history(dev,prop)
    valids = [h for h in his if fun.str2time(h.get_date())<epoch]
    news = [h for h in his if fun.str2time(h.get_date())>epoch]
    if valids and news:
        print('Restoring property %s/%s to %s'%(dev,prop,valids[-1].get_date()))
        db.put_device_property(dev,{prop:valids[-1].get_value().value_string})
    elif not valids:print('No property values found for %s/%s before %s'%(dev,prop,fun.time2str(epoch)))
    elif not news: print('Property %s/%s not modified after %s'%(dev,prop,fun.time2str(epoch)))
    
def search_device_properties(dev,prop,exclude=''):
    db = get_database()
    result = {}
    devs = get_matching_devices(dev) #devs if fun.isSequence(dev) else [devs]
    props = prop if fun.isSequence(prop) else [prop]
    for d in devs:
        if exclude and fun.matchCl(exclude,d): continue
        r = {}
        vals = db.get_device_property(d,props)
        for k,v in vals.items():
            if v: r[k] = v[0]
        if r: result[d] = r
    if not fun.isSequence(devs):
        if not fun.isSequence(prop): return result.values().values()[0]
        else: return result.values()[0]
    else: return result

####################################################################################################################
##@name Methods for searching the database with regular expressions
#@{

#Regular Expressions
metachars = re.compile('([.][*])|([.][^*])|([$^+\-?{}\[\]|()])')
#alnum = '[a-zA-Z_\*][a-zA-Z0-9-_\*]*' #[a-zA-Z0-9-_]+ #Added wildcards
alnum = '(?:[a-zA-Z_\*]|(?:\.\*))(?:[a-zA-Z0-9-_\*]|(?:\.\*))*'
no_alnum = '[^a-zA-Z0-9-_]'
no_quotes = '(?:^|$|[^\'"a-zA-Z0-9_\./])'
rehost = '(?:(?P<host>'+alnum+':[0-9]+)(?:/))' #(?:'+alnum+':[0-9]+/)?
redev = '(?P<device>'+(rehost+'?')+'(?:'+'/'.join([alnum]*3)+'))' #It matches a device name
reattr = '(?:/(?P<attribute>'+alnum+')(?:(?:\\.)(?P<what>quality|time|value|exception))?)' #Matches attribute and extension
retango = redev+(reattr+'?')+'(?:\$?)' 

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

def get_all_devices(expressions,limit=1000):
    ''' Returns the list of registered devices (including unexported) that match any of the given wildcars (Regexp not admitted!) '''
    results = []
    db = get_database()
    expressions = fun.toList(expressions)
    for target in expressions:
        #if not target.count('/')>=2:
            #print 'get_all_devices(%s): device names must have 2 slash characters'%target
            #if len(expressions)>1: continue
            #else: raise 'ThisIsNotAValidDeviceName'
        match = fun.matchCl(retango,target,terminate=True)
        if not match: raise 'ThisIsNotAValidDeviceName:%s'%target
        #target = match.groups()[0]
        td,tf,tm = target.split('/')[-3:]
        domains = db.get_device_domain(target)
        for d in domains:
            families = db.get_device_family(d+'/'+tf+'/'+tm)
            for f in families:
                members = db.get_device_member((d+'/'+f+'/'+tm))
                for m in members:
                    results.append('/'.join((d,f,m)))
    return results
                
def get_matching_devices(expressions,limit=1000):
    if not fun.isSequence(expressions): expressions = [expressions]
    all_devs = []
    if any(not fun.matchCl(rehost,expr) for expr in expressions):
        all_devs.extend(list(get_database().get_device_name('*','*')))
    for expr in expressions:
        m = fun.matchCl(rehost,expr) 
        if m:
            host = m.groups()[0]
            print 'get_matching_devices(%s): getting %s devices ...'%(expr,host)
            odb = PyTango.Database(*host.split(':'))
            all_devs.extend('%s/%s'%(host,d) for d in odb.get_device_name('*','*'))
    expressions = map(fun.toRegexp,fun.toList(expressions))
    return filter(lambda d: any(fun.matchCl(e,d,terminate=True) for e in expressions),all_devs)

def get_matching_attributes(dev,expressions):
    """ Given a device name it returns the attributes matching any of the given expressions """
    expressions = map(fun.toRegexp,fun.toList(expressions))
    al = get_device(dev).get_attribute_list()
    result = [a for a in al for expr in expressions if fun.matchCl(expr,a,terminate=True)]
    return result

def get_matching_device_attributes(expressions,limit=1000):
    """ 
    Returns all matching device/attribute pairs. 
    regexp only allowed in attribute names
    :param expressions: a list of expressions like [domain_wild/family_wild/member_wild/attribute_regexp] 
    """
    attrs = []
    def_host = os.getenv('TANGO_HOST')
    if not fun.isSequence(expressions): expressions = [expressions]
    #expressions = map(fun.partial(fun.toRegexp,terminate=True),fun.toList(expressions))
    for e in expressions:
        match = fun.matchCl(retango,e,terminate=True)
        if not match:
            raise Exception('Expression must match domain/family/member/attribute shape!: %s'%e)
        else:
            host,dev,attr = [d[k] for k in ('host','device','attribute') for d in (match.groupdict(),)]
            host,attr = host or def_host,attr or 'state'
        print 'get_matching_device_attributes(e) -> %s / %s / %s'%(host,dev,attr)
        #if e.count('/')==2: 
            #dev,attr = e,'state'
        #elif e.count('/')==3: 
            #dev,attr = e.rsplit('/',1)
        #else: 
            #raise Exception('Expression must match domain/family/member/attribute shape!: %s'%e)
        for d in get_matching_devices(dev):
            print 'get_matching_device_attributes(%s,%s)...'%(dev,attr)
            if fun.matchCl(attr,'state',terminate=True):
                attrs.append(d+'/State')
            if attr.lower().strip() != 'state':
                try: 
                    ats = get_matching_attributes(d,[attr])
                    attrs.extend([d+'/'+a for a in ats])
                    if len(attrs)>limit: break
                except: 
                    print 'Unable to get attributes for %s'%d
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
              devs = [s for s in all_devs if fun.matchCl(device,s)]
          else:
              devs = [device]
              
          print 'get_all_models(): devices matched by %s / %s are %d:' % (device,attribute,len(devs))
          print '%s' % (devs)
          for dev in devs:
              if any(c in attribute for c in '.*[]()+?'):
                  if '*' in attribute and '.*' not in attribute: attribute = attribute.replace('*','.*')
                  try: 
                      dp = get_device(dev)
                      attrs = [att.name for att in dp.attribute_list_query() if fun.matchCl(attribute,att.name)]
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
    """ This class simulates a modifiable AttributeValue object (not available in PyTango)
    :param parent: Apart of common Attribute arguments, parent will be used to keep a proxy to the parent object (a DeviceProxy or DeviceImpl) 
    """
    def __init__(self,name,value=None,time_=0.,quality=PyTango.AttrQuality.ATTR_VALID,dim_x=1,dim_y=1,parent=None,device=''):
        self.name=name
        self.device=device or (self.name.split('/')[-1] if '/' in self.name else '')
        self.value=value
        self.write_value = None
        self.time=time_ or time.time()
        self.quality=quality
        self.dim_x=dim_x
        self.dim_y=dim_y
        self.parent=parent
        
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