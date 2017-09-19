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

from .defaults import *

__test__ = {}
       
###############################################################################

def add_new_device(server,klass,device):
    for c in (server+klass+device):
      if re.match('[^a-zA-Z0-9\-\/_]',c):
        raise Exception,"CharacterNotAllowed('%s')"%c
    dev_info = PyTango.DbDevInfo()
    dev_info.name = device
    dev_info.klass = klass
    dev_info.server = server
    get_database().add_device(dev_info)
    
def delete_device(device,server=True):
    """
    This method will delete a device and all of its properties
    If the device was the last of its server, it will be also deleted 
    """
    #First, remove the attribue properties
    server = server and get_device_info(device).server
    db = get_database(get_tango_host(device))
    if check_device(device):
      dp = get_device(device)
      if False: #QUARANTINED
        ## As of Tango9 this code fails to delete attribute properties
        attrs = dp.get_attribute_list()
        for a in attrs:
          props = db.get_device_attribute_property(device,a)
          db.delete_device_attribute_property(device,props)
      adm = dp.adm_name()
      print('Kill %s'%adm)
      get_device(adm).kill()
    
    props = get_matching_device_properties(device,'*')
    print('Removing %d properties'%len(props))
    db.delete_device_property(device,props)
    print('Delete %s'%device)
    db.delete_device(device)
    if server:
      others = list(db.get_server_class_list(server))
      if all(d in ('DDebug','DServer') for d in others):
        print('Delete %s'%server)
        db.delete_server(server)
    
    return True

@Cached(depth=1000,expire=30)
def get_device_info(dev,db=None):
    """
    This method provides an alternative to DeviceProxy.info() for those 
    devices that are not running.
    As a bonus, it returns the process PID of the device!!
    """
    #vals = PyTango.DeviceProxy('sys/database/2').DbGetDeviceInfo(dev)
    vals = None
    if ':' in dev:
        from fandango.tango.search import parse_tango_model
        model = fandango.Struct(parse_tango_model(dev))
        db = get_database(model.host,model.port)
        dev = '/'.join(model.device.split('/')[-3:])
  
    try:
        dd = get_database_device(db=db)
        vals = dd.DbGetDeviceInfo(dev)
        di = Struct([(k,v) for k,v in zip(('name','ior','level','server',
                        'host','started','stopped'),vals[1])])
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
    try: 
        return get_database().get_alias(dev) 
        #.get_database_device().DbGetDeviceAlias(dev)
    except Exception,e:
        if 'no alias found' in str(e).lower(): return None
        return None #raise e

def get_alias_dict(exp='*'):
    """
    returns an {alias:device} dictionary with all matching alias from Tango DB
    :param exp:
    """
    tango = get_database()
    return dict((k,tango.get_device_alias(k)) 
                for k in tango.get_device_alias_list(exp))

def attr2str(attr_value):
    att_name = '%s='%attr_value.name if hasattr(attr_value,'name') else ''
    if hasattr(attr_value,'value'):
        return '%s%s(%s)' %(att_name,type(attr_value.value).__name__,
                            attr_value.value)
    else: 
        return '%s%s(%s)' %(att_name,type(attr_value).__name__,attr_value)

def get_real_name(dev,attr=None):
    """
    It translate any device/attribute string by name/alias/label
    
    :param device: Expected format is [host:port/][device][/attribute]; 
        where device can be either a/b/c or alias
    :param attr: optional, when passed it will be regexp 
        matched against attributes/labels
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
    """ 
    Given a device name it returns the attributes matching any of 
    the given expressions 
    """
    expressions = map(toRegexp,toList(expressions))
    al = (get_device(dev) if isString(dev) else dev).get_attribute_list()
    result = [a for a in al for expr in expressions 
              if matchCl(expr,a,terminate=True)]
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
    attrlist = (db.get_device_attribute_list(target,filters) 
                    if brief and hasattr(db,'get_device_attribute_list') 
                    else d.get_attribute_list())
    for a in attrlist:
        l = (get_attribute_label(target+'/'+a,use_db=True) 
                if brief else d.get_attribute_config(a).label)
        if ((not filters or any(map(matchCl,(filters,filters),(a,l)))) 
                and (not brief or l!=a)): 
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
    """ 
    To get all gauge port labels: 
    get_matching_device_attribute_labels('*vgct*','p*') 
    """
    devs = get_matching_devices(device)
    return dict((t+'/'+a,l) for t in devs 
                for a,l in get_device_labels(t,attribute).items() 
                if check_device(t))

def get_attribute_info(device,attribute):
    """
    This method returns attribute info in the attr_list format
    It parses values returned by:
            DeviceProxy(device).get_attribute_config(attribute)

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
    types = [CmdArgType.values.get(ai.data_type),
             ai.data_format,ai.writable]
    if ai.max_dim_x>1: types.append(ai.max_dim_x)
    if ai.max_dim_y>0: types.append(ai.max_dim_y)
    formats = dict((k,getattr(ai,k)) 
        for k,v in (('label',''),('unit','No unit'),('format',''))
        if getattr(ai,k)!=v)
    return [types,formats]
  
@Cached(depth=100,expire=15.)
def get_attribute_config(target):
    d,a = target.rsplit('/',1)
    return get_device(d).get_attribute_config(a)

def set_attribute_config(device,attribute,config,events=True,verbose=False):
    """
    device may be a DeviceProxy object
    config may be a dictionary
    """
    print('fandango.tango.set_attribute_config(%s,%s,%s)'
          %(device,attribute,config))
    dp = get_device(device) if isString(device) else device
    name,a,v = dp.name(),attribute,config    
    polling = None
    
    if isMapping(v):
        if verbose:
            print('parsing dictionary ...')

        polling = v.get('polling',None)
        
        if a.lower() not in ('state','status'):           
            ac = dp.get_attribute_config(a)
            for c,vv in v.items():
                try:
                    if c not in AC_PARAMS:
                        continue                    
                    if c.lower() == 'events':
                        if not events:
                            continue                
                        elif verbose:
                            print('parsing events: %s'%vv)
                    if not hasattr(ac,c):
                        continue
                    
                    if verbose:
                        print('%s.%s.%s'%(name,a,c))
                    
                    if isinstance(vv,dict):
                        for cc,vvv in vv.items():
                            if cc not in AC_PARAMS:
                                continue
                            acc = getattr(ac,c)
                            if not hasattr(acc,cc):
                                continue
                            elif isinstance(vvv,dict):
                                for e,p in vvv.items():
                                    if e not in AC_PARAMS:
                                        continue
                                    ae = getattr(acc,cc)
                                    if not hasattr(ae,e):
                                        continue
                                    elif getattr(ae,e)!=p:
                                        print('%s.%s.%s.%s = %s'%(a,c,cc,e,p))
                                        setattr(ae,e,p)                                        
                            elif getattr(acc,cc)!=vvv:
                                print('%s.%s.%s = %s'%(a,c,cc,vvv))
                                setattr(acc,cc,vvv)
                                
                    elif getattr(ac,c)!=vv:
                        print('%s.%s = %s'%(a,c,vv))
                        setattr(ac,c,vv)
                except:
                    print('%s/%s.%s=%s failed!'%(device,a,c,vv))
                    traceback.print_exc()
                                                   
            config = ac
            dp.set_attribute_config(config)    
            
    if polling is not None:
        p = polling
        try:
            print('%s.poll_attribute(%s,%s)'%(name,a,p))
            if not p and dp.get_attribute_poll_period(a):
                dp.stop_poll_attribute(a)
            else:
                dp.poll_attribute(a,p)
        except:
            traceback.print_exc()
            
    return config
  
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
        ('arch_event',('archive_abs_change','archive_rel_change',
                       'archive_period')),
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
        prop = get_database().get_device_attribute_property(dev,[attr])[attr]
        return (prop.get('label',[attr]) or [''])[0]
      
def set_attribute_label(target,label='',unit=''):
    if target.lower().rsplit('/')[-1] in ('state','status'): 
        return
    ap = AttributeProxy(target)
    cf = ap.get_config()
    if label: cf.label = label
    if unit: cf.unit = unit
    ap.set_config(cf)
    
def parse_db_command_array(data,keys=1,depth=2):
    """ 
    This command will parse data from DbGetDeviceAttributeProperty2 command.
    DB device commands return data in this format: 
        X XSize Y YSize Z ZSize ZValue W WSize WValue
    This corresponds to {X:{Y:{Z:[Zdata],W:[Wdata]}}}
    Depth of the array is 2 by default
    e.g.: 
    label_of_dev_test_attribute = \
        parse_db_command_array(dbd.DbGetDeviceAttributeProperty2([dev,attr]).,
        keys=1,depth=2)[dev][attr]['label'][0]
    """
    dict = {}

    for x in range(keys):
        key = data.pop(0)
        try: length = data.pop(0)
        except: return None

        if depth:
            k,v = key,parse_db_command_array(data,
                                             keys=int(length),depth=depth-1)
        else:
            try:
                length = int(length)
                k,v = key,[data.pop(0) for y in range(length)]
            except:
                k,v = key,[length]

        dict.update([(k,v)])
    return dict

def get_free_property(name,prop,db=None):
    """
    It returns class property value or just first item 
    if value list has lenght==1
    """
    host = get_tango_host(name)
    name = name.split('/')[-1]    
    db = db or get_database(host)
    prop = db.get_property(name,[prop])[prop]
    return prop if len(prop)!=1 else prop[0]

def put_free_property(name,prop,value=None,db=None):
    """
    Two syntax are possible:
     - put_free_property(free,{property:value})
     - put_free_property(free,property,value)
    """
    host = get_tango_host(name)
    name = name.split('/')[-1]
    db = db or get_database(host)    
    if not isMapping(prop):
        if isSequence(value) and not isinstance(value,list):
            value = list(value)
        prop = {prop:value}
    else:
        for p,v in prop.items():          
            if isSequence(v):
                if len(v)==1:
                    prop[p] = v[0]
                elif not isinstance(value,list):
                    prop[p] = list(v)
                    
    return db.put_property(name,prop)
  
def get_class_property(klass,property,db=None):
    """
    It returns class property value or just first item 
    if value list has lenght==1
    """
    prop = (db or get_database()
            ).get_class_property(klass,[property])[property]
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
    It returns device property value or just first item 
    if value list has lenght==1
    """
    prop = (db or get_database()).get_device_property(
                                    device,[property])[property]
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
    (db or get_database()).put_device_property(device,property)
    return property
            
def get_devices_properties(device_expr,properties,hosts=[],port=10000):
    """
    Usage:

      get_devices_properties('*alarms*',props,
        hosts=[get_bl_host(i) for i in bls])

    props must be an string as passed to Database.get_device_property(); 
    regexp are not enabled!
    
    get_matching_device_properties enhanced with multi-host support

    @TODO: Compare performance of this method with 
    get_matching_device_properties
    """
    expr = device_expr
    if not isSequence(properties): properties = [properties]
    get_devs = lambda db, reg : [d for d in db.get_device_name('*','*') 
                    if not d.startswith('dserver') and matchCl(reg,d)]
    if hosts: tango_dbs = dict(('%s:%s'%(h,port),PyTango.Database(h,port)) 
                               for h in hosts)
    else: tango_dbs = {get_tango_host():get_database()}
    return dict(('/'.join((host,d) if hosts else (d,)),
                 db.get_device_property(d,properties))
                 for host,db in tango_dbs.items() for d in get_devs(db,expr))
    
def property_undo(dev,prop,epoch):
    db = get_database()
    his = db.get_device_property_history(dev,prop)
    valids = [h for h in his if str2time(h.get_date())<epoch]
    news = [h for h in his if str2time(h.get_date())>epoch]
    if valids and news:
        print('Restoring property %s/%s=%s'%(dev,prop,valids[-1].get_date()))
        db.put_device_property(dev,{prop:valids[-1].get_value().value_string})
    elif not valids:
        print('No property values found for %s/%s before %s'
              %(dev,prop,time2str(epoch)))
    elif not news: 
        print('Property %s/%s not modified after %s'
              %(dev,prop,time2str(epoch)))
    
def get_property_history(dev,prop):
    db = get_database()
    his = db.get_device_property_history(dev,prop)
    return [(str2time(h.get_date()),h.get_value()) for h in his]
  
def get_server_property(name,instance,prop):
    name = clsub("(dserver/|.py)","",name)
    return get_device_property('dserver/'+name+'/'+instance,prop)
    

###############################################################################
# Property extensions

def get_extension_arg(x): 
    return x.split(':',1)[-1].split('#')[0]

def _copy_extension(prop,row,db=None): 
    #This extension will copy property contents from argument
    db = db or get_database()
    return db.get_device_property(get_extension_arg(row),[prop])[prop]

def _file_extension(prop,row,db=None):
    #This extension will copy property contents from filename
    try:
        f = open(get_extension_arg(row))
        r = f.readlines()
        f.close()
        return r
    except:
        traceback.print_exc()
        return []
      
def _attr_extension(prop,row,db=None):
    """
    This extension will replace the line by an attribute forwarding formula 
      ($Arg = Type(ATTR('arg'))
    
    Syntax is @ATTR:[alias=]model [+formula]
    """
    try:
      db = db or get_database()
      args = row.split(':',1)[-1].split('#')[0].split('=')
      s = args[-1].lower() #formula
      model = (searchCl(retango,s).group())
      ai = get_attribute_config(model) #config
      t = cast_tango_type(ai.data_type).__name__ #pytype
      f = str(ai.data_format) #format
      a = args[0] if len(args)>1 else model.split('/')[-1]
      s = s.replace(model,"ATTR('%s')"%model)
      r = "%s=%s(%s,%s)"%(a,f,t,s)
      return [r]
    except:
      print('fandango.tango._attr_extension(%s,%s) failed!'%(prop,row))
      traceback.print_exc()
      return []
      

EXTENSIONS = {'@COPY:':_copy_extension,
              '@FILE:':_file_extension,
              '@ATTR:':_attr_extension}

def check_property_extensions(prop,value,db=None,
                              extensions=EXTENSIONS,filters=[]):
    db = db or get_database()
    if ((not filters or prop in filters) and fandango.isSequence(value) 
        and any(str(s).startswith(e) for e in extensions for s in value)):
        parsed,get_arg = [],(lambda x:x.split(':',1)[-1].split('#')[0])
        for v in value:
            try:
                #if v.startswith('@COPY:'): 
                    #parsed.extend(DynamicDS._copy_extension(prop,v))
                #elif v.startswith('@FILE:'): 
                    #parsed.extend(DynamicDS._file_extension(prop,v))
                ext,f = first([(e,f) for e,f in extensions.items() 
                               if v.startswith(e)] or [(None,None)])
                if ext: parsed.extend(f(prop,v))
                else: parsed.append(v)
            except: 
                print('check_property_extensions(%s,%s): %s'
                      %(prop,value,traceback.format_exc()))
        return parsed
    return value


    
###############################################################################
## Methods for checking device/attribute availability
   
def get_server_pid(server):
    try:
        return get_device_info('dserver/'+server).PID
    except:
        print('failed to use server Admin, using OS')
        pid = fandango.linos.get_process_pid(server.replace('/','.py '))
        if not pid: 
            pid = fandango.linos.get_process_pid(server.replace('/',' '),
                                    exclude='javaArch|grep|screen|0:00')
        return pid    

def check_host(host):
    """
    Pings a hostname, returns False if unreachable
    """
    import fandango.linos
    print('Checking host %s'%host)
    return fandango.linos.ping(host)[host]

def check_starter(host):
    """
    Checks host's Starter server
    """
    if check_host(host):
        return check_device('tango/admin/%s'%(host.split('.')[0]))
    else:
        return False
    
def check_device(dev,attribute=None,command=None,full=False,admin=False,
        bad_state=False,throw=False, timeout=3000):
    """ 
    Command may be 'StateDetailed' for testing HdbArchivers 
    It will return True for devices ok, False for devices not running 
    and None for unresponsive devices.
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
        dp = DeviceProxy(dev)
        dp.set_timeout_millis(int(timeout))
        dp.ping()
    except Exception,e:
        return e if throw else False
    try:
        if attribute: dp.read_attribute(attribute)
        elif command: dp.command_inout(command)
        else: 
          s = dp.state()
          if bad_state:
            assert s not in bad_state and str(s) not in bad_state
          return str(s) #True
        return True
    except Exception,e:
        return e if throw else None

@Cached(depth=1000,expire=10)
def check_device_cached(*args,**kwargs):
    """ 
    Cached implementation of check_device method
    @Cached(depth=200,expire=10)
    """
    return check_device(*args,**kwargs)

def check_attribute(attr,readable=False,timeout=0,brief=False,trace=False):
    """ checks if attribute is available.
    :param readable: Whether if it's mandatory that the attribute returns 
            a value or if it must simply exist.
    :param timeout: Checks if the attribute value have been effectively 
            updated (check zombie processes).
    :param brief: return just .value instead of AttrValue object
    """
    try:
        if hasattr(attr,'read'):
          proxy = attr
        else:
          dev,att = attr.lower().rsplit('/',1)
          assert att in [str(s).lower() 
                for s in DeviceProxy(dev).get_attribute_list()]
          proxy = AttributeProxy(attr)
          
        try: 
            attvalue = proxy.read()
            if readable and attvalue.quality == AttrQuality.ATTR_INVALID:
                return None
            elif timeout and attvalue.time.totime()<(time.time()-timeout):
                return None
            else:
                if not brief:
                  return attvalue
                else:
                  return (getattr(attvalue,'value',
                                  getattr(attvalue,'rvalue',None)))
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
    This method will check a list of devices grouping them by host and server; 
    minimizing the amount of pings to do.
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
            print('Host %s failed, discarding %d devices'
                  %(host,sum(len(s) for s in servs.values())))
            result.update((d,False) for s in servs.values() for d in s)
        else:
            for server,devs in servs.items():
                if not check_device('dserver/%s'%server,full=False):
                    print('Server %s failed, discarding %d devices'
                          %(server,len(devs)))
                    result.update((d,False) for d in devs)
                else:
                    for d in devs:
                        result[d] = check_device(d,attribute=attribute,
                                                 command=command,full=False)
    return result

###############################################################################
## Methods usable from within DeviceImpl instances

def cast_tango_type(value_type):
    """ Returns the python equivalent to a Tango type"""
    if value_type in (PyTango.DevBoolean,): 
        return bool
    elif value_type in (PyTango.DevDouble,PyTango.DevFloat): 
        return float
    elif value_type in (PyTango.DevLong64,PyTango.DevULong64):
        return long
    elif value_type in (PyTango.DevState,PyTango.DevShort,PyTango.DevInt,
        PyTango.DevLong,PyTango.DevULong,PyTango.DevUShort,PyTango.DevUChar): 
        return int
    else: 
        return str
      
def get_device_help(self,str_format='text'):
    """
    This command returns help text for this device class and its parents
    """
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
        ('Class Properties','class_property_list'),
        ('Device Properties','device_property_list'),
        ('Commands','cmd_list'),
        ('Attributes','attr_list')):
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
      * If a device object (Impl or Proxy) is given, it is used 
        to read the attribute
      * If the attribute belongs to a device in the SAME SERVER, 
        it accesses directly to the device object
      * If the attribute belongs to an external SERVER, 
        use PyTango proxies to read it
      * It can manage dynamic attributes used within the 
        same SERVER calling read_dyn_attr
    device must be a DevImpl object or string, attribute must be an string
    if the device is not internal this method will connect to a PyTango Proxy
    the method will return a fakeAttributeValue object
    """
    print('read_internal_attribute(%s,%s)'%(device,attribute))
    import fandango.dynamic as dynamic
    
    if isString(device):
        device = get_internal_devices().get(device,
                    (getattr(attribute,'parent',None) 
                     or get_device(device,use_tau=False,keep=True)))
    
    attr = (attribute if isinstance(attribute,fakeAttributeValue) 
                    else fakeAttributeValue(name=attribute,parent=device))
    
    isProxy = isinstance(device,DeviceProxy)
    isDyn = hasattr(device,'read_dyn_attr')
    aname = attr.name.lower()
    if aname=='state': 
        if isProxy: attr.set_value(device.state())
        elif hasattr(device,'last_state'): attr.set_value(device.last_state)
        else: attr.set_value(device.get_state())
        print('%s = %s' % (attr.name,attr.value))
        attr.error = ''
    else: 
        if isProxy:
            print('fandango.read_internal_attribute(): '
                    'calling DeviceProxy(%s).read_attribute(%s)'
                    %(attr.device,attr.name))
            val = device.read_attribute(attr.name)
            attr.set_value_date_quality(val.value,val.time,val.quality)
        else:
            allow_method,read_method = None,None
            for s in dir(device):
                if s.lower()=='is_%s_allowed'%aname: allow_method = s
                if s.lower()=='read_%s'%aname: read_method = s
            print('fandango.read_internal_attribute():'
                    ' calling %s.is_%s_allowed()'%(attr.device,attr.name))
            is_allowed = ((not allow_method) 
                          or getattr(device,allow_method)(AttReqType.READ_REQ))
            if not is_allowed:
                attr.throw_exception('%s.read_%s method is not allowed!!!'
                                     %(device,aname))
            elif not read_method:
                if isDyn: 
                    print('fandango.read_internal_attribute():'
                            ' calling %s(%s).read_dyn_attr(%s)'
                            %(device.myClass,attr.device,attr.name))
                    if not device.myClass:
                        attr.throw_exception('\t%s is a dynamic device '
                                        'not initialized yet.'%attr.device)
                    else:
                        #Returning valid values
                        try:
                            device.myClass.DynDev = device
                            if dynamic.USE_STATIC_METHODS: 
                                device.read_dyn_attr(device,attr)
                            else: 
                                device.read_dyn_attr(attr)
                            print('%s = %s' % (attr.name,attr.value))
                            attr.error = ''
                        except:
                            attr.throw_exception()
                else:
                    attr.throw_exception('%s.read_%s method not found!!!'
                                %(device,aname,[d for d in dir(device)]))
            else: 
                #Returning valid values
                msg = ('fandango.read_internal_attribute():'
                        ' calling %s.read_%s()'%(attr.device,aname))
                print(msg)
                try:
                    getattr(device,read_method)(attr)
                    print('%s = %s' % (attr.name,attr.value))
                    attr.error = ''
                except:
                    attr.throw_exception()
    return attr

def get_polled_attrs(device,others=None):
    """ 
    @TODO: Tango8 has own get_polled_attr method; check for incompatibilities
    if a device is passed, it returns the polled_attr property as a dictionary
    if a list of values is passed, it converts to dictionary
    others argument allows to get extra property values in a single DB call; 
    e.g others = ['polled_cmd'] would append the polled commands to the list
    """
    if isSequence(device):
        return CaselessDict(zip(map(str.lower,device[::2]),
                                map(float,device[1::2])))
    elif isinstance(device,DeviceProxy):
        attrs = device.get_attribute_list()
        periods = [(a.lower(),int(dp.get_attribute_poll_period(a))) 
                   for a in attrs]
        return CaselessDict((a,p) for a,p in periods if p)
    else:
        others = others or []
        if isinstance(device,PyTango.DeviceImpl):
            db = PyTango.Util.instance().get_database()
            #polled_attrs = {}
            #lst = self.get_admin_device().DevPollStatus(device.get_name())
            #for st in lst:
                #lines = st.split('\n')
                #try: polled_attrs[lines[0].split()[-1]]=lines[1].split()[-1]
                #except: pass
            #return polled_attrs
            device = device.get_name()
        else:
            db = fandango.get_database()
        props = db.get_device_property(device,
                                       ['polled_attr']+toSequence(others))
        d = get_polled_attrs(props.pop('polled_attr'))
        if others: d.update(props)
        return d
        
def __test_method__(args=None):
    print(__name__,'test',args)
    if args:
      if args and args[0] == 'help':
          help(globals().get(args[1]))
      elif args[0] in globals():
          f = globals().get(args[0])
          try:
              if callable(f):
                  args = [fandango.trial(lambda:eval(a) if isString(a) else a,
                                         excepts=a) for a in args[1:]]
                  print(f(*args))
              return 0
          except:
              traceback.print_exc()
              return 1
    else:
      pass
    print('TEST PASSED')
    return 0
            
        
if __name__ == '__main__':
    import sys
    __test_method__(sys.argv[1:])

from fandango.doc import get_fn_autodoc
__doc__ = get_fn_autodoc(__name__,vars())
