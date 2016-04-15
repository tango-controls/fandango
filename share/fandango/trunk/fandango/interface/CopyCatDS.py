#!/usr/bin/env python

import sys
import traceback
import PyTango
import fandango
import json

from fandango.dynamic import *

"""
This module provides some method to extract command/attributes declaration of an existing device

It will return dictionaries to emulate the copied class, and some methods to "bypass" its commands, record their behavior and later emulate it.

Typical command declaration:
            'CreateAlarmContext':
            [[PyTango.DevVarStringArray, "tag,attributes,..."],
            [PyTango.DevLong,"new context ID"]],
            
            'CreateAlarmContext':
            [[PyTango.DevVarStringArray, "tag,attributes,..."],
            [PyTango.DevLong,"new context ID"]],
            
Typical attributes declaration:
        'VersionNumber':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ],
            {
                'Display level':PyTango.DispLevel.EXPERT,
                'description':"Version number and release note",
            } ],
        'PhoneBook':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 512]],
        'SentEmails':
            [[PyTango.DevString,
            PyTango.IMAGE,
            PyTango.READ, 512,512]],
"""

def get_cmd_descriptions(device):
    return dict((c.cmd_name,c) for c in fandango.get_device(device).command_list_query())

def copy_cmd_list(device):
    cmd_list = {}
    cmd_objs = get_cmd_descriptions(device)
    for c,obj in cmd_objs.items():
        cmd_list[c] = [[obj.in_type,obj.in_type_desc],[obj.out_type,obj.out_type_desc]]
    return cmd_list
        
def get_attr_descriptions(device):
    dp = fandango.get_device(device)
    aql = fandango.retry(dp.attribute_list_query)
    return dict((c.name,c) for c in aql)

def copy_attr_list(device):
    attr_list = {}
    attr_objs = get_attr_descriptions(device)
    for a,obj in attr_objs.items():
        attr_list[a] = [[PyTango.CmdArgType.values[obj.data_type],obj.data_format,obj.writable]]
        if obj.data_format == PyTango.SPECTRUM: attr_list[a][0].append(obj.max_dim_x)
        if obj.data_format == PyTango.IMAGE: attr_list[a][0].append(obj.max_dim_y)
    return attr_list
        
def choose_db(url,default=None):
    if ':' not in url and default is not None:
        return default
    import os
    thost = os.getenv('TANGO_HOST') if ':' not in url else url.split('/')[0]
    print 'TANGO_HOST=%s'%thost
    return PyTango.Database(*thost.split(':'))
    
class Doppelganger(fandango.SingletonMap):
    #Modes
    PLAYBACK,RECORD,BYPASS = 0,1,2
    
    #    Device Properties
    device_property_list = {
        'TargetDevice':
            [PyTango.DevString,
            "Device from which all attributes and commands will be mirrored",
            [ '' ] ],
        'ReadOnly':
            [PyTango.DevBoolean,
            "If True, all attributes will be implemented as Read Only, and no Commands will be updated",
            [ False ] ],
        'CopyAttributes':
            [PyTango.DevVarStringArray,
            "List of regular expressions to control which attributes will be copied",
            [ '*' ] ],
        'CopyCommands':
            [PyTango.DevVarStringArray,
            "List of regular expressions to control which commands will be copied",
            [ '*' ] ],
        }
    
    def __init__(self,device,filename=''):
        self.proxy = fandango.get_device(device)
        self.commands = copy_cmd_list(self.proxy)
        self.attributes = copy_attr_list(self.proxy)
        self.filename = filename
        self.data = []
        self.mode = self.BYPASS
        self.load()
        
    def load(self,filename=''):
        filename = filename or self.filename
        if not filename: return
    
    def __call__(self,argin=None):
        if self.mode in (self.BYPASS,self.RECORD):
            r = self.proxy.command_inout(*([self.command,argin] if argin is not None else [self.command]))
            if self.mode == self.RECORD:
                pass
            return r
        if self.mode == self.PLAYBACK:
            pass

###############################################################################

class CopyCatDS(DynamicDS):
    def __init__(self,cl, name):
        _locals = locals()
        self.U = PyTango.Util.instance()
        self.ds_name = self.U.get_ds_name()
        self.db = self.U.get_database()
        #self.TargetDevice = fandango.tango.get_device_property(name,'TargetDevice')
        DynamicDS.__init__(self,cl,name,_locals=_locals,useDynStates=True)
        CopyCatDS.init_device(self)
    def delete_device(self):
        self.warning("[Device delete_device method] for device")
    def init_device(self):
        self.setLogLevel('DEBUG')
        self.info("In %s::init_device()"%self.get_name())
        self.get_device_properties(self.get_device_class()) #Needed to do it twice to generate StaticAttributes properly
        fandango.tango.put_device_property(self.get_name(),dict((k,getattr(self,k)) for k in CopyCatDSClass.device_property_list),db=self.db)
        self.StaticAttributes = []
        try:
            for a,t in sorted(copy_attr_list(self.TargetDevice).items()):
                if any(fandango.matchCl(e,a) for e in self.CopyAttributes):
                    ttype,format,writable = t[0][:3]
                    if not isTypeSupported(ttype):
                        self.warning('%s attribute of type %s is not supported by DynamicDS'%(a,ttype.name))
                    else:
                        dims = len(t[0][3:])
                        if dims==2:
                            self.warning('%s attribute of type IMAGE is not supported by DynamicDS'%(a))
                        else:
                            ttype = ttype.name if not dims else ttype.name.replace('Dev','DevVar')+'Array'
                            if self.ReadOnly or writable==PyTango.AttrWriteType.READ:
                                formula = "%s=%s(XATTR('%s'))"%(a,ttype,self.TargetDevice+'/'+a)
                            else:
                                formula = "%s=%s(XATTR('%s') if not WRITE else WATTR('%s',VALUE))"%(a,ttype,self.TargetDevice+'/'+a,self.TargetDevice+'/'+a)
                            self.StaticAttributes.append(formula)
                            self.info('Added %s'%formula)
        except:
            traceback.print_exc()
        self.set_status('Copied attributes:\n\t'+'\n\t'.join(self.StaticAttributes))
        self.get_DynDS_properties()
        if self.DynamicStates: self.set_state(PyTango.DevState.UNKNOWN)
        self.info("Out of %s::init_device()"%self.get_name())
        
    def always_executed_hook(self):
        DynamicDS.always_executed_hook(self)
    def read_attr_hardware(self,data):
        pass
    #def read_dyn_attr(self):
        
    #def write_dyn_attr(self):
        
    
class CopyCatDSClass(DynamicDSClass):
    device_property_list = Doppelganger.device_property_list
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name)
    def dyn_attr(self,dev_list):
        for dev in dev_list:
            CopyCatDS.dyn_attr(dev)
        
class CopyCatServer(DynamicServer):
    """
    The DynamicServer class provides .util .instance .db .classes to have access to Tango DS internals.
    """
    def load_class(self,c):
        if c.endswith('_Copy'): return
        else: DynamicServer.load_class(self,c)
        
    def main(self,class_override=False):
        import fandango #needed to avoid startup exceptions when loading dynamically
        
        #fandango.tango.get_device_property failed!     desc = BAD_INV_ORDER CORBA system exception: BAD_INV_ORDER_ORBHasShutdown
        #doppels = dict((d,(db.get_device_property(d,['TargetDevice'])['TargetDevice'] or [''])[0]) for d in self.classes['CopyCatDS'])
        ks = [k for k in self.classes if fandango.matchCl('CopyCatDS|(^*Copy$)',k)]
        print 'classes: %s'%ks
        doppels = sorted(set(t for k in ks for t in self.classes[k]))
        print 'copycat devices: %s'%doppels
        targets = dict((d,fandango.tango.get_device_property(d,'TargetDevice')) for d in doppels)
        classes = {}
        print 'targets: %s'%targets
        if class_override:
            for t in set(targets.values()):
                if t: classes[t] = choose_db(t,self.db).get_class_for_device(t if ':' not in t else t.split('/',1)[-1])
            print 'Devices: \n%s'%"\n".join(sorted('%s = %s(%s)'%(d,t,classes.get(t,None)) for d,t in targets.items()))
        if class_override and classes:
            for c in set(classes.values()):
                print('Adding %s_Copy ...'%c)
                import fandango.interface
                setattr(fandango.interface,'%s_Copy',CopyCatDS),setattr(fandango.interface,'%s_CopyClass',CopyCatDSClass)
                self.util.add_TgClass(CopyCatDSClass,CopyCatDS,c+'_Copy')
            for d in targets:
                fandango.tango.add_new_device(self.name,classes[targets[d]]+'_Copy',d)
        self.instance.server_init()
        self.instance.server_run()
        
    def CreateCommands(self,device,target):
        pass
    
###############################################################################
        
def __test_Doppelganger(target = 'sys/tg_test/1'):
    dg = Doppelganger(target)
    print('%d commands'%len(dg.commands))
    print(dg.commands.items()[0])
    print('\n')
    print('%d attributes'%len(dg.attributes))
    print(dg.attributes.items()[0])
    
def __test_CopyCatDS(target = 'sys/tg_test/1'):
    fandango.tango.add_new_device('CopyCatDS/test','CopyCatDS','test/copycatds/01')
    PyTango.Database().put_device_property('test/copycatds/01',{'TargetDevice':[target]})
    ds = CopyCatServer('CopyCatDS/test',log='-v4')
    ds.main()
    
def main(args=None):
    import sys
    args = args or sys.argv
    if '--test' in sys.argv:
        __test_Doppelganger('sys/tg_test/1')
        print '\n'
        __test_CopyCatDS('sys/tg_test/1',class_override=True)
    else:
        ds = CopyCatServer('CopyCatDS/'+sys.argv[1],log=(sys.argv[2:] or ['-v2'])[0])
        ds.main()
    
if __name__ == '__main__':
    main()

