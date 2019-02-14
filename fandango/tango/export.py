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
from .methods import *
from .search import *
from fandango.functional import str2type, toSequence

###############################################################################
## Methods to export device/attributes/properties to dictionaries


def export_attribute_to_dict(model,attribute=None,value=None,
                             keep=False,as_struct=False):
    """
    get attribute config, format and value from Tango and return it as a dict
    
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
    attr.events = Struct()
    
    def vrepr(v):
      try: return str(attr.format)%(v)
      except: return str(v)
    def cleandict(d):
      for k,v in d.items():
        if v in ('Not specified','No %s'%k):
          d[k] = ''
      return d

    try:
        v = (value 
             or check_attribute(attr.database+'/'+attr.device+'/'+attr.name))

        if v and 'DevFailed' not in str(v):
            ac = proxy.get_attribute_config(attr.name)
            
            try:
                attr.data_format = str(ac.data_format)
                attr.data_type = str(PyTango.CmdArgType.values[ac.data_type])
                attr.writable = str(ac.writable)
                attr.label = ac.label
                attr.standard_unit = ac.standard_unit
                attr.display_unit = ac.display_unit
                attr.unit = ac.unit
                attr.description = (ac.description
                    if ac.description!='No description' else '')
                attr.format = ac.format
                attr.dim_x = v.dim_x
                attr.dim_y = v.dim_y                
                attr.min_value = ac.min_value
                attr.max_value = ac.max_value
                attr.max_dim_x = ac.max_dim_x
                attr.max_dim_y = ac.max_dim_y
                attr.min_alarm = ac.min_alarm
                attr.max_alarm = ac.max_alarm
                attr.enum_labels = list(
                    getattr(ac,'enum_labels',[])) # New in T9
            except:
                traceback.print_exc()

            attr.events.ch_event = fandango.obj2dict(ac.events.ch_event)
            attr.events.arch_event = fandango.obj2dict(ac.events.arch_event)
            attr.events.per_event = fandango.obj2dict(ac.events.per_event)
            attr.alarms = fandango.obj2dict(ac.alarms)
            attr.quality = str(v.quality)
            attr.time = ctime2time(v.time)
            sep = '\n' if attr.data_type == 'DevString' else ','
                  
            if attr.data_format == 'SCALAR':
                if attr.data_type in ('DevState','DevBoolean'):
                    attr.value = int(v.value)
                    attr.string = str(v.value)
                else:
                    attr.value = v.value
                    attr.string = vrepr(v.value)
            else:
                if v.value is None or not v.dim_x:
                    attr.value = []
                    attr.string = '[]'
                elif attr.data_format == 'SPECTRUM': 
                    attr.value = list(v.value) 
                    svalue = map(vrepr,attr.value)
                    attr.string = sep.join(svalue)
                elif attr.data_format=='IMAGE': 
                    attr.value = list(map(list,v.value))
                    svalue = [[vrepr(w) for w in vv] for vv in attr.value]
                    attr.string = sep.join('[%s]' % sep.join(vv) 
                                           for vv in svalue)
                if 'numpy' in str(type(v.value)): 
                    #print('%s("%s") => python' % (type(v.value), attr.string))
                    attr.value = toSequence(str2type(attr.string))
                  
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
        print('export_attribute_to_dict(%s) failed!: %s' % (model,v))
        traceback.print_exc()
        raise(e)

    if as_struct:
        r = Struct(dict(attr))
    else:
        attr.events = dict(attr.events)
        r = dict(attr)
    return r
            
def export_commands_to_dict(device,target='*'):
    """ export all device commands config to a dictionary """
    name,proxy = ((device,get_device(device)) if isString(device) 
                  else (device.name(),device))
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
        props = [p for p in db.get_class_property_list(device) 
                 if fandango.matchCl(target,p)]
        return dict((k,v if isString(v) else list(v)) for k,v in
                    db.get_class_property(device,props).items())
    
def export_device_to_dict(device,commands=True,properties=True):
    """
    This method can be used to export the current configuration of devices, 
    attributes and properties to a file.
    The dictionary will get properties, class properties, attributes, 
    commands, attribute config, event config, alarm config and pollings.
    
    .. code-block python:
    
        data = dict((d,fandango.tango.export_device_to_dict(d)) 
            for d in fandango.tango.get_matching_devices('*00/*/*'))
        pickle.dump(data,open('bl00_devices.pck','w'))
        
    """
    i = get_device_info(device)
    dct = Struct(fandango.obj2dict(i,
            fltr=lambda n: n in 'dev_class host level name server'.split()))
    dct.attributes,dct.commands = {},{}

    if check_device(device):
        try:
            proxy = get_device(device)
            for a in proxy.get_attribute_list():
                try:
                    dct.attributes[a] = export_attribute_to_dict(proxy,a)
                except:
                    traceback.print_exc()
            if commands:
                dct.commands = export_commands_to_dict(proxy)
        except:
            traceback.print_exc()

    if properties:
        dct.properties = export_properties_to_dict(device)
        dct.class_properties = export_properties_to_dict(dct.dev_class)

    return dict(dct)

def import_device_from_dict(dct,device=None,server=None,create=True,
                            properties=True,attributes=True,events=True,
                            init=True,start=False,host=''):
    """
    This method will read a dictionary as generated by export_device_to_dict
    
    From the dictionary, properties for device and attributes will be applied
    
    properties,attributes,events can be boolean or regexp filter
    
    """
    name = device or dct['name']
    server = server or dct['server']
    if name not in get_all_devices():
        assert create,'Device %s does not exist!'%name  
        print('Creating %s at %s ...'%(name,server))
        add_new_device(server,dct['dev_class'],name)
    
    properties = '*' if properties is True else properties
    if properties:
        props = dict((k,v) for k,v in dct['properties'].items() 
                     if clmatch(properties,k))
        put_device_property(name,props)
        
    dp = get_device(name)
    if not attributes:
        return
    elif not check_device(dp):
        if not start:
            print('Device must be running to import attributes!')
            return
        from fandango import ServersDict
        print('Starting %s ...'%server)
        sd = ServersDict(name)
        sd.start_servers(host=host)
        time.sleep(5.)
    elif init:
        dp.init()

    if attributes is True:
        attributes = '*'
        
    attrs = dict((k,v) for k,v in dct['attributes'].items()
                 if clmatch(attributes,k))
    dp = get_device(name)
    alist = dp.get_attribute_list()
    alist = map(str.lower,alist)
    
    print('Loading %d attributes'%len(attrs))
    for a,v in attrs.items():
        if a.lower() not in alist:
            print('Attribute %s does not exist yet!'%a)
            continue
        
        #set attribute config implemented in .methods
        set_attribute_config(dp,a,v,events=events,verbose=True)
            
    return           
                    
                    
def tango2table(filters,opts=[]):
    """
    New method to generate .csv using export_device_to_dict and dict2array
    
    Valid options are:
        --hosts, --text, --print, --skip-attributes
        
    Calling tango2table(filters,['--hosts','--skip-attributes']) will 
        return same output that the old tango2csv scripts
        
    """
    import fandango as fd
    import fandango.tango as ft
    devices = []
    [devices.extend(ft.find_devices(f)) for f in filters]
    output = fd.defaultdict(lambda :fd.defaultdict(dict))
    attr_info = ('display_unit','standard_unit','label','unit','min_alarm',
        'events','description','format','max_alarm','polling','alarms',)
    excluded = ('None','No standard unit','No display unit','Not specified'
                'nada',)

    for d in devices:
        v = ft.export_device_to_dict(d)
        if '--hosts' in opts:
            d = output[v['host']][v['server']]
        else:
            d = output[v['server']]
            
        if '--skip-attributes' not in opts:
            d[v['name']] = {'properties':v['properties']}
            
            da = d[v['name']]['attributes'] = fd.defaultdict(dict)
            for a,t in v['attributes'].items():
                da[a] = dict((i,t.get(i)) for i in attr_info)
                
        else:
            d[v['name']] = v['properties']
        

    table = fd.arrays.dict2array(output,
                branch_filter = (lambda x: 
                    str(x)!='extensions'),
                leave_filter = (lambda y: 
                    y and str(y).split()[0] not in excluded),
                empty='')
                
    if '--text' in opts or '--print' in opts:
        text = '\n'.join('\t'.join(map(str,r)) for r in table)
    
    if '--print' in opts: 
        print(text)

    return text if '--text' in opts else table
    
