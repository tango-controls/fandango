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
provides tango utilities for fandango, like database search methods and emulated Attribute Event/Value types

This module is a light-weight set of utilities for PyTango.
Classes dedicated for device management will go to fandango.device
Methods for Astor-like management will go to fandango.servers
"""

#python imports
import time,re,os,traceback

#pytango imports
import PyTango
from PyTango import AttrQuality,EventType,DevState,AttrDataFormat,AttrWriteType,CmdArgType
if 'Device_4Impl' not in dir(PyTango):
    PyTango.Device_4Impl = PyTango.Device_3Impl

import fandango
import objects
import threading
from fandango.functional import *
from dicts import CaselessDefaultDict,CaselessDict
from objects import Object,Struct
from log import Logger,except2str,printf

__test__ = {}

#taurus imports, here USE_TAU is defined for all fandango
global TAU,USE_TAU,TAU_LOGGER
TAU,USE_TAU = None,False
def loadTaurus():
    print '#'*80
    print '%s fandango.tango.loadTaurus()'%time.ctime()
    global TAU,USE_TAU,TAU_LOGGER
    try:
        assert str(os.getenv('USE_TAU')).strip().lower() not in 'no,false,0'
        import taurus
        TAU = taurus
        USE_TAU=True
        TAU_LOGGER = taurus.core.util.Logger
        """USE_TAU will be used to choose between taurus.Device and PyTango.DeviceProxy"""
    except:
        print 'fandango.tango: USE_TAU disabled'
        TAU = None
        USE_TAU=False
        TAU_LOGGER = Logger
    return bool(TAU)

####################################################################################################################
def TGet(*args):
    """ 
    Universal fandango helper, it will return a matching Tango object depending on the arguments passed
    Objects are: database (), server (*/*), attribute ((:/)?*/*/*/*), device (*)
    """
    if not args:
        return get_database()
    arg0 = args[0]
    if arg0.count('/')==1:
        return fandango.servers.ServersDict(arg0)
    if arg0.count('/')>(2+(':' in arg0)):
        return sorted(get_matching_attributes(arg0)) if isRegexp(arg0,WILDCARDS+' ') else check_attribute(arg0,brief=True)
    else:
        return sorted(get_matching_devices(arg0)) if isRegexp(arg0,WILDCARDS+' ') else get_device(arg0)
        
__test__['fandango.tango.TGet'] = ('sys/database/2',['sys/database/2'],{})
        
####################################################################################################################

TANGO_STATES = \
  'ON OFF CLOSE OPEN INSERT EXTRACT MOVING STANDBY FAULT INIT RUNNING ALARM DISABLE UNKNOWN'.split()
TANGO_COLORS = \
  'Lime White White Lime White Lime LightBlue Yellow Red Brown LightBlue Orange Magenta Grey'.split()

TANGO_STATE_COLORS = dict(zip(TANGO_STATES,TANGO_COLORS))

####################################################################################################################
##@name Access Tango Devices and Database

##TangoDatabase singletone
global TangoDatabase,TangoDevice,TangoProxies
TangoDatabase,TangoDevice,TangoProxies = None,None,None

def get_tango_host(dev_name='',use_db=False):
    """
    If device is a tango model, it will extract the host from the model URL
    If devicesis none, then environment variable or PyTango.Database are used to extract the host
    If TANGO_HOST is not defined it will always fallback to PyTango.Database()
    """
    try:
        if dev_name:
            if isString(dev_name):
              m  = matchCl(rehost,dev_name)
            else: 
              m,use_db = None,dev_name
            return m.groups()[0] if m else get_tango_host(use_db=use_db)
        elif use_db:
            use_db = use_db if hasattr(use_db,'get_db_host') else get_database()
            host,port = use_db.get_db_host(),int(use_db.get_db_port())
            if matchCl('.*[a-z].*',host.lower()):
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
    @TODO: host/port is checked only at first creation, once initialized you can't change HOST
    """
    global TangoDatabase
    global TAU,USE_TAU
    if host in (True,False): use_tau,host,port = host,'','' #For backwards compatibility
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
            #TangoDatabase.check_tango_host(TangoDatabase.get_db_host()+':'+TangoDatabase.get_db_port())
            #TangoDatabase.get_timeout_millis()
            print time.time()-t
            return TangoDatabase 
        except:
            #traceback.print_exc()
            pass #defaulting to Taurus/PyTango
    try: 
        if use_tau and not TAU: TAU = loadTaurus()
        db = (use_tau and TAU and TAU.Database(*args)) or PyTango.Database(*args)
        if not args: TangoDatabase = db
        return db
    except:
        print traceback.format_exc()
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
    elif isinstance(dev,PyTango.DeviceProxy) or (use_tau and TAU and isinstance(dev,TAU.core.tango.TangoDevice)):
        return dev
    else:
        return None

def get_database_device(use_tau=False,db=None): 
    global TangoDevice
    if db is None and TangoDevice is not None:
      td = TangoDevice
    else:
        try:
           dev_name = (db or get_database(use_tau=use_tau)).dev_name()
           dev_name = get_tango_host(use_db=db)+'/'+dev_name if db else dev_name
           td = get_device(dev_name,use_tau=use_tau)
        except: 
           traceback.print_exc()
        if db is None: 
          TangoDevice = td
    return td

def add_new_device(server,klass,device):
    for c in (server+klass+device):
      if re.match('[^a-zA-Z0-9\-\/_]',c):
        raise Exception,"'%s' Character Not Allowed! (only a-z,A-Z,0-9,/,-,_)"%c
    dev_info = PyTango.DbDevInfo()
    dev_info.name = device
    dev_info.klass = klass
    dev_info.server = server
    get_database().add_device(dev_info)    
    
def get_device_info(dev,db=None):
    """
    This method provides an alternative to DeviceProxy.info() for those devices that are not running
    """
    #vals = PyTango.DeviceProxy('sys/database/2').DbGetDeviceInfo(dev)
    vals = None
    if ':' in dev:
      model = fandango.Struct(parse_tango_model(dev))
      db = get_database(model.host,model.port)
      dev = model.device
    try:
      dd = get_database_device(db=db)
      vals = dd.DbGetDeviceInfo(dev)
      di = Struct([(k,v) for k,v in zip(('name','ior','level','server','host','started','stopped'),vals[1])])
      di.exported,di.PID = vals[0]
      di.dev_class = dd.DbGetClassForDevice(dev)
      return di
    except:
      raise Exception('get_device_info(%s,%s,%s): %s'%(
        dev,db,vals,traceback.format_exc()))

def get_device_host(dev):
    """
    Asks the Database device server about the host of this device 
    """
    return get_device_info(dev).host

def get_device_started(target):
    """ Returns device started time """
    return get_database_device().DbGetDeviceInfo(target)[-1][5]
  
def get_device_for_alias(alias):
    """ returns the device name for a given alias """
    try: return get_database().get_device_alias(alias)
    except Exception,e:
        if 'no device found' in str(e).lower(): return None
        return None #raise e

def get_alias_for_device(dev):
    """ return alias for this device """
    try: return get_database().get_alias(dev) #.get_database_device().DbGetDeviceAlias(dev)
    except Exception,e:
        if 'no alias found' in str(e).lower(): return None
        return None #raise e

def get_alias_dict(exp='*'):
    """
    returns an {alias:device} dictionary with all matching alias from Tango DB
    :param exp:
    """
    tango = get_database()
    return dict((k,tango.get_device_alias(k)) for k in tango.get_device_alias_list(exp))

def get_real_name(dev,attr=None):
    """
    It translate any device/attribute string by name/alias/label
    
    :param device: Expected format is [host:port/][device][/attribute]; where device can be either a/b/c or alias
    :param attr: optional, when passed it will be regexp matched against attributes/labels
    """
    if isString(dev):
        if attr is None and dev.count('/') in (1,4 if ':' in dev else 3): 
          dev,attr = dev.rsplit('/',1)
        if '/' not in dev: 
          dev = get_device_for_alias(dev)
        if attr is None: return dev
    for a in get_device_attributes(dev):
        if matchCl(attr,a): return (dev+'/'+a)
        if matchCl(attr,get_attribute_label(dev+'/'+a)): return (dev+'/'+a)
    return None

def get_full_name(model):
    """ Returns full schema name as needed by HDB++ api
    """
    if ':' not in model:
      model = get_tango_host()+'/'+model
    if not model.startswith('tango://'):
      model = 'tango://'+model
    return model

def get_device_commands(dev):
    """
    returns a list of device command names
    """
    return [c.cmd_name for c in get_device(dev).command_list_query()]

def get_device_attributes(dev,expressions='*'):
    """ Given a device name it returns the attributes matching any of the given expressions """
    expressions = map(toRegexp,toList(expressions))
    al = (get_device(dev) if isString(dev) else dev).get_attribute_list()
    result = [a for a in al for expr in expressions if matchCl(expr,a,terminate=True)]
    return result
        
def get_device_labels(target,filters='*',brief=True):
    """
    Returns an {attr:label} dict for all attributes of this device 
    Filters will be a regular expression to apply to attr or label.
    If brief is True (default) only those attributes with label are returned.
    This method works offline, does not need device to be running
    """
    labels = {}
    if isString(target): d = get_device(target)
    else: d,target = target,target.name()
    db = get_database()
    attrlist = db.get_device_attribute_list(target,filters) if brief and hasattr(db,'get_device_attribute_list') else d.get_attribute_list()
    for a in attrlist:
        l = get_attribute_label(target+'/'+a,use_db=True) if brief else d.get_attribute_config(a).label
        if (not filters or any(map(matchCl,(filters,filters),(a,l)))) and (not brief or l!=a): 
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
    return dict((t+'/'+a,l) for t in devs for a,l in get_device_labels(t,attribute).items() if check_device(t))

def get_attribute_info(device,attribute):
    """
    This method returns attribute info in the attr_list format
    It parses values returned by PyTango.DeviceProxy(device).get_attribute_config(attribute)
    return format:
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ_WRITE, 2],
            {
                'unit':"mbar",
                'format':"%4d",
             }],
    """
    if isString(device): device = get_device(device)
    ai = device.get_attribute_config(attribute)
    types = [PyTango.CmdArgType.values.get(ai.data_type),ai.data_format,ai.writable]
    if ai.max_dim_x>1: types.append(ai.max_dim_x)
    if ai.max_dim_y>0: types.append(ai.max_dim_y)
    formats = dict((k,getattr(ai,k)) 
        for k,v in (('label',''),('unit','No unit'),('format',''))
        if getattr(ai,k)!=v)
    return [types,formats]
  
def get_attribute_config(target):
    d,a = target.rsplit('/',1)
    return get_device(d).get_attribute_config(a)
  
def get_attribute_events(target,polled=True,throw=False):
    try:
      d,a = target.rsplit('/',1)
      dp = get_device(d)
      polling = dp.get_attribute_poll_period(a)
      if polled and not polling:
        return None
      aei = dp.get_attribute_config(a).events
      r = {'polling':polling}
      for k,t in (
        ('arch_event',('archive_abs_change','archive_rel_change','archive_period')),
        ('ch_event',('abs_change','rel_change')),
        ('per_event',('period',))):
        r[k],v = [None]*len(t),None
        for i,p in enumerate(t):
          try: 
            v = str2float(getattr(getattr(aei,k),p))
            r[k][i] = v
          except: pass #print(k,i,p,v)
        if not any(r[k]): r.pop(k)
      return r
    except Exception,e:
      if throw: raise e
      return None

def get_attribute_label(target,use_db=True):
    dev,attr = target.rsplit('/',1)
    if not use_db: #using AttributeProxy
        if attr.lower() in ('state','status'): 
            return attr
        cf = get_attribute_config(target)
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
  
def get_class_property(klass,property,db=None):
    """
    It returns class property value or just first item if value list has lenght==1
    """
    prop = (db or get_database()).get_class_property(klass,[property])[property]
    return prop if len(prop)!=1 else prop[0]

def put_class_property(klass,property,value=None,db=None):
    """
    Two syntax are possible:
     - put_class_property(class,{property:value})
     - put_class_property(class,property,value)
    """
    if not isMapping(property):
        if isSequence(value) and not isinstance(value,list):
            value = list(value)
        property = {property:value}
    else:
        for p,v in property.items():          
            if isSequence(v):
                if len(v)==1:
                    property[p] = v[0]
                elif not isinstance(value,list):
                    property[p] = list(v)
    return (db or get_database()).put_class_property(klass,property)
            
def get_device_property(device,property,db=None):
    """
    It returns device property value or just first item if value list has lenght==1
    """
    prop = (db or get_database()).get_device_property(device,[property])[property]
    return prop if len(prop)!=1 else prop[0]

def put_device_property(device,property,value=None,db=None):
    """
    Two syntax are possible:
     - put_device_property(device,{property:value})
     - put_device_property(device,property,value)
    """
    if not isMapping(property):
        if isSequence(value) and not isinstance(value,list):
            value = list(value)
        property = {property:value}
    else:
        for p,v in property.items():          
            if isSequence(v):
                if len(v)==1:
                    property[p] = v[0]
                elif not isinstance(value,list):
                    property[p] = list(v)
    return (db or get_database()).put_device_property(device,property)
            
def get_devices_properties(device_expr,properties,hosts=[],port=10000):
    """
    get_devices_properties('*alarms*',props,hosts=[get_bl_host(i) for i in bls])
    props must be an string as passed to Database.get_device_property(); regexp are not enabled!
    get_matching_device_properties enhanced with multi-host support
    @TODO: Compare performance of this method with get_matching_device_properties
    """
    expr = device_expr
    if not isSequence(properties): properties = [properties]
    get_devs = lambda db, reg : [d for d in db.get_device_name('*','*') if not d.startswith('dserver') and matchCl(reg,d)]
    if hosts: tango_dbs = dict(('%s:%s'%(h,port),PyTango.Database(h,port)) for h in hosts)
    else: tango_dbs = {get_tango_host():get_database()}
    return dict(('/'.join((host,d) if hosts else (d,)),db.get_device_property(d,properties))
                 for host,db in tango_dbs.items() for d in get_devs(db,expr))
    
    
def get_matching_device_properties(devs,props,hosts=[],exclude='*dserver*',port=10000,trace=False):
    """
    get_matching_device_properties enhanced with multi-host support
    @props: regexp are enabled!
    get_devices_properties('*alarms*',props,hosts=[get_bl_host(i) for i in bls])
    @TODO: Compare performance of this method with get_devices_properties
    """    
    db = get_database()
    result = {}
    if not isSequence(devs): devs = [devs]
    if not isSequence(props): props = [props]
    if hosts:
        hosts = [h if ':' in h else '%s:%s'%(h,port) for h in hosts]
    else:
        hosts = set(get_tango_host(d) for d in devs)

    result = {}
    for h in hosts:
        result[h] = {}
        db = get_database(h)
        exps  = [h+'/'+e if ':' not in e else e for e in devs]
        if trace: print(exps)
        hdevs = [d.replace(h+'/','') for d in get_matching_devices(exps,fullname=False)]
        if trace: print('%s: %s vs %s'%(h,hdevs,props))
        for d in hdevs:
            if exclude and matchCl(exclude,d): continue
            dprops = [p for p in db.get_device_property_list(d,'*') if matchAny(props,p)]
            if not dprops: continue
            if trace: print(d,dprops)
            vals = db.get_device_property(d,dprops)
            vals = dict((k,list(v) if isSequence(v) else v) for k,v in vals.items())
            if len(hosts)==1 and len(hdevs)==1:
                return vals
            else: 
                result[h][d] = vals
        if len(hosts)==1: 
            return result[h]
    return result
    
def property_undo(dev,prop,epoch):
    db = get_database()
    his = db.get_device_property_history(dev,prop)
    valids = [h for h in his if str2time(h.get_date())<epoch]
    news = [h for h in his if str2time(h.get_date())>epoch]
    if valids and news:
        print('Restoring property %s/%s to %s'%(dev,prop,valids[-1].get_date()))
        db.put_device_property(dev,{prop:valids[-1].get_value().value_string})
    elif not valids:print('No property values found for %s/%s before %s'%(dev,prop,time2str(epoch)))
    elif not news: print('Property %s/%s not modified after %s'%(dev,prop,time2str(epoch)))
    
def get_property_history(dev,prop):
    db = get_database()
    his = db.get_device_property_history(dev,prop)
    return [(str2time(h.get_date()),h.get_value()) for h in his]    

###############################################################################
# Property extensions

def get_extension_arg(x): 
    return x.split(':',1)[-1].split('#')[0]

def _copy_extension(prop,row,db=None): 
    db = db or get_database()
    return db.get_device_property(get_extension_arg(row),[prop])[prop]

def _file_extension(prop,row,db=None):
    try:
        f = open(get_extension_arg(row))
        r = f.readlines()
        f.close()
        return r
    except:
        traceback.print_exc()
        return []

EXTENSIONS = {'@COPY:':_copy_extension,'@FILE:':_file_extension}

def check_property_extensions(prop,value,db=None,extensions=EXTENSIONS,filters=[]):
    db = db or get_database()
    #print(prop in DynamicDSClass.device_property_list,fandango.isSequence(value),any(str(s).startswith(e) for e in DynamicDS._EXTENSIONS for s in value))
    if (not filters or prop in filters) and fandango.isSequence(value) and any(str(s).startswith(e) for e in extensions for s in value):
        parsed,get_arg = [],(lambda x:x.split(':',1)[-1].split('#')[0])
        for v in value:
            try:
                #if v.startswith('@COPY:'): parsed.extend(DynamicDS._copy_extension(prop,v))
                #elif v.startswith('@FILE:'): parsed.extend(DynamicDS._file_extension(prop,v))
                ext,f = first([(e,f) for e,f in extensions.items() if v.startswith(e)] or [(None,None)])
                if ext: parsed.extend(f(prop,v))
                else: parsed.append(v)
            except: print('check_property_extensions(%s,%s): %s'%(prop,value,traceback.format_exc()))
        return parsed
    return value

####################################################################################################################
##@name Methods for searching the database with regular expressions
#@{

#Regular Expressions
metachars = re.compile('([.][*])|([.][^*])|([$^+\-?{}\[\]|()])')
#alnum = '[a-zA-Z_\*][a-zA-Z0-9-_\*]*' #[a-zA-Z0-9-_]+ #Added wildcards
alnum = '(?:[a-zA-Z0-9-_\*]|(?:\.\*))(?:[a-zA-Z0-9-_\*]|(?:\.\*))*'
no_alnum = '[^a-zA-Z0-9-_]'
no_quotes = '(?:^|$|[^\'"a-zA-Z0-9_\./])'
rehost = '(?:(?P<host>'+alnum+'(?:\.'+alnum+')?'+'(?:\.'+alnum+')?'+'(?:\.'+alnum+')?'+'[\:][0-9]+)(?:/))' #(?:'+alnum+':[0-9]+/)?
redev = '(?P<device>'+'(?:'+'/'.join([alnum]*3)+'))' #It matches a device name
reattr = '(?:/(?P<attribute>'+alnum+')(?:(?:\\.)(?P<what>quality|time|value|exception|history))?)' #Matches attribute and extension
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
        
def get_model_name(model):
    if isString(model): 
        m = searchCl(retango,str(model).lower())
        return m.group() if m else str(model).lower()
    try: 
        model = model.getFullName()
    except: 
        try:
            model = model.getModelName()
        except:
            print traceback.format_exc()
    return str(model).lower()
        
def parse_tango_model(name,use_tau=False,use_host=False):
    """
    {'attributename': 'state',
    'attribute': 'state',
    'devicename': 'bo01/vc/ipct-01', #Always short name
    'device': 'cts:10000/bo01/vc/ipct-01', #Will contain host if use_host or host!=TANGO_HOST
    'host': 'cts',
    'port': '10000',
    'scheme': 'tango'}
    """
    values = {'scheme':'tango'}
    values['host'],values['port'] = defhost = get_tango_host().split(':',1)
    try:
        if not use_tau or not TAU: raise Exception('NotTau')
        from taurus.core import tango as tctango
        from taurus.core import AttributeNameValidator,DeviceNameValidator
        validator = {tctango.TangoDevice:DeviceNameValidator,tctango.TangoAttribute:AttributeNameValidator}
        values.update((k,v) for k,v in validator[tctango.TangoFactory().findObjectClass(name)]().getParams(name).items() if v)
    except:
        name = str(name).replace('tango://','')
        m = re.match(fandango.tango.retango,name)
        if m:
            gd = m.groupdict()
            values['device'] = '/'.join([s for s in gd['device'].split('/') if ':' not in s])
            if gd.get('attribute'): values['attribute'] = gd['attribute']
            if gd.get('host'): values['host'],values['port'] = gd['host'].split(':',1)
    if 'device' not in values: 
        return None
    else:
        values['devicename'] = values['device']
        values['model'] = '%s:%s/%s'%(values['host'],values['port'],values['device'])
        if use_host or tuple(defhost) != (values['host'],values['port']): 
            values['device'] = values['model']
        if 'attribute' in values: 
            values['attributename'] = values['attribute']
            values['model'] = values['model']+'/'+values['attribute']
    return values

TANGO_KEEPTIME = 60 #This variable controls how often the Tango Database will be queried

class get_all_devices(objects.SingletonMap):
    _keeptime = TANGO_KEEPTIME
    def __init__(self,exported=False,keeptime=None,host=''):
        self._all_devs = []
        self._last_call = 0
        self._exported = exported
        self._host = host and get_tango_host(host)
        if keeptime: self.set_keeptime(keeptime)
    @classmethod
    def set_keeptime(klass,keeptime):
        klass._keeptime = max(keeptime,60) #Only 1 query/minute to DB allowed
    def get_all_devs(self):
        now = time.time()
        if not self._all_devs or now>(self._last_call+self._keeptime):
            #print 'updating all_devs ...............................'
            db = get_database(self._host)
            self._all_devs = sorted(map(str.lower,
                (db.get_device_exported('*') if self._exported 
                 else db.get_device_name('*','*'))))
            self._last_call = now
        return self._all_devs
    def __new__(cls,*p,**k):
        instance = objects.SingletonMap.__new__(cls,*p,**k)
        return instance.get_all_devs()
    
def get_class_devices(klass,db=None):
    """ Returns all registered devices for a given class 
    """
    if not db:
        db = get_database()
    if isString(db): 
        db = get_database(db)
    return sorted(str(d).lower() for d in db.get_device_name('*',klass))
    
    
def get_matching_devices(expressions,limit=0,exported=False,fullname=False,trace=False):
    """ 
    Searches for devices matching expressions, if exported is True only running devices are returned 
    Tango host will be included in the matched name if fullname is True
    """
    if not isSequence(expressions): expressions = [expressions]
    defhost = get_tango_host()
    hosts = list(set((m.groups()[0] if m else None) for m in (matchCl(rehost,e) for e in expressions)))
    fullname = fullname or ':' in str(expressions) or len(hosts)>1 or hosts[0] not in (defhost,None) #Dont count slashes, as regexps may be complex
    all_devs = []
    if trace: print(hosts,fullname)
    for host in hosts:
        if host in (None,defhost):
            db_devs = get_all_devices(exported)
        else:
            print('get_matching_devices(*%s)'%host)
            odb = PyTango.Database(*host.split(':'))
            db_devs = odb.get_device_exported('*') if exported else odb.get_device_name('*','*')
        prefix = '%s/'%(host or defhost)
        all_devs.extend(prefix+d for d in db_devs)
        
    expressions = map(toRegexp,toList(expressions))
    if trace: print(expressions)
    if not fullname: all_devs = [r.split('/',1)[-1] if matchCl(rehost,r) else r for r in all_devs]
    condition = lambda d: any(matchCl("(%s/)?(%s)"%(defhost,e),d,terminate=True) for e in expressions)
    result = sorted(filter(condition,all_devs))
    return sorted(result[:limit] if limit else result)
  
def get_matching_servers(expressions,tango_host='',exported=False):
    """
    Return all servers in the given tango tango_host matching the given expressions.
    :param exported: whether servers should be running or not
    """
    expressions = toSequence(expressions)
    servers = get_database(tango_host).get_server_list()
    servers = sorted(set(s for s in servers if matchAny(expressions,s)))
    if exported:
      exported = get_all_devices(exported=True,host=tango_host)
      servers = [s for s in servers if ('dserver/'+s).lower() in exported]
    return sorted(servers)
    
def find_devices(*args,**kwargs):
    #A get_matching_devices() alias, just for backwards compatibility
    return get_matching_devices(*args,**kwargs) 
    
def get_matching_attributes(expressions,limit=0,fullname=None,trace=False):
    """ 
    Returns all matching device/attribute pairs. 
    regexp only allowed in attribute names
    :param expressions: a list of expressions like [domain_wild/family_wild/member_wild/attribute_regexp] 
    """
    attrs = []
    def_host = get_tango_host()
    matches = []
    if not isSequence(expressions): expressions = [expressions]
    fullname = any(matchCl(rehost,e) for e in expressions)
    
    for e in expressions:
        match = matchCl(retango,e,terminate=True)
        if not match:
            if '/' not in e:
                host,dev,attr = def_host,e.rsplit('/',1)[0],'state'
                #raise Exception('Expression must match domain/family/member/attribute shape!: %s'%e)
            else:
                host,dev,attr = def_host,e.rsplit('/',1)[0],e.rsplit('/',1)[1]
        else:
            host,dev,attr = [d[k] for k in ('host','device','attribute') for d in (match.groupdict(),)]
            host,attr = host or def_host,attr or 'state'
        if trace: print('get_matching_attributes(%s): match:%s,host:%s,dev:%s,attr:%s'%(e,bool(match),host,dev,attr))
        matches.append((host,dev,attr))
    
    fullname = fullname or any(m[0]!=def_host for m in matches)

    for host,dev,attr in matches:

        if fullname and host not in dev:
            dev = host+'/'+dev
            
        for d in get_matching_devices(dev,exported=True,fullname=fullname):
            if matchCl(attr,'state',terminate=True):
                attrs.append(d+'/State')
            if attr.lower().strip() != 'state':
                try: 
                    ats = sorted(get_device_attributes(d,[attr]),key=str.lower)
                    attrs.extend([d+'/'+a for a in ats])
                    if limit and len(attrs)>limit: break
                except: 
                    print 'Unable to get attributes for %s'%d
                    print traceback.format_exc()
                    
    result = sorted(set(attrs))
    return result[:limit] if limit else result
                    
def find_attributes(*args,**kwargs):
    #A get_matching_attributes() alias, just for backwards compatibility
    return get_matching_attributes(*args,**kwargs) 
    
def get_all_models(expressions,limit=1000):
    ''' 
    Customization of get_matching_attributes to be usable in Taurus widgets.
    It returns all the available Tango attributes (exported!) matching any of a list of regular expressions.
    '''
    if isinstance(expressions,str): #evaluating expressions ....
        if any(re.match(s,expressions) for s in ('\{.*\}','\(.*\)','\[.*\]')): expressions = list(eval(expressions))
        else: expressions = expressions.split(',')
    else:
        types = [list,tuple,dict]
        try: 
            from PyQt4 import Qt
            types.append(Qt.QStringList)
        except: pass
        if isinstance(expressions,types):
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
    
def get_domain(model):
    if model.count('/') in (2,3): return model.split['/'][0]
    else: return ''
    
def get_family(model):
    if model.count('/') in (2,3): return model.split['/'][1]
    else: return ''
    
def get_member(model):
    if model.count('/') in (2,3): return model.split['/'][2]
    else: return ''
    
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
## Methods to export device/attributes/properties to dictionaries

def export_attribute_to_dict(model,attribute=None,value=None,keep=False):
    """
    get attribute config, format and value from Tango and return it as a dictionary:
    
    :param model: can be a full tango model, a device name or a device proxy
    
    keys: min_alarm,name,data_type,format,max_alarm,ch_event,data_format,value,
          label,writable,device,polling,alarms,arch_event,unit
    """
    attr,proxy = Struct(),None
    if not isString(model):
        model,proxy = model.name(),model
      
    model = parse_tango_model(model)
    attr.device = model['device']
    proxy = proxy or get_device(attr.device,keep=keep)
    attr.database = '%s:%s'%(model['host'],model['port'])
    attr.name = model.get('attribute',None) or attribute or 'state'
    attr.model = '/'.join((attr.database,attr.device,attr.name))
    attr.color = 'Lime'
    attr.time = 0
    
    def vrepr(v):
      try: return str(attr.format)%(v)
      except: return str(v)
    def cleandict(d):
      for k,v in d.items():
        if v in ('Not specified','No %s'%k):
          d[k] = ''
      return d

    try:
        v = value or check_attribute(attr.database+'/'+attr.device+'/'+attr.name)

        if v and 'DevFailed' not in str(v):
            ac = proxy.get_attribute_config(attr.name)
            attr.description = ac.description if ac.description!='No description' else ''
            attr.data_format = str(ac.data_format)
            attr.data_type = str(PyTango.CmdArgType.values[ac.data_type])
            attr.writable = str(ac.writable)
            attr.label,attr.min_alarm,attr.max_alarm = ac.label,ac.min_alarm,ac.max_alarm
            attr.unit,attr.format = ac.unit,ac.format
            attr.standard_unit,attr.display_unit = ac.standard_unit,ac.display_unit
            attr.ch_event = fandango.obj2dict(ac.events.ch_event)
            attr.arch_event = fandango.obj2dict(ac.events.arch_event)
            attr.alarms = fandango.obj2dict(ac.alarms)
            attr.quality = str(v.quality)
            attr.time = ctime2time(v.time)
              
            if attr.data_format!='SCALAR': 
                attr.value = list(v.value if v.value is not None and v.dim_x else [])
                sep = '\n' if attr.data_type == 'DevString' else ','
                svalue = map(vrepr,attr.value)
                attr.string = sep.join(svalue)
                if 'numpy' in str(type(v.value)): 
                  attr.value = map(fandango.str2type,svalue)
            else:
              if attr.data_type in ('DevState','DevBoolean'):
                  attr.value = int(v.value)
                  attr.string = str(v.value)
              else:
                  attr.value = v.value
                  attr.string = vrepr(v.value)
            if attr.unit.strip() not in ('','No unit'):
              attr.string += ' %s'%(attr.unit)
            attr.polling = proxy.get_attribute_poll_period(attr.name)
        else: 
            print((attr.device,attr.name,'unreadable!'))
            attr.value = None
            attr.string = str(v)
            
        if attr.value is None:
            attr.data_type = None
            attr.color = TANGO_STATE_COLORS['UNKNOWN']
        elif attr.data_type == 'DevState':
            attr.color = TANGO_STATE_COLORS.get(attr.string,'Grey')
        elif 'ALARM' in attr.quality:
            attr.color = TANGO_STATE_COLORS['FAULT']
        elif 'WARNING' in attr.quality:
            attr.color = TANGO_STATE_COLORS['ALARM']
        elif 'INVALID' in attr.quality:
            attr.color = TANGO_STATE_COLORS['OFF']
            
    except Exception,e:
        print(str((attr,traceback.format_exc())))
        raise(e)
    return dict(attr)
            
def export_commands_to_dict(device,target='*'):
    """ export all device commands config to a dictionary """
    name,proxy = (device,get_device(device)) if isString(device) else (device.name(),device)
    dct = {}
    for c in proxy.command_list_query():
        if not fandango.matchCl(target,c.cmd_name): continue
        dct[c.cmd_name] = fandango.obj2dict(c)
        dct[c.cmd_name]['device'] = name
        dct[c.cmd_name]['name'] = c.cmd_name
    return dct
    
def export_properties_to_dict(device,target='*'):
    """ export device or class properties to dictionary """
    if '/' in device:
        return get_matching_device_properties(device,target)
    else:
        db = get_database()
        props = [p for p in db.get_class_property_list(device) if fandango.matchCl(target,p)]
        return dict((k,v if isString(v) else list(v)) for k,v in db.get_class_property(device,props).items())
    
def export_device_to_dict(device):
    """
    This method can be used to export the current configuration of devices, attributes and properties to a file.
    The dictionary will get properties, class properties, attributes, commands, attribute config, event config, alarm config and pollings.
    
    .. code-block python:
    
        data = dict((d,fandango.tango.export_device_to_dict(d)) for d in fandango.tango.get_matching_devices('*00/*/*'))
        pickle.dump(data,open('bl00_devices.pck','w'))
        
    """
    i = get_device_info(device)
    dct = Struct(fandango.obj2dict(i,fltr=lambda n: n in 'dev_class host level name server'.split()))
    dct.attributes,dct.commands = {},{}
    if check_device(device):
      try:
        proxy = get_device(device)
        dct.attributes = dict((a,export_attribute_to_dict(proxy,a)) for a in proxy.get_attribute_list())
        dct.commands = export_commands_to_dict(proxy)
      except:
        traceback.print_exc()
    dct.properties = export_properties_to_dict(device)
    dct.class_properties = export_properties_to_dict(dct.dev_class)
    return dict(dct)
    
########################################################################################
## Methods for checking device/attribute availability
   
    
def get_server_pid(server):
    try:
        return get_device_info('dserver/'+server).PID
    except:
        print 'failed to use server Admin, using OS'
        pid = fandango.linos.get_process_pid(server.replace('/','.py '))
        if not pid: pid = fandango.linos.get_process_pid(server.replace('/',' '),exclude='javaArch|grep|screen|0:00')
        return pid    

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
    
def check_device(dev,attribute=None,command=None,full=False,admin=False,bad_state=False):
    """ 
    Command may be 'StateDetailed' for testing HdbArchivers 
    It will return True for devices ok, False for devices not running and None for unresponsive devices.
    """
    try:
        if full or admin:
            info = get_device_info(dev)
            if not info.exported:
                return False
            if full and not check_host(info.host):
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
        else: 
          s = dp.state()
          if bad_state:
            assert s not in bad_state and str(s) not in bad_state
          return str(s) #True
        return True
    except:
        return None

def check_attribute(attr,readable=False,timeout=0,brief=False,trace=False):
    """ checks if attribute is available.
    :param readable: Whether if it's mandatory that the attribute returns a value or if it must simply exist.
    :param timeout: Checks if the attribute value have been effectively updated (check zombie processes).
    :param brief: return just .value instead of AttrValue object
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
                if not brief:
                  return attvalue
                else:
                  return getattr(attvalue,'value',None)
        except Exception,e: 
            if trace: traceback.print_exc()
            return None if readable or brief else e
    except:
        if trace: traceback.print_exc()
        return None
    
def read_attribute(attr,timeout=0,full=False):
    """ Alias to check_attribute(attr,brief=True)"""
    return check_attribute(attr,timeout=timeout,brief=not full)

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
    elif value_type in (PyTango.DevLong64,PyTango.DevULong64):
        return long
    elif value_type in (PyTango.DevState,PyTango.DevShort,PyTango.DevInt,PyTango.DevLong,PyTango.DevULong,PyTango.DevUShort,PyTango.DevUChar): 
        return int
    else: 
        return str
      
def get_device_help(self,str_format='text'):
    """This command returns help text for this device class and its parents"""
    if str_format=='text' or True:
      linesep,docsep,item = '\n','\n\n------------\n\n',' * %s'
    try:
      doc = ''
      parents = []
      for b in type(self).__bases__:
        parents.append(b.__name__)
        if b.__doc__:
          doc = b.__name__+':'+b.__doc__
          break
      docs = [type(self).__name__+'(%s)'%','.join(parents),doc]
      for t,o in (
        ('Class Properties','class_property_list'),('Device Properties','device_property_list'),
        ('Commands','cmd_list'),('Attributes','attr_list')
        ):
        c = self.get_device_class()
        d = getattr(c,o).keys()
        if d:
          docs.append(t+linesep+linesep+linesep.join(item%k for k in d))
    except Exception,e:
      traceback.print_exc()
      raise e
    return docsep.join(docs)
    
def get_internal_devices():
    """ Gets all devices declared in the current Tango server """
    try:
        U = PyTango.Util.instance()
        dct = fandango.CaselessDict()
        for klass in U.get_class_list():
            for dev in U.get_device_list_by_class(klass.get_name()):
                dct[dev.get_name().lower()]=dev
        return dct
    except:
        return {}
    
def read_internal_attribute(device,attribute):
    """
    This method allows several things:
      * If a device object (Impl or Proxy) is given, it is used to read the attribute
      * If the attribute belongs to a device in the SAME SERVER, it accesses directly to the device object
      * If the attribute belongs to an external SERVER, use PyTango proxies to read it
      * It can manage dynamic attributes used within the same SERVER calling read_dyn_attr
    device must be a DevImpl object or string, attribute must be an string
    if the device is not internal this method will connect to a PyTango Proxy
    the method will return a fakeAttributeValue object
    """
    print 'read_internal_attribute(%s,%s)'%(device,attribute)
    import dynamic
    
    if isString(device):
        device = get_internal_devices().get(device,(getattr(attribute,'parent',None) or get_device(device,use_tau=False,keep=True)))
    
    attr = attribute if isinstance(attribute,fakeAttributeValue) else fakeAttributeValue(name=attribute,parent=device)
    
    isProxy, isDyn = isinstance(device,PyTango.DeviceProxy),hasattr(device,'read_dyn_attr')
    aname = attr.name.lower()
    if aname=='state': 
        if isProxy: attr.set_value(device.state())
        elif hasattr(device,'last_state'): attr.set_value(device.last_state)
        else: attr.set_value(device.get_state())
        print '%s = %s' % (attr.name,attr.value)
        attr.error = ''
    else: 
        if isProxy:
            print ('fandango.read_internal_attribute(): calling DeviceProxy(%s).read_attribute(%s)'%(attr.device,attr.name))
            val = device.read_attribute(attr.name)
            attr.set_value_date_quality(val.value,val.time,val.quality)
        else:
            allow_method,read_method = None,None
            for s in dir(device):
                if s.lower()=='is_%s_allowed'%aname: allow_method = s
                if s.lower()=='read_%s'%aname: read_method = s
            print ('fandango.read_internal_attribute(): calling %s.is_%s_allowed()'%(attr.device,attr.name))
            is_allowed = (not allow_method) or getattr(device,allow_method)(PyTango.AttReqType.READ_REQ)
            if not is_allowed:
                attr.throw_exception('%s.read_%s method is not allowed!!!'%(device,aname))
            elif not read_method:
                if isDyn: 
                    print ('fandango.read_internal_attribute(): calling %s(%s).read_dyn_attr(%s)'%(device.myClass,attr.device,attr.name))
                    if not device.myClass:
                        attr.throw_exception('\t%s is a dynamic device not initialized yet.'%attr.device)
                    else:
                        #Returning valid values
                        try:
                            device.myClass.DynDev = device
                            if dynamic.USE_STATIC_METHODS: device.read_dyn_attr(device,attr)
                            else: device.read_dyn_attr(attr)
                            print '%s = %s' % (attr.name,attr.value)
                            attr.error = ''
                        except:
                            attr.throw_exception()
                else:
                    attr.throw_exception('%s.read_%s method not found!!!'%(device,aname,[d for d in dir(device)]))
            else: 
                #Returning valid values
                msg = ('fandango.read_internal_attribute(): calling %s.read_%s()'%(attr.device,aname))
                print msg
                try:
                    getattr(device,read_method)(attr)
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
    others argument allows to get extra property values in a single DB call; 
    e.g others = ['polled_cmd'] would append the polled commands to the list
    """
    if isSequence(device):
        return CaselessDict(zip(map(str.lower,device[::2]),map(float,device[1::2])))
    elif isinstance(device,PyTango.DeviceProxy):
        attrs = device.get_attribute_list()
        periods = [(a.lower(),int(dp.get_attribute_poll_period(a))) for a in attrs]
        return CaselessDict((a,p) for a,p in periods if p)
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
        props = db.get_device_property(device,['polled_attr']+toSequence(others))
        d = get_polled_attrs(props.pop('polled_attr'))
        if others: d.update(props)
        return d

########################################################################################

class CachedAttributeProxy(PyTango.AttributeProxy):
    """ 
    This subclass of AttributeProxy keeps the last read value for a fixed keeptime (in milliseconds).
    
    It is used to avoid abusive attribute access from composers (fandango.dynamic) or alarm servers (fandango.tango)
    In comparison to AttributeValue, it can be used for attribute configuration setup (including polling/events)
    And it is WRITABLE!!
    """
    def __init__(self,name,keeptime=1000.,fake=False):
        self.keeptime = keeptime
        self.last_read_value = None
        self.last_read_time = 0
        self.fake = fake
        if not fake: PyTango.AttributeProxy.__init__(self,name)
        else: self.name = name
        
    def set_cache(self,value,t=None):
        self.last_read_time = t or time.time()
        self.last_read_value = hasattr(value,'value') and value or fakeAttributeValue('',value)
    
    def read(self,cache=True):
        now = time.time()
        if not cache or (now-self.last_read_time)>(self.keeptime/1e3):
            self.last_read_time = now
            try:
                self.last_read_value = None if self.fake else PyTango.AttributeProxy.read(self)
            except Exception,e:
                self.last_read_value = e
        if isinstance(self.last_read_value,Exception): raise self.last_read_value
        else: return self.last_read_value


########################################################################################
## A useful fake attribute value and event class
    
class fakeAttributeValue(object):
    """ 
    This class simulates a modifiable AttributeValue object (not available in PyTango)
    It is the class used to read values from Dev4Tango devices (valves, pseudos, composer, etc ...)
    It also has a read(cache) method to be used as a TaurusAttribute or AttributeProxy (but it returns self if cache is not used)
    The cache is controlled by keeptime variable (milliseconds)
    :param parent: Apart of common Attribute arguments, parent will be used to keep a proxy to the parent object (a DeviceProxy or DeviceImpl) 
    """
    def __init__(self,name,value=None,time_=0.,quality=PyTango.AttrQuality.ATTR_VALID,dim_x=1,dim_y=1,parent=None,device='',error=False,keeptime=0):
        self.name=name
        self.device=device or (self.name.rsplit('/',1)[0] if '/' in self.name else '')
        self.set_value(value,dim_x,dim_y)
        self.set_date(time_ or time.time())
        self.write_value = None
        self.quality=quality
        self.parent=parent
        self.error = error
        self.keeptime = keeptime*1e3 if keeptime<10. else keeptime
        self.lastread = 0
        self.type = type(value)
        
    def __repr__(self):
        return 'fakeAttributeValue(%s,%s,%s,%s,error=%s)'%(self.name,fandango.log.shortstr(self.value),time.ctime(self.get_time()),self.quality,self.error)
    __str__ = __repr__
        
    def get_name(self): return self.name
    def get_value(self): return self.value
    def get_date(self): return self.time
    def get_time(self): return self.time.totime()
    def get_quality(self): return self.quality
    
    def read(self,cache=True):
        #Method to emulate AttributeProxy returning an AttributeValue
        #print '\t\tfakeAttributeValue(%s/%s).read(%s)'%(self.device,self.name,cache)
        if not self.parent:
            self.parent = get_device(self.device,use_tau=False,keep=True)
        if not cache or 0<self.keeptime<(time.time()-self.read()):
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
        self.write_value = value
    def get_write_value(self,data = None):
        if data is None: data = []
        if isSequence(self.write_value):
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
    def __init__(self,use_tau = False):
        self.log = Logger('ProxiesDict')
        self.log.setLogLevel('INFO')
        self.use_tau = TAU and use_tau
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
                devklass,attrklass = (TAU.Device,TAU.Attribute) if self.use_tau else (PyTango.DeviceProxy,PyTango.AttributeProxy)
                dev = (attrklass if str(dev_name).count('/')==(4 if ':' in dev_name else 3) else devklass)(dev_name)
            except Exception,e:
                print('ProxiesDict: %s doesnt exist!'%dev_name)
                #print traceback.format_exc()
                #raise e
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

def get_attribute_time(value):
    #Gets epoch for a Tango value
    return getattr(value.time,'tv_sec',value.time)

class TangoedValue(object):
    pass

def getTangoValue(obj,device=None):
    """
    This method may be used to return objects from read_attribute or FIND() that are still computable and keep quality/time members
    try to avoid spectrums.; this method doesn't work for numpy arrays so I have to convert them to less efficient lists.
    """
    try:
        p = parse_tango_model(obj if type(obj) is str else (device or ''))
        if p: device,host = p['device'],p['host']+':'+p['port']
        else: host = get_tango_host()
        if type(obj) is str:
            obj = PyTango.AttributeProxy(obj).read()
        
        if hasattr(obj,'quality'):
            value,quality,t,name,ty = obj.value,obj.quality,get_attribute_time(obj),obj.name,obj.type
            if isSequence(value): 
                value = value.tolist() if hasattr(value,'tolist') else list(value)
        else:
            value,quality,t,name,ty = obj,PyTango.AttrQuality.ATTR_VALID,time.time(),'',type(obj)
            
        try: domain,family,member = device.split('/')[-3:]
        except: domain,family,member = '','',''
            
        Type = type(value)
        Type = Type if (Type not in (bool,None,type(None)) and ty!=PyTango.CmdArgType.DevState) else int
        nt = type('tangoed_'+Type.__name__,(Type,TangoedValue),{})
        o = nt(value or 0)
        [setattr(o,k,v) for k,v in (
            ('value',value),('quality',quality),('time',t),('name',name),('type',ty),
            ('device',device),('domain',domain),('family',family),('member',member),('host',host),
            )]
        return o
    except:
        print traceback.format_exc()
        return obj
            
    def __repr__(self):
        return 'v(%s)'%(self.value)

class TangoEval(object):
    """ 
    Class for Tango formula evaluation; used by Panic-like formulas
    
    example:
        te = fandango.TangoEval(cache=3)
        te.eval('test/sim/test-00/A * test/sim/test-00/S.delta')
        Out: 2.6307095848792521 #A value multiplied by delta of S in its last 3 values
    
    Attributes in the formulas may be (it is recommended to insert spaces between attribute names and operators):
    THIS REGULAR EXPRESSIONS DOES NOT MATCH THE HOST IN THE FORMULA!!!; IT IS TAKEN AS PART OF THE DEVICE NAME!!
    
        dom/fam/memb/attrib >= V1 #Will evaluate the attribute value
        d/f/m/a1 > V2 and d/f/m/a2 == V3 #Comparing 2 attributes
        d/f/m.quality != QALARM #Using attribute quality
        d/f/m/State == UNKNOWN #States can be compared directly
        d/f/m/A.exception #True if exception occurred
        d/f/m/A.time #Attribute value time
        d/f/m/A.value #Explicit value
        d/f/m/A.delta #Increase/decrease of the value since the first value in cache (if cache and cache_depth are set)
        d/f/m/A.all #Instead of just value will return an AttributeValue object 
    
    All tango-like variables are parsed. TangoEval.macros can be used to do regexp-based substitution. By default FIND(regexp) will be replaced by a list of matching attributes.
    
        FIND([a-zA-Z0-9\/].*) macro allows to get any attribute matching a regular expression
        Any variable in _locals is evaluated or explicitly replaced in the formula if matches $(); e.g. FIND($(VARNAME)/*/*)
        T() < T('YYYY/MM/DD hh:mm') allow to compare actual time with any time
    """
    FIND_EXP = 'FIND\(((?:[ \'\"])?[^)]*(?:[ \'\"])?)\)' #FIND( optional quotes and whatever is not ')' )
    
    #operators = '[><=][=>]?|and|or|in|not in|not'
    #l_split = re.split(operators,formula)#.replace(' ',''))
    alnum = '[a-zA-Z0-9-_]+'
    no_alnum = '[^a-zA-Z0-9-_]'
    no_quotes = '(?:^|$|[^\'"a-zA-Z0-9_\./])'
    #THIS REGULAR EXPRESSIONS DOES NOT MATCH THE HOST IN THE FORMULA!!!; IT IS TAKEN AS PART OF THE DEVICE NAME!!
    redev = '(?P<device>(?:'+alnum+':[0-9]+/{1,2})?(?:'+'/'.join([alnum]*3)+'))' #It matches a device name
    reattr = '(?:/(?P<attribute>'+alnum+')(?:(?:\\.)(?P<what>quality|time|value|exception|delta|all|hist))?)?' #Matches attribute and extension
    retango = redev+reattr#+'(?!/)'
    regexp = no_quotes + retango + no_quotes.replace('\.','') #Excludes attr_names between quotes, accepts value type methods    
    
    def __init__(self,formula='',launch=True,timeout=1000,keeptime=100,trace=False, proxies=None, attributes=None, cache=0, use_tau = False):
        self.formula = formula
        self.source = ''
        self.variables = []
        self.timeout = timeout
        self.keeptime = keeptime
        self.use_tau = TAU and use_tau
        self.proxies = proxies or dicts.defaultdict_fromkey(taurus.Device) if self.use_tau else ProxiesDict(use_tau=self.use_tau)
        self.attributes = attributes or dicts.CaselessDefaultDict(taurus.Attribute if self.use_tau else (lambda a:CachedAttributeProxy(a,keeptime=self.keeptime)))
        self.previous = dicts.CaselessDict() #Keeps last values for each variable
        self.last = dicts.CaselessDict() #Keeps values from the last eval execution only
        self.cache_depth = cache
        self.cache = dicts.CaselessDefaultDict(lambda k:list()) if self.cache_depth else None#Keeps [cache]
        self.result = None
        self.macros = [('FIND(%s)',self.FIND_EXP,self.find_macro)]
        
        self._trace = trace
        self._defaults = dict([(str(v),v) for v in PyTango.DevState.values.values()]+[(str(q),q) for q in PyTango.AttrQuality.values.values()])
        self._defaults['T'] = str2time
        self._defaults['str2time'] = str2time
        self._defaults['time'] = time
        self._defaults['NOW'] = time.time
        self._defaults['DEVICES'] = self.proxies
        self._defaults['DEV'] = lambda x:self.proxies[x]
        self._defaults['NAMES'] = lambda x: get_matching_devices(x) if x.count('/')<3 else get_matching_attributes(x)
        self._defaults['CACHE'] = self.cache
        self._defaults['PREV'] = self.previous
        self._defaults['READ'] = self.read_attribute
        #self._locals['now'] = time.time() #Updated at execution time
        self._defaults.update((k,v) for k,v in {'get_domain':get_domain,'get_family':get_family,'get_member':get_member,'parse':parse_tango_model}.items())
        #self._defaults.update((k,None) for k in ('os','sys',)) #Updating Not allowed models
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
        
    def find_macro(self,target):
        """
        Gets a match of FIND_EXP and applies get_matching_attributes to the expresion found.
        """
        exp = target.replace('"','').replace("'",'').strip()
        exp,sep,what = exp.partition('.')
        res = str(sorted(d.lower()+sep+what for d in get_matching_attributes([exp],trace=self._trace)))
        return res.replace('"','').replace("'",'')
    
    def add_macro(self,macro_name,macro_expression,macro_function):
        """
        Add a new macro to be parsed by parse_formula. It will apply macro_function to the target found by macro_expression; the result will later replace macro_name%target
        
        e.g: self.add_macro('FIND(%s)',self.FIND_EXP,self.find_macro) #where FIND_EXP = 'FIND\(((?:[ \'\"])?[^)]*(?:[ \'\"])?)\)'
        """
        self.macros.insert(0,(macro_name,macro_expression,macro_function))
        
    def parse_formula(self,formula,_locals=None):
        """ 
        This method just removes comments and applies self.macros (e.g FIND()) searches in the formula; 
        In this method there is no tango check, neither value replacement 
        """
        _locals = _locals or {}
        _locals.update(self._locals)
        if '#' in formula:
            formula = formula.split('#',1)[0]
        if ':' in formula and not re.match('^',redev):
            tag,formula = formula.split(':',1)
        if _locals and '$(' in formula: #explicit replacement of env variables if $() used
            for l,v in _locals.items():
                formula = formula.replace('$(%s)'%str(l),str(v))
        for macro_name,macro_exp,macro_fun in self.macros:
            matches = re.findall(macro_exp,formula)
            for match in matches:
                res = macro_fun(match)
                formula = formula.replace(macro_name%match,res)
                self.trace('TangoEval.parse_formula: Replacing %s with %s'%(macro_name%match,res))
        return formula
        
    def parse_variables(self,formula,_locals=None,parsed=False):
        ''' This method parses attributes declarated in formulas with the following formats:
        TAG1: dom/fam/memb/attrib >= V1 #A comment
        TAG2: d/f/m/a1 > V2 and d/f/m/a2 == V3
        TAG3: d/f/m.quality != QALARM #Another comment
        TAG4: d/f/m/State ##A description?, Why not
        :return: 
            - a None value if the alarm is not parsable
            - a list of (device,attribute,value/time/quality) tuples
        '''            

        #self.trace( regexp)
        idev,iattr,ival = 0,1,2 #indexes of the expression matching device,attribute and value
        
        if not parsed: formula = self.parse_formula(formula,_locals)
        
        ##@var all_vars list of tuples with (device,/attribute) name matches
        #self.variables = [(s[idev],s[iattr],s[ival] or 'value') for s in re.findall(regexp,formula) if s[idev]]
        variables = [s for s in re.findall(self.regexp,formula)]
        self.trace('parse_variables(...): %s'%(variables))
        return variables
        
    def read_attribute(self,device,attribute,what='',_raise=True, timeout=None):
        """
        Executes a read_attribute and returns the value requested
        :param _raise: if attribute is empty or 'State' exceptions will be rethrown
        """
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
            if self.cache_depth and not any(get_attribute_time(v)==get_attribute_time(value) for v in self.cache[aname]):
                while len(self.cache[aname])>=self.cache_depth: self.cache[aname].pop(-1)
                self.cache[aname].insert(0,value)
            if what == 'all': 
                if self.cache_depth:
                    try: setattr(value,'delta',self.get_delta(aname))
                    except: pass
                setattr(value,'exception',isinstance(getattr(value,'value',None),PyTango.DevFailed))
            elif what in ('value',''): 
                value = getTangoValue(value,device=device)
            elif what == 'time': value = get_attribute_time(value)
            elif what == 'exception': value = isinstance(getattr(value,'value',None),PyTango.DevFailed) #False
            elif what == 'delta': value = self.get_delta(aname)
            else: value = getattr(value,what)
            self.trace('read_attribute(%s/%s.%s) => %s'%(device,attribute,what,value))
        except Exception,e:
            if isinstance(e,PyTango.DevFailed) and what=='exception':
                return e
            elif _raise and not isNaN(_raise):
                raise e
            self.trace('TangoEval: ERROR(%s)! Unable to get %s for attribute %s/%s: %s' % (type(e),what,device,attribute,e))
            self.trace(traceback.format_exc())
            value = _raise
        return value
                
    def update_locals(self,dct=None):
        if dct:
            if not hasattr(dct,'keys'): dct = dict(dct)
            self._locals.update(dct)
            self.trace('update_locals(%s)'%dct.keys())
        self._locals['now'] = time.time()
        return self._locals
            
    def parse_tag(self,target,wildcard='_'):
        return wildcard+target.replace('/',wildcard).replace('-',wildcard).replace('.',wildcard).replace(':',wildcard).replace('_',wildcard).lower()
    
    def get_delta(self,target):
        """
        target = (device+'/'+attribute).lower() ; returns difference between first and last cached value
        """
        if self.cache and target in self.cache:
            cache = self.cache.get(target)
        else:
            var_name = self.parse_tag(target)
            if var_name in self.previous:
                device,attribute = self.parse_variables(target)[0][:2]
                cache = [self.read_attribute(device,attribute,'all'),self.previous[var_name]]
            else:
                cache = []
        delta = 0 if not cache else (cache[0].value-cache[-1].value)
        self.trace('get_delta(%s); cache[%d] = %s; delta = %s' % (target,len(cache),[v.value for v in cache],delta))
        return delta
    
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
        variables = self.parse_variables(self.formula,parsed=True) #Extract the list of tango variables
        self.trace('>'*80)
        self.trace('eval(): variables in formula are %s' % variables)
        self.source = self.formula #It will be modified on each iteration
        targets = [(device + (attribute and '/%s'%attribute) + (what and '.%s'%what),device,attribute,what) for device,attribute,what in variables]
        self.last.clear()
        ## NOTE!: It is very important to keep the same order in which expressions were extracted
        for target,device,attribute,what in targets: 
            var_name = self.parse_tag(target)
            #self.trace('\t%s => %s'%(target,var_name))
            try:
                #Reading or Overriding attribute value, if overriden value will not be kept for future iterations
                self.previous[var_name] = previous.get(target,
                    self.read_attribute(device,
                        attribute or 'State',
                        what, # if what and what!='delta' else 'value',
                        _raise=_raise if not any(d==device and a==attribute and w=='exception' for t,d,a,w in targets) else False
                        ))
                #if what=='delta':
                    #self.previous[var_name] = self.get_delta((device+'/'+attribute).lower())
                self.previous.pop(target,None)
                self.source = self.source.replace(target,var_name,1) #Every occurrence of the attribute is managed separately, read_attribute already uses caches within polling intervals
                self.last[target] = self.previous[var_name] #Used from alarm messages
            except Exception,e:
                self.last[target] = e
                raise e
        self.trace('formula = %s' % (self.source))
        self.trace('previous.items():\n'+'\n'.join(str((str(k),str(i))) for k,i in self.previous.items()))
        #self.trace('locals.items():\n'+'\n'.join(str((str(k),str(i)[:40])) for k,i in self._locals.items() if k not in self._defaults))
        self.result = eval(self.source,dict(self.previous),self._locals)
        self.trace('result = %s' % str(self.result))
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
        if isCallable(feedback):
            self.feedback = feedback
        elif isinstance(feedback,basestring):
            if '/' in feedback:
                device,target = feedback.rsplit('/',1) if feedback.count('/')>=(4 if ':' in feedback else 3) else (feedback,state)
            else:
                device,target = self.device,feedback
            proxy = TangoCommand.Proxies[device]
            attrs,comms = proxy.get_attribute_list(),[cmd.cmd_name for cmd in proxy.command_list_query()]
            if inCl(target,comms):
                self.feedback = (lambda d=device,c=target: TangoCommand.Proxies[d].command_inout(c))
            elif inCl(target,attrs):
                self.feedback = (lambda d=device,a=target: TangoCommand.Proxies[d].read_attribute(a).value)
            else:
                raise TangoCommand.CommandException('UnknownFeedbackMethod_%s'%feedback)
        return self.feedback

    def __call__(self,*args,**kwargs):
        self.execute(*args,**kwargs)
    
    def execute(self,args=None,timeout=None,feedback=None,expected=None,wait=None,asynch=None):
        self.trace('%s/%s(%s)'%(self.device,self.command,args or ''))
        #args = (args or []) #Not convinient
        timeout = notNone(timeout,self.timeout)
        if feedback is not None:
            feedback = self._parse_feedback(feedback)
        else:
            feedback = self.feedback
        expected = notNone(expected,self.expected)
        wait = notNone(wait,self.wait)
        asynch = notNone(asynch,self.asynch)
        t0 = time.time()
        result = None
        
        if isString(self.command):
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
        elif isCallable(self.command):
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

def __test_method__(args=None):
    print __name__,'test',args
    if args:
      if args and args[0] == 'help':
          help(globals().get(args[1]))
      elif args[0] in globals():
          f = globals().get(args[0])
          try:
              if callable(f):
                  args = [fandango.trial(lambda:eval(a) if isString(a) else a,excepts=a) for a in args[1:]]
                  print f(*args)
              return 0
          except:
              traceback.print_exc()
              return 1
    else:
      pass
    print 'TEST PASSED'
    return 0
            
        
if __name__ == '__main__':
    import sys
    __test_method__(sys.argv[1:])

__doc__ = fandango.get_autodoc(__name__,vars())
