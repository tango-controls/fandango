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

.. contents::

.

"""

from .defaults import *
from .methods import *
from .search import *

########################################################################################
## Methods to export device/attributes/properties to dictionaries

def export_attribute_to_dict(model,attribute=None,value=None,keep=False,as_struct=False):
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
    return dict(attr) if not as_struct else Struct(dict(attr))
            
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
    
def export_device_to_dict(device,commands=True,properties=True):
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
        if commands:
          dct.commands = export_commands_to_dict(proxy)
      except:
        traceback.print_exc()
    if properties:
      dct.properties = export_properties_to_dict(device)
      dct.class_properties = export_properties_to_dict(dct.dev_class)
    return dict(dct)
