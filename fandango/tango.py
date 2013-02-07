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

This module is a light-weight set of utilities for PyTango.
Classes dedicated for device management will go to fandango.device
Methods for Astor-like management will go to fandango.servers
"""

#python imports
import time,re,os,traceback

#pytango imports
import PyTango
from PyTango import AttrQuality
if 'Device_4Impl' not in dir(PyTango):
    PyTango.Device_4Impl = PyTango.Device_3Impl

#taurus imports, here USE_TAU is defined for all fandango
try:
    assert str(os.getenv('USE_TAU')).strip().lower() not in 'no,false,0'
    import taurus
    TAU = taurus
    USE_TAU=True
    """USE_TAU will be used to choose between taurus.Device and PyTango.DeviceProxy"""
except:
    print 'fandango.tango: USE_TAU disabled'
    USE_TAU=False

import objects
import threading
import functional as fun
from dicts import CaselessDefaultDict,CaselessDict
from objects import Object,Struct
from log import Logger,except2str,printf

####################################################################################################################
##@name Access Tango Devices and Database

##TangoDatabase singletone, This object is not thread safe, use TAU database if possible
global TangoDatabase,TangoDevice
TangoDatabase,TangoDevice = None,None

def get_database(): 
    global TangoDatabase
    if TangoDatabase is None:
        try: 
            TangoDatabase = USE_TAU and taurus.Database() or PyTango.Database()
        except: pass
    return TangoDatabase

def get_device(dev): 
    if isinstance(dev,basestring): 
        if USE_TAU: return TAU.Device(dev)
        else: return PyTango.DeviceProxy(dev)
    elif isinstance(dev,PyTango.DeviceProxy) or (USE_TAU and isinstance(dev,TAU.core.tango.TangoDevice)):
        return dev
    else:
        return None

def get_database_device(): 
    global TangoDevice
    if TangoDevice is None:
        try:
           TangoDevice = get_device(TangoDatabase.dev_name())
        except: pass
    return TangoDevice

try:
    #TangoDatabase = USE_TAU and taurus.core.TaurusManager().getFactory()().getDatabase() or PyTango.Database()
    TangoDatabase = get_database()
    TangoDevice = get_database_device()
except: pass
    
def add_new_device(server,klass,device):
    dev_info = PyTango.DbDevInfo()
    dev_info.name = device
    dev_info.klass = klass
    dev_info.server = server
    get_database().add_device(dev_info)    
    
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

def get_device_started(target):
    """ Returns device started time """
    return get_database_device().DbGetDeviceInfo(target)[-1][5]
    
def get_device_for_alias(alias):
    try: return get_database().get_device_alias(alias)
    except Exception,e:
        if 'no device found' in str(e).lower(): return None
        return None #raise e

def get_alias_for_device(dev):
    try: return get_database().get_alias(dev) #.get_database_device().DbGetDeviceAlias(dev)
    except Exception,e:
        if 'no alias found' in str(e).lower(): return None
        return None #raise e

def get_alias_dict(exp='*'):
    tango = get_database()
    return dict((k,tango.get_device_alias(k)) for k in tango.get_device_alias_list(exp))

def get_real_name(dev,attr=None):
    """
    It translate any device/attribute string by name/alias/label
    """
    if fandango.isString(dev):
        if attr is None and dev.count('/') in (1,4 if ':' in dev else 3): dev,attr = dev.rsplit('/',1)
        if '/' not in dev: dev = get_device_for_alias(dev)
        if attr is None: return dev
    for a in get_device_attributes(dev):
        if fandango.matchCl(attr,a): return (dev+'/'+a)
        if fandango.matchCl(attr,get_attribute_label(dev+'/'+a)): return (dev+'/'+a)
    return None

def get_device_commands(dev):
    return [c.cmd_name for c in get_device(dev).command_list_query()]

def get_device_attributes(dev,expressions='*'):
    """ Given a device name it returns the attributes matching any of the given expressions """
    expressions = map(fun.toRegexp,fun.toList(expressions))
    al = (get_device(dev) if fandango.isString(dev) else dev).get_attribute_list()
    result = [a for a in al for expr in expressions if fun.matchCl(expr,a,terminate=True)]
    return result
        
def get_device_labels(target,filters='',brief=True):
    """
    Returns an {attr:label} dict for all attributes of this device 
    Filters will be a regular expression to apply to attr or label.
    If brief is True (default) only those attributes with label are returned.
    This method works offline, does not need device to be running
    """
    labels = {}
    if fandango.isString(target): d = get_device(target)
    else: d,target = target,target.name()
    db = get_database()
    attrlist = db.get_device_attribute_list(target,filters) if brief else d.get_attribute_list()
    for a in attrlist:
        l = get_attribute_label(target+'/'+a,use_db=True) if brief else d.get_attribute_config(a).label
        if (not filters or any(map(fun.matchCl,(filters,filters),(a,l)))) and (not brief or l!=a): 
            labels[a] = l
    return labels
    
def set_device_labels(target,labels):
    """
    Applies an {attr:label} dict for attributes of this device 
    """
    labels = CaselessDict(labels)
    d = get_device(target)
    for a in d.get_attribute_list():
        if a in labels:
            ac = d.get_attribute_config(a)
            ac.label = labels[a]
            d.set_attribute_config(ac)
    return labels

def get_matching_device_attribute_labels(device,attribute):
    """ To get all gauge port labels: get_matching_device_attribute_labels('*vgct*','p*') """
    devs = get_matching_devices(device)
    return dict((t+'/'+a,l) for t in devs for a,l in get_device_labels(t,attribute).items())

def get_attribute_label(target,use_db=True):
    dev,attr = target.rsplit('/',1)
    if not use_db: #using AttributeProxy
        if attr.lower() in ('state','status'): 
            return attr
        ap = PyTango.AttributeProxy(target)
        cf = ap.get_config()
        return cf.label
    else: #using DatabaseDevice
        return (get_database().get_device_attribute_property(dev,[attr])[attr].get('label',[attr]) or [''])[0]
    
def set_attribute_label(target,label='',unit=''):
    if target.lower().rsplit('/')[-1] in ('state','status'): 
        return
    ap = PyTango.AttributeProxy(target)
    cf = ap.get_config()
    if label: cf.label = label
    if unit: cf.unit = unit
    ap.set_config(cf)
    
def parse_db_command_array(data,keys=1,depth=2):
    """ 
    This command will parse data received from DbGetDeviceAttributeProperty2 command.
    DB device commands return data in this format: X XSize Y YSize Z ZSize ZValue W WSize WValue
    This corresponds to {X:{Y:{Z:[Zdata],W:[Wdata]}}}
    Depth of the array is 2 by default
    e.g.: 
    label_of_dev_test_attribute = parse_db_command_array(dbd.DbGetDeviceAttributeProperty2([dev,attr]).,keys=1,depth=2)[dev][attr]['label'][0]
    """
    dict = {}
    #print '[%s]: %s' % (keys,data)
    for x in range(keys):
        key = data.pop(0)
        try: length = data.pop(0)
        except: return None
        #print '%s,%s,%s => '%(key,length,depth)
        if depth:
            k,v = key,parse_db_command_array(data,keys=int(length),depth=depth-1)
        else:
            try:
                length = int(length)
                k,v = key,[data.pop(0) for y in range(length)]
            except:
                k,v = key,[length]
        #print '\t%s,%s'%(k,v)
        dict.update([(k,v)])
    return dict
            
def get_devices_properties(expr,properties,hosts=[],port=10000):
    """get_devices_properties('*alarms*',props,hosts=[get_bl_host(i) for i in bls])"""
    if not isinstance(properties,dict): properties = dict.fromkeys(properties,[])
    get_devs = lambda db, reg : [d for d in db.get_device_name('*','*') if not d.startswith('dserver') and fandango.matchCl(reg,d)]
    if hosts: tango_dbs = dict(('%s:%s'%(h,port),PyTango.Database(h,port)) for h in hosts)
    else: tango_dbs = {os.getenv('TANGO_HOST'):PyTango.Database()}
    return dict(('/'.join((host,d)),db.get_device_property(d,properties.keys())) for host,db in tango_dbs.items() for d in get_devs(db,expr))
    
def get_matching_device_properties(dev,prop,exclude=''):
    db = get_database()
    result = {}
    devs = dev if fun.isSequence(dev) else get_matching_devices(dev) #devs if fun.isSequence(dev) else [devs]
    props = prop if fun.isSequence(prop) else list(set(s for d in devs for s in db.get_device_property_list(d,prop)))
    print 'devs: %s'%devs
    print 'props: %s'%props
    for d in devs:
        if exclude and fun.matchCl(exclude,d): continue
        r = {}
        vals = db.get_device_property(d,props)
        for k,v in vals.items():
            if v: r[k] = v[0]
        if r: result[d] = r
    if not fun.isSequence(devs) or len(devs)==1:
        if len(props)==1: return result.values()[0].values()[0]
        else: return result.values()[0]
    else: return result
    
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

####################################################################################################################
##@name Methods for searching the database with regular expressions
#@{

#Regular Expressions
metachars = re.compile('([.][*])|([.][^*])|([$^+\-?{}\[\]|()])')
#alnum = '[a-zA-Z_\*][a-zA-Z0-9-_\*]*' #[a-zA-Z0-9-_]+ #Added wildcards
alnum = '(?:[a-zA-Z0-9-_\*]|(?:\.\*))(?:[a-zA-Z0-9-_\*]|(?:\.\*))*'
no_alnum = '[^a-zA-Z0-9-_]'
no_quotes = '(?:^|$|[^\'"a-zA-Z0-9_\./])'
rehost = '(?:(?P<host>'+alnum+'(?:\.'+alnum+')?'+'(?:\.'+alnum+')?'+':[0-9]+)(?:/))' #(?:'+alnum+':[0-9]+/)?
redev = '(?P<device>'+'(?:'+'/'.join([alnum]*3)+'))' #It matches a device name
reattr = '(?:/(?P<attribute>'+alnum+')(?:(?:\\.)(?P<what>quality|time|value|exception))?)' #Matches attribute and extension
retango = '(?:tango://)?'+(rehost+'?')+redev+(reattr+'?')+'(?:\$?)' 

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
        
def parse_tango_model(name,use_tau=False):
    """
    {'attributename': 'state',
    'devicename': 'bo01/vc/ipct-01',
    'host': 'alba02',
    'port': '10000',
    'scheme': 'tango'}
    """
    values = {'scheme':'tango'}
    values['host'],values['port'] = os.getenv('TANGO_HOST').split(':',1)
    try:
        if not use_tau or not USE_TAU: raise Exception('NotTau')
        from taurus.core import tango as tctango
        from taurus.core import AttributeNameValidator,DeviceNameValidator
        validator = {tctango.TangoDevice:DeviceNameValidator,tctango.TangoAttribute:AttributeNameValidator}
        values.update((k,v) for k,v in validator[tctango.TangoFactory().findObjectClass(name)]().getParams(name).items() if v)
    except:
        name = str(name).replace('tango://','')
        m = re.match(fandango.tango.retango,name)
        if m:
            gd = m.groupdict()
            values['devicename'] = '/'.join([s for s in gd['device'].split('/') if ':' not in s])
            if gd.get('attribute'): values['attributename'] = gd['attribute']
            if gd.get('host'): values['host'],values['port'] = gd['host'].split(':',1)
    if 'devicename' not in values: return None
    values['device'] = values['devicename']
    if 'attributename' in values: values['attribute'] = values['attributename']
    return values

import fandango.objects
class get_all_devices(fandango.objects.SingletonMap):
    def __init__(self,exported=False,keeptime=60):
        self._all_devs = []
        self._last_call = 0
        self._keeptime = keeptime #Only 1 query/minute to DB allowed
        self._exported = exported
    def get_all_devs(self):
        now = time.time()
        if not self._all_devs or now>(self._last_call+self._keeptime):
            print 'updating all_devs ...'
            self._all_devs = list(get_database().get_device_exported('*') if self._exported else get_database().get_device_name('*','*'))
            self._last_call = now
        return self._all_devs
    def __new__(cls,*p,**k):
        instance = fandango.objects.SingletonMap.__new__(cls,*p,**k)
        return instance.get_all_devs()
    
def get_matching_devices(expressions,limit=0,exported=False):
    """ 
    Searches for devices matching expressions, if exported is True only running devices are returned 
    """
    if not fun.isSequence(expressions): expressions = [expressions]
    all_devs = []
    if any(not fun.matchCl(rehost,expr) for expr in expressions): all_devs.extend(get_all_devices(exported))
    for expr in expressions:
        m = fun.matchCl(rehost,expr) 
        if m:
            host = m.groups()[0]
            print 'get_matching_devices(%s): getting %s devices ...'%(expr,host)
            odb = PyTango.Database(*host.split(':'))
            all_devs.extend('%s/%s'%(host,d) for d in odb.get_device_name('*','*'))
    expressions = map(fun.toRegexp,fun.toList(expressions))
    result = filter(lambda d: any(fun.matchCl(e,d,terminate=True) for e in expressions),all_devs)
    return result[:limit] if limit else result
        
find_devices = get_matching_devices
    
def get_matching_attributes(expressions,limit=0):
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
            if '/' not in e:
                host,dev,attr = def_host,e.rsplit('/',1)[0],'state'
                #raise Exception('Expression must match domain/family/member/attribute shape!: %s'%e)
            else:
                host,dev,attr = def_host,e.rsplit('/',1)[0],e.rsplit('/',1)[1]
        else:
            host,dev,attr = [d[k] for k in ('host','device','attribute') for d in (match.groupdict(),)]
            host,attr = host or def_host,attr or 'state'
        #print '%s => %s: %s /%s' % (e,host,dev,attr)
        for d in get_matching_devices(dev,exported=True):
            if fun.matchCl(attr,'state',terminate=True):
                attrs.append(d+'/State')
            if attr.lower().strip() != 'state':
                try: 
                    ats = get_device_attributes(d,[attr])
                    attrs.extend([d+'/'+a for a in ats])
                    if limit and len(attrs)>limit: break
                except: 
                    print 'Unable to get attributes for %s'%d
    result = list(set(attrs))
    return result[:limit] if limit else result
                    
find_attributes = get_matching_attributes
    
def get_all_models(expressions,limit=1000):
    ''' 
    Customization of get_matching_attributes to be usable in Taurus widgets.
    It returns all the available Tango attributes (exported!) matching any of a list of regular expressions.
    '''
    if isinstance(expressions,str): #evaluating expressions ....
        if any(re.match(s,expressions) for s in ('\{.*\}','\(.*\)','\[.*\]')): expressions = list(eval(expressions))
        else: expressions = expressions.split(',')
    else:
        try: from PyQt4 import Qt
        except: USE_TAU = False
        if isinstance(expressions,(USE_TAU and Qt.QStringList or list,list,tuple,dict)):
            expressions = list(str(e) for e in expressions)
    
    print 'In get_all_models(%s:"%s") ...' % (type(expressions),expressions)
    db = get_database()
    if 'SimulationDatabase' in str(type(db)): #used by TauWidgets displayable in QtDesigner
      return expressions
    return get_matching_attributes(expressions,limit)
              
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
    return fun.first((vals[k],rates[k]) for k,r in rates.items() if r == max(rates.values()))
 

########################################################################################
            
########################################################################################
## Methods for checking device/attribute availability
   
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
## Methods usable from within DeviceImpl instances

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
    
def get_internal_devices():
    """ Gets all devices declared in the current Tango server """
    dct = fandango.CaselessDict()
    U = PyTango.Util.instance()
    for klass in U.get_class_list():
        for dev in U.get_device_list_by_class(klass.get_name()):
            dct[dev.get_name().lower()]=dev
    return dct
    
def read_internal_attribute(device,attribute):
    """
    device must be a DevImpl object or string, attribute must be an string
    the method will return a fakeAttributeValue object
    """
    print 'read_internal_attribute(%s,%s)'%(device,attribute)
    import dynamic
    if fun.isString(device):
        device = get_internal_devices().get(device,PyTango.DeviceProxy(device))
    attr = attribute if isinstance(attribute,fakeAttributeValue) else fakeAttributeValue(name=attribute,parent=device)
    isProxy, isDyn = isinstance(attr.parent,PyTango.DeviceProxy),hasattr(attr.parent,'read_dyn_attr')
    aname = attr.name.lower()
    if aname=='state': 
        if isProxy: attr.set_value(attr.parent.state())
        elif hasattr(attr.parent,'last_state'): attr.set_value(attr.parent.last_state)
        else: attr.set_value(attr.parent.get_state())
        print '%s = %s' % (attr.name,attr.value)
        attr.error = ''
    else: 
        if isProxy:
            print ('fandango.update_external_attributes(): calling DeviceProxy(%s).read_attribute(%s)'%(attr.device,attr.name))
            val = attr.parent.read_attribute(attr.name)
            attr.set_value_date_quality(val.value,val.date,val.quality)
        else:
            allow_method,read_method = None,None
            for s in dir(attr.parent):
                if s.lower()=='is_%s_allowed'%aname: allow_method = s
                if s.lower()=='read_%s'%aname: read_method = s
            print ('fandango.update_external_attributes(): calling %s.is_%s_allowed()'%(attr.device,attr.name))
            is_allowed = (not allow_method) or getattr(attr.parent,allow_method)(PyTango.AttReqType.READ_REQ)
            if not is_allowed:
                attr.throw_exception('%s.read_%s method is not allowed!!!'%(device,aname))
            elif not read_method:
                if isDyn: 
                    print ('fandango.update_external_attributes(): calling %s(%s).read_dyn_attr(%s)'%(attr.parent.myClass,attr.device,attr.name))
                    if not attr.parent.myClass:
                        attr.throw_exception('\t%s is a dynamic device not initialized yet.'%attr.device)
                    else:
                        #Returning valid values
                        try:
                            attr.parent.myClass.DynDev = attr.parent
                            if dynamic.USE_STATIC_METHODS: attr.parent.read_dyn_attr(attr.parent,attr)
                            else: attr.parent.read_dyn_attr(attr)
                            print '%s = %s' % (attr.name,attr.value)
                            attr.error = ''
                        except:
                            attr.throw_exception()
                else:
                    attr.throw_exception('%s.read_%s method not found!!!'%(device,aname,[d for d in dir(attr.parent)]))
            else: 
                #Returning valid values
                msg = ('Dev4Tango.update_external_attributes(): calling %s.read_%s()'%(attr.device,aname))
                print msg
                try:
                    getattr(attr.parent,read_method)(attr)
                    print '%s = %s' % (attr.name,attr.value)
                    attr.error = ''
                except:
                    attr.throw_exception()
    return attr

def get_polled_attrs(device,others=None):
    """ 
    @TODO: Tango8 has its own get_polled_attr method; check for incompatibilities
    if a device is passed, it returns the polled_attr property as a dictionary
    if a list of values is passed, it converts to dictionary
    others argument allows to get extra property values in a single DB call 
    """
    if fun.isSequence(device):
        return dict(zip(map(str.lower,device[::2]),map(float,device[1::2])))
    elif isinstance(device,PyTango.DeviceProxy):
        attrs = device.get_attribute_list()
        periods = [(a.lower(),int(dp.get_attribute_poll_period(a))) for a in attrs]
        return dict((a,p) for a,p in periods if p)
    else:
        others = others or []
        if isinstance(device,PyTango.DeviceImpl):
            db = PyTango.Util.instance().get_database()
            #polled_attrs = {}
            #for st in self.get_admin_device().DevPollStatus(device.get_name()):
                #lines = st.split('\n')
                #try: polled_attrs[lines[0].split()[-1]]=lines[1].split()[-1]
                #except: pass
            #return polled_attrs
            device = device.get_name()
        else:
            db = fandango.get_database()
        props = db.get_device_property(device,['polled_attr']+others)
        d = get_polled_attrs(props.pop('polled_attr'))
        if others: d.update(props)
        return d

########################################################################################
## A useful fake attribute value and event class
    
class fakeAttributeValue(object):
    """ This class simulates a modifiable AttributeValue object (not available in PyTango)
    :param parent: Apart of common Attribute arguments, parent will be used to keep a proxy to the parent object (a DeviceProxy or DeviceImpl) 
    """
    def __init__(self,name,value=None,time_=0.,quality=PyTango.AttrQuality.ATTR_VALID,dim_x=1,dim_y=1,parent=None,device=''):
        self.name=name
        self.device=device or (self.name.split('/')[-1] if '/' in self.name else '')
        self.set_value(value,dim_x,dim_y)
        self.set_date(time_ or time.time())
        self.write_value = None
        self.quality=quality
        self.parent=parent
        self.error = ''
        
    def get_name(self): return self.name
    def get_value(self): return self.value
    def get_date(self): return self.time
    def get_quality(self): return self.quality
    
    def read(self,cache=True):
        #Method to emulate AttributeProxy returning an AttributeValue
        print 'fakeAttributeValue(%s).read(%s)'%(self.name,cache)
        if not cache:
            return read_internal_attribute(self.parent,self) #it's important to pass self as argument so values will be kept
        return self 
    
    def throw_exception(self,msg=''):
        self.error = msg or traceback.format_exc()
        print 'fakeAttributeValue(%s).throw_exception(%s)'%(self.name,self.error)
        #event_type = fakeEventType.lookup['Error']
        self.set_value(None)
        self.set_quality(PyTango.AttrQuality.ATTR_INVALID)
        raise Exception(self.error)
    
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
                devklass,attrklass = (TAU.Device,TAU.Attribute) if USE_TAU else (PyTango.DeviceProxy,PyTango.AttributeProxy)
                dev = (attrklass if str(dev_name).count('/')==(4 if ':' in dev_name else 3) else devklass)(dev_name)
            except Exception,e:
                print('ProxiesDict: %s doesnt exist!'%dev_name)
                print traceback.format_exc()
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