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
    """
    This methods mimics Jive UI form:
        server: ExecutableName/Instance
        klass:  DeviceClass
        device: domain/family/member
        
    e.g.:
        fandango.tango.add_new_device(
          'MyServer/test','MyDevice','my/own/device')
    """
    for c in (server+klass+device):
      if re.match('[^a-zA-Z0-9\-\/_\+\.\:]',c):
        raise Exception,"CharacterNotAllowed('%s')"%c
    assert server.count('/')==1
    assert clmatch(alnum,klass)
    assert clmatch(retango,device)
    dev_info = PyTango.DbDevInfo()
    dev_info.name = device.strip()
    dev_info.klass = klass.strip()
    dev_info.server = server.strip()
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
    
    from fandango.tango.search import get_matching_device_properties
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
        db,dev = get_database(dev),get_normal_name(dev)
  
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

def get_device_class(dev):
    return get_device_info(dev).dev_class

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
        
def get_model_name(model):
    """
    DEPRECATED, use parse_tango_model instead
    """
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
        
def parse_tango_model(name, use_host=False, fqdn=None, *args, **kwargs):
    """
    THIS METHOD SEEMS QUITE SLOW, USE get_normal/full_name WHEN POSSIBLE
    
    parse_tango_model('bt/DI/bpm-01/MaxADC',use_host=False,fqdn=False).items()
        ('attribute', 'MaxADC')
        ('attributename', 'maxadc')
        ('authority', 'alba03:10000')
        ('device', 'bt/DI/bpm-01')
        ('devicemodel', 'alba03:10000/bt/di/bpm-01')
        ('devicename', 'bt/di/bpm-01')
        ('fullname', 'tango://alba03:10000/bt/di/bpm-01/maxadc')
        ('host', 'alba03') # will be FQDN if specified
        ('model', 'alba03:10000/bt/di/bpm-01/maxadc') 
        ('normalname', 'bt/DI/bpm-01/maxadc') # with host if specified
        ('port', '10000')
        ('scheme', 'tango')
        ('simplename', 'bt/di/bpm-01/maxadc')
        ('tango_host', 'alba03:10000')

    
    In taurus it has to be translated; as simplename means different things
    for a TaurusAttribute and for a TaurusDevice, and taurus no longer supports
    the host + normalname syntax as fullname:
    
    In [4]: ta.getFullName() ~ model
    Out[4]: 'alba03:10000/sys/tg_test/1/state'
    In [5]: ta.getSimpleName() ~ attributename
    Out[5]: 'state'
    In [6]: ta.getNormalName() ~ simplename
    Out[6]: 'sys/tg_test/1/state'
    
    DEPRECATED: use_tau option is now deprecated due to changes in 
    Device/AttributeNameValidator API in Taurus
    """
    if fqdn is None: fqdn = fandango.tango.defaults.USE_FQDN
    use_host = use_host or fqdn
    r = Struct({'scheme':'tango'})
    r.tango_host = defhost = get_tango_host()
    r.host,r.port = defhost.split(':',1)

    name = str(name).split(';')[0].strip().replace('tango://','')
    name,r.fragment = name.split('#',1) if '#' in name else (name,'')
    m = re.match(fandango.tango.retango,name)

    if m and '/' not in name[m.end():]: #Name should end at attribute
        
        gd = m.groupdict()
        r.device = '/'.join([s for s in gd['device'].split('/') 
                                        if ':' not in s])
        if gd.get('attribute'): 
            r.attribute = gd['attribute']
        if gd.get('host'): 
            r.authority = r.tango_host = gd['host']
        if name[m.end():]:
            r.query = name[m.end():]

    if 'device' not in r: 
        return None

    else:
        r.host,r.port = r.tango_host.split(':',1)
        use_host = use_host or defhost != r.tango_host
            
        if fqdn and '.' not in r['host']:
            r.host = get_fqdn(r.host)
            r.tango_host = r.host + ':' + r.port
        
        r.authority = r.tango_host
        r.devicename = r.simplename = r.device.lower()
        r.devicemodel = r.model = ('%s/%s' % (r.tango_host, r.simplename))
        
        r.normalname = (r.devicename,r.model)[use_host]

        if 'attribute' in r: 
            r.attributename = r.attribute.lower() #taurus-like
            r.model = r.model+'/'+r.attributename
            r.simplename += '/'+r.attributename #hostless
            r.normalname += '/'+r.attributename #hostwith

        r.fullname = 'tango://'+r.model #aka uri

    return r

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
        periods = [(a.lower(),int(device.get_attribute_poll_period(a))) 
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

def get_polling_stats(device,brief = False):
    """
    Returns a dictionary of {attribute:(period,time,lasts)}
    
    If brief is True, returns usage (sum(times)/min(periods))
    """
    dp = get_device(device)
    stats = {}
    pst = dp.polling_status()
    for st in pst:
        st = [s.rsplit('=',1) for s in st.split('\n')]
        name = st[0][-1].strip()
        period = [float(s[-1]) for s in st 
                if s[0].startswith('Polling period')][0]
        times = [float(s[-1]) for s in st 
                if s[0].startswith('Time needed')][0]
        deltas = [map(float,s[-1].split(',')) for s in st 
                if 'last records' in s[0]][0]
        stats[name] = period,times,deltas
        
    if brief:
        p = min(t[0] for t in stats.values())
        s = sum(t[1] for t in stats.values())
        return s/p
        
    return stats

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

def parse_labels(text):
    if any(text.startswith(c[0]) and text.endswith(c[1]) for c in 
           [('{','}'),('(',')'),('[',']')]):
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
                                if verbose:
                                    print('cc %s?'%(cc))                                
                                continue
                            acc = getattr(ac,c)
                            if not hasattr(acc,cc):
                                if verbose:
                                    print('%s not in %s acc'%(cc,acc))
                                continue
                            elif isinstance(vvv,dict):
                                for e,p in vvv.items():
                                    if e not in AC_PARAMS:
                                        if verbose:
                                            print('e %s?'%(e))
                                        continue
                                    ae = getattr(acc,cc)
                                    if not hasattr(ae,e):
                                        if verbose:
                                            print('%s not in %s ae'%(e,ae))
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
            if p:
                dp.poll_attribute(a,p)
            elif not dp.get_attribute_poll_period(a):
                dp.stop_poll_attribute(a)
                
        except:
            traceback.print_exc()
            
    return config

def get_attribute_events(target,polled=True,throw=False):
    """
    Get current attribute events configuration 

    Pushed events will be not show, attributes not polled may not works
    
    Use check_attribute_events to verify if events are really working
    
    TODO: it uses Tango Device Proxy, should be Tango Database instead to 
    allow offline checking
    """
    try:
        d,a = target.rsplit('/',1)
        dp = get_device(d)
        aei = dp.get_attribute_config(a).events
        r = {} 
        for k,t in (
            ('arch_event',('archive_abs_change','archive_rel_change',
                        'archive_period')),
            ('ch_event',('abs_change','rel_change')),
            ('per_event',('period',))
            ):
            r[k],v = [None]*len(t),None
            for i,p in enumerate(t):
                try: 
                    v = str2float(getattr(getattr(aei,k),p))
                    r[k][i] = v
                except: 
                    pass #print(k,i,p,v)
            if not any(r[k]): 
                r.pop(k)
                
        if len(r)==1 and 'per_event' in r:
            # remove periodic event if it is the only setting (default)
            r.pop('per_event')
            
        # check polling always, as bool/state/string will have events always
        if r or polled or a.lower() in ('state','status'):
            polling = dp.get_attribute_poll_period(a)
            r['polling'] = polling

        return r
  
    except Exception,e:
        if throw: raise e
        return None
    
def get_attribute_polling(target):
    try:
        dp.get_device(target)
        return dp.get_attribute_poll_period(target.split('/')[-1])
    except:
        return None
    
def check_attribute_events(model, ev_type = None, verbose = False, 
                           asynch = False, keep = False, wait = 0.01):
    """
    This method expects model and a list of event types.
    If empty, CHANGE and ARCHIVE events are tested.
    
    It will return a dictionary with:
     - keys: available event types
     - value: True for code-pushed events, int(period) for polled-based
     
    """
    try:
        dev,attr = model.rsplit('/',1)
        dp = get_device(dev, keep = keep)
        ev_type = fandango.notNone(ev_type,
                    (EventType.CHANGE_EVENT, EventType.ARCHIVE_EVENT))
        result = dict.fromkeys(toSequence(ev_type))
        
        if check_device(dp):
            for ev_type in result.keys():
                try:
                    def hook(self,*args,**kwargs):
                        # IT SEEMS NOT EXECUTED PROPERLY!!!!
                        # keep alive threads running?
                        if self.eid is not None:
                            self.proxy.unsubscribe_event(eid)
                    
                    if asynch:
                        cb = EventCallback(dp,hook).subscribe(attr,ev_type)
                    else:
                        cb = lambda *args: None
                        if verbose:
                            print('%s.subscribe_event(%s)' % (dp,attr))
                        ei = dp.subscribe_event(attr,ev_type,cb)
                        fandango.wait(wait)
                        if verbose:
                            print('%s.unsubscribe_event(%s)' % (dp,ei))
                        dp.unsubscribe_event(ei)
                        
                    period = dp.get_attribute_poll_period(attr) 
                    result[ev_type] = period or True
                except:
                    if verbose:
                        traceback.print_exc()
                    result.pop(ev_type)

                if verbose:
                    print('Subscribe(%s,%s): %s' % (
                            attr,ev_type,result.get(ev_type,False)))

            return result

    except:
        traceback.print_exc()
        
    return None
    
def set_attribute_events(target, polling = None, rel_event = None, 
                        abs_event = None, per_event = None,
                        arch_rel_event = None, arch_abs_event = None, 
                        arch_per_event = None,verbose = False):
    """
    Allows to set independently each event property of the attribute
    
    Event properties should have same type that the attribute to be set    
    
    Polling must be integer, in millisecons
    
    Setting any event to 0 or False will erase the current configuration
    
    """

    cfg = CaselessDefaultDict(dict)
    if polling is not None: 
        #first try if the attribute can be subscribed w/out polling:
        cfg['polling'] = polling
        
    if any(e is not None for e in (rel_event, abs_event, )):
        d = cfg['events']['ch_event'] = {}
        if rel_event is not None:
            d['rel_change'] = str(rel_event or 'Not specified')
        if abs_event is not None:
            d['abs_change'] = str(abs_event or 'Not specified')

    if any(e is not None for e in 
           (arch_rel_event, arch_abs_event, arch_per_event)):
        d = cfg['events']['arch_event'] = {}
        if arch_rel_event is not None: 
            d['archive_rel_change'] = str(arch_rel_event or 'Not specified')
        if arch_abs_event is not None: 
            d['archive_abs_change'] = str(arch_abs_event or 'Not specified')
        if arch_per_event is not None: 
            d['archive_period'] = str(arch_per_event or 'Not specified')
            
    if per_event is not None:
        cfg['events']['per_event'] = {'period': str(per_event)}
    
    dev,attr = target.rsplit('/',1)
    return set_attribute_config(dev,attr,cfg,True,verbose=verbose)

def check_device_events(device):
    """
    apply check_attribute_events to all attributes of the device
    """
    if not check_device(device):
        return None
    dp = get_device(device,keep=True)
    attrs = dict.fromkeys(dp.get_attribute_list())
    
    for a in attrs:
        attrs[a] = check_attribute_events(device+'/'+a)
        
    return attrs

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
    dct = {}

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

        dct.update([(k,v)])
    return dct

def parse_black_box_row(row):
    alnum = '[0-9a-zA-Z]+'
    rip = '('+alnum+'\.'+alnum+'\.'+alnum+'(P:'+'\.'+alnum+')?)'
    pid = '(?:PID[\ =])([0-9]+)'
    date,cmd = map(str.strip,row.split(' : ',1))
    if date.count(':') == 3 and '.' not in date:
        date = '.'.join(date.rsplit(':',1))
    result = {'date':date, 'command':cmd, 'row':row, 'load':0}
    try:
        result['time'] = str2time(date)
    except:
        result['time'] = None
    
    for k,r in (('pid',pid),('host',rip)):
        try:
            result[k] = re.search(r,cmd).groups()[0]
        except:
            result[k] = ''
    result['proc'] = result['host']+':'+result['pid']
    result['cmd'] = cmd.replace(result['host'],'?').replace(result['pid'],'?')
    return result

def parse_black_box(device, n=100):
    """
    This method can be used to inspect all the clients accessing a device
    
    data = fandango.tango.methods.parse_black_box('sys/database/2')
    hosts = fn.dicts.defaultdict(list)
    for r in data.values(): hosts[r['host']].append(r)
    procs = fn.dicts.defaultdict(list)
    for r in data.values(): procs[r['proc']].append(r)
    """
    if not isinstance(device,PyTango.DeviceProxy):
        device = get_device(device)
        
    bb = device.black_box(100)
    data = dict(kmap(parse_black_box_row,bb))
    j,t,l = 0,0,''
    for i,k in enumerate(sorted(data.keys()[1:])):
        v = data[k]
        r = data[k]['time'] - data.values()[i]['time']
        if r > t: 
            j,t,l = i,r,k
        data[k]['load'] = r if r > 0 else 0
    print('slower command (%f) was %d: %s' % (t,j,l))
    return data
        

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
            
def get_device_property(device,property,db=None,raw=False):
    """
    It returns device property value or just first item 
    if value list has lenght==1
    """
    if ':' in device:
        db, device = db or get_database(device), get_normal_name(device)
        
    prop = (db or get_database()).get_device_property(
                                    device,[property])[property]
    return prop if raw or len(prop)!=1 else prop[0]

def put_device_property(device,property,*value,**db):
                        #value=None,db=None):
    """
    Two syntax are possible:
     - put_device_property(device,{property:value})
     - put_device_property(device,property,value)
    """
    value = value[0] if len(value)==1 else value
    db = db.get('db',None)
    if ':' in device:
        db, device = db or get_database(device), get_normal_name(device)
        
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

def get_attribute_property(device,attribute,prop,db=None):
    """
    It returns attribute property value or just first item 
    if value list has lenght==1
    """    
    if ':' in device:
        db, device = db or get_database(device), get_normal_name(device)
        
    return (db or get_databse()).get_device_attribute_property(
                                            device,attribute,prop)[prop]
    
def get_attributes_properties(device,attribute='*',db=None):
    """
    For a single device, it returns all matching attribute 
    property values as dict
    """
    if ':' in device:
        db, device = db or get_database(device), get_normal_name(device)
        
    db = db or get_database()
    dbd = get_database_device(db=db)
    attrs = dbd.DbGetDeviceAttributeList([device,attribute])
    props = db.get_device_attribute_property(device,attrs)
    return props
            
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
    
def property_undo(dev,prop,epoch,db=None):
    """
    Undo property change in the database 
    """
    if ':' in dev:
        db, dev = db or get_database(dev), get_normal_name(dev)
        
    db = db or get_database()
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
    
def get_property_history(dev,prop,db=None):
    """ Undo property history from the database """
    if ':' in dev:
        db, dev = db or get_database(dev), get_normal_name(dev)  
        
    db = db or get_database()
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
        extensions=EXTENSIONS,filters=[],multiline='\\',
        compact=False):
    """
    This method is intended to allow multiline properties and 
    apply @COPY, @FILE, @ATTR macros in properties declaration, 
    to obtain property values from the database or stored files.
    
    DynamicDS adds its own extensions
    """
    db = db or get_database()
    if multiline and isSequence(value) and len(value) and isString(value[0]): 
        value = list2lines(value,multiline=multiline,comment='#',joiner=False)
        #print('\n'.join(value))
        
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
        value = parsed
    
    if compact and isSequence(value) and len(value)==1:
        value = value[0]
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
        bad_state=False,throw=False, timeout=None):
    """ 
    Command may be 'StateDetailed' for testing HdbArchivers 
    It will return True for devices ok, False for devices not running 
    and None for unresponsive devices.
    """
    #print('check_device(%s,%s,%s)' % (dev,attribute,command))
    try:
        if isinstance(dev,DeviceProxy):
            dp = dev
        else:
            import fandango.tango.search as fts
            dev = fts.parse_tango_model(dev).devicemodel
            if full or admin:
                info = get_device_info(dev)
                if not info.exported:
                    return False
                if full and not check_host(info.host):
                    return False
                if not check_device('dserver/%s'%info.server,full=False):
                    return False

            dp = get_device(dev)

        if timeout:    
            dp.set_timeout_millis(int(timeout))
        p = dp.ping()
        if not p:
            return False
    except Exception as e:
        return e if throw else False

    try:
        if 'state' in (attribute,command):
            print('state')
            s = dp.state()
            if bad_state:
                assert s not in bad_state and str(s) not in bad_state
            r = str(s) #True            
        elif attribute: 
            r = dp.read_attribute(attribute)
        elif command: 
            r = dp.command_inout(command)
        else: 
            r = True

        #print('pinged, check %s,%s = %s' % (attribute,command,r))
        return r
        
    except Exception as e:
        return e if throw else None

@Cached(depth=1000,expire=10,catched=True)
def check_device_cached(*args,**kwargs):
    """ 
    Cached implementation of check_device method
    @Cached(depth=200,expire=10)
    """
    return check_device(*args,**kwargs)

def check_attribute(attr,readable=False,timeout=0,brief=False,trace=False,
                    expire=0):
    """ checks if attribute is available.
    
    Returns None if attribute does not exist, Exception if unreadable, 
    an AttrValue object if brief is False, just the value or None if True
    
    :param readable: Whether if it's mandatory that the attribute returns 
            a value or if it must simply exist.
    :param expire: Checks if the attribute value have been effectively 
            updated (check zombie processes).
    :param brief: return just .value instead of AttrValue object
    """
    try:
        if hasattr(attr,'read'):
          proxy = attr
        else:
          dev,att = attr.lower().rsplit('/',1)
          assert att in [str(s).lower() 
                for s in DeviceProxy(dev).get_attribute_list()],'AttrNotFound'
          proxy = AttributeProxy(attr)
          
        if timeout:
            proxy.get_device_proxy().set_timeout_millis(timeout)
            
        try: 
            attvalue = proxy.read()
            if readable and attvalue.quality == AttrQuality.ATTR_INVALID:
                return None
            elif expire and attvalue.time.totime()<(time.time()-expire):
                return None
            else:
                if not brief:
                    return attvalue
                else:
                    return (getattr(attvalue,'value',
                        getattr(attvalue,'rvalue',None)))

        except Exception as e: 
            if trace: 
                traceback.print_exc()
            return None if readable or brief else e
        
    except Exception as e:
        if trace: 
            traceback.print_exc()
        return None if readable or brief else e
    
@Cached(depth=10000,expire=300,catched=True)
def check_attribute_cached(*args,**kwargs):
    """ 
    Cached implementation of check_attribute method
    @Cached(depth=10000,expire=300,catched=True)
    """
    return check_attribute(*args,**kwargs)    
    
def read_attribute(attr,timeout=0,full=False):
    """ Alias to check_attribute(attr,brief=True)"""
    return check_attribute(attr,timeout=timeout,brief=not full)

def write_attribute(attr,value,timeout=0,full=False):
    """ Write attribute value to device """
    model = parse_tango_model(attr)
    dp = get_device(model.device)
    dp.set_timeout_millis(timeout*1000)
    return dp.write_attribute(model.attribute,value)

def device_command(attr,args=[],timeout=0,full=False):
    """ Execute a device command """
    model = parse_tango_model(attr)
    dp = get_device(model.device)
    dp.set_timeout_millis(timeout*1000)
    if args:
        return dp.command_inout(model.attribute,args)
    else:
        return dp.command_inout(model.attribute)

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

@Cached(depth=1,expire=3600,catched=True)
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
    
@fandango.excepts.Catched
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
    #print('read_internal_attribute(%s,%s)'%(device,attribute))
    import fandango.dynamic as dynamic
    
    if isString(device):
        device = get_internal_devices().get(device,
                    (getattr(attribute,'parent',None) 
                     or get_device(device,use_tau=False,keep=True)))
    
    attr = (attribute if isinstance(attribute,fakeAttributeValue) 
                    else fakeAttributeValue(name=attribute,parent=device))
    #attr = attribute
    
    isProxy = isinstance(device,DeviceProxy)
    isDyn = hasattr(device,'read_dyn_attr')
    aname = attr.name.lower()

    if aname=='state': 
        if isProxy: 
            # read_attribute(state) does not work and may have leaks
            #print('fandango.read_internal_attribute(): '
                    #'calling DeviceProxy(%s).state()'
                    #%(attr.device))     
            v = device.state()
            attr.set_value(v)
        elif hasattr(device,'last_state'): 
            attr.set_value(device.last_state)
        else: 
            attr.set_value(device.get_state())
        print('%s.%s = %s' % (attr.device,attr.name,attr.value))
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
