#!/usr/bin/env python2.5
""" @if gnuheader
#############################################################################
##
## file :       dynamic.py
##
## description : see below
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
"""

__doc__ = """
@package dynamic
<pre>
CLASSES FOR TANGO DEVICE SERVER WITH DYNAMIC ATTRIBUTES
by Sergi Rubio Manrique, srubio@cells.es
ALBA Synchrotron Control Group
Created 5th November 2007

This Module includes several classes:
    DynamicDS : template for dynamic attributes and states.
    DynamicDSTypes : for managing TANGOs Attribute Types
    DynamicAttribute : allows operations between Tango attributes while maintaining quality and date values

    Usage:

    1.DON'T FORGET TO ADD THIS CALLS IN YOUR DEVICE SERVER
        from dynamic import *

    2.TO init_device:
        #It is necessary to avoid all devices to have the same property values, should be unnecessary with newest PyTango release
        self.get_DynDS_properties()

    3.TO always_executed_hook or read_attr_hardware:
        self.prepare_DynDS()
        #or
        DynamicDS.always_executed_hook(self)

    4.DECLARATION OF CLASSES SHOULD BE:
        #class PyPLC(PyTango.Device_3Impl):
        class PyPLC(DynamicDS):
        #class PyPLCClass(PyTango.PyDeviceClass):
        class PyPLCClass(DynamicDSClass):

        NOTE: To make your devices Pogoable again you can substitute this change with 2 calls to:
            addTangoInterface(PyPLC,DynamicDS) and addTangoInterface(PyPLCClass,DynamicDSClass)
        This calls must be inserted in the __main__ method of your Class.py file and also at the end of the file.

    5.AND THE __init__ METHOD:
    def __init__(self,cl, name):
        #PyTango.Device_3Impl.__init__(self,cl,name)
        DynamicDS.__init__(self,cl,name,_locals={},useDynStates=True)

        #The _locals dictionary allows to parse the commands of the class to be available in attributes declaration:
        DynamicDS.__init__(self,cl,name,_locals={
            'Command0': lambda argin: self.Command0(argin),
            'Command1': lambda _addr,val: self.Command1([_addr,val]), #typical Tango command that requires an array as argument
            'Command2': lambda argin,VALUE=None: self.Command1([argin,VALUE]), #typical write command, with VALUE defaulting to None only argin is used
            },useDynStates=False)
        # This will be stored in the self._locals dictionary, that could be extended later by calling eval_attr(...,_locals={...}).
        # useDynStates argument allows to switch between generating State using alarm/warning configuration of the attributes
        # or use the commands introduced in the DynamicDS property (it must be done in __init__ as cannot be changed later).
        ...

    IF YOU WANT TO USE YOUR OWN METHODS IN THE PROPERTY TEXTS YOU SHOULD CUSTOMIZE evalAttr(Atrr_Name) and evalState(expression)
        Copy it to your device server and edit it, the arguments isREAD and isWRITE allows to differentiate Read/Write access
        </pre>
"""

import PyTango
import sys,threading,time,traceback
import inspect
from PyTango import AttrQuality
from PyTango import DevState
from excepts import *
from fandango.objects import self_locked
from fandango.dicts import SortedDict,CaselessDefaultDict
from fandango.log import Logger,shortstr
import fandango.functional as fun
import fandango.device

#from .excepts import Catched,ExceptionManager
#from  . import log

try: 
    import tau
    USE_TAU = True
except: 
    print 'Unable to import tau'
    USE_TAU=False


import os
MEM_CHECK = str(os.environ.get('PYMEMCHECK')).lower() == 'true'
if MEM_CHECK:
    try: 
        import guppy
        HEAPY = guppy.hpy()    
        HEAPY.setrelheap()    
    except:
        MEM_CHECK=False

GARBAGE_COLLECTION=False
GARBAGE,NEW_GARBAGE = None,None
if GARBAGE_COLLECTION:
    import gc
        
if 'Device_4Impl' not in dir(PyTango): PyTango.Device_4Impl = PyTango.Device_3Impl
if 'DeviceClass' not in dir(PyTango): PyTango.DeviceClass = PyTango.PyDeviceClass

class DynamicDS(PyTango.Device_4Impl,Logger):
    ''' Check fandango.dynamic.__doc__ for more information ...'''

    ######################################################################################################
    # INTERNAL DYNAMIC DEVICE SERVER METHODS
    ######################################################################################################

    def __init__(self,cl=None,name=None,_globals=None,_locals=None, useDynStates=True):
        self.call__init__(Logger,name,format='%(levelname)-8s %(asctime)s %(name)s: %(message)s')
        self.setLogLevel('WARNING')
        self.warning( ' in DynamicDS.__init__ ...')
        self.trace=False

        #Tango Properties
        self.DynamicAttributes = []
        self.DynamicStates = []
        self.DynamicStatus = []
        self.CheckDependencies = True
        #Internals
        self.dyn_attrs = {}
        self.dyn_types = {}
        self.dyn_states = SortedDict()
        self.dyn_values = {} #<- That's the main cache used for attribute management
        self.dyn_qualities = {} #<- It keeps the dynamic qualities variables
        self.variables = {}
        self.DEFAULT_POLLING_PERIOD = 3000.
        
        #Setting default values for properties
        [setattr(self,k,v[2]) for k,v in DynamicDSClass.device_property_list.items()]

        ##Local variables and methods to be bound for the eval methods
        self._globals=globals().copy()
        if _globals: self._globals.update(_globals)
        self._locals={'self':self}
        self._locals['Attr'] = lambda _name: self.getAttr(_name)
        self._locals['ATTR'] = lambda _name: self.getAttr(_name)
        self._locals['XAttr'] = lambda _name,default=None: self.getXAttr(_name,default=default)
        self._locals['XATTR'] = lambda _name,default=None: self.getXAttr(_name,default=default)
        self._locals['WATTR'] = lambda _name,value: self.getXAttr(_name,wvalue=value,write=True)
        self._locals['COMM'] = lambda _name,_argin=None,feedback=None,expected=None: self.getXCommand(_name,_argin,feedback,expected)
        self._locals['XDEV'] = lambda _name: self.getXDevice(_name)
        self._locals['ForceAttr'] = lambda a,v=None: self.ForceAttr(a,v)
        self._locals['VAR'] = lambda a,v=None: self.ForceVar(a,v)
        #self._locals['RWVAR'] = (lambda read_exp=(lambda arg=NAME:self.ForceVar(arg)),
                                #write_exp=(lambda arg=NAME,val=VALUE:self.ForceVar(arg,val)),
                                #aname=NAME, 
                                #_read=READ: 
                                    #(_read and read_exp or write_exp))
        self._locals['SetStatus'] = lambda status: [True,self.set_status(status)]
        self._locals['Add2Status'] = lambda status: [True,self.set_status(self.get_status()+status)]
        self._locals['EVAL'] = lambda formula: self.evaluateFormula(formula)
        self._locals['PROPERTY'] = lambda property,update=False: self.get_device_property(property,update)
        self._locals['DYN'] = DynamicAttribute
        [self._locals.__setitem__(str(quality),quality) for quality in AttrQuality.values.values()]
        
        #Adding states for convenience evaluation
        self.TangoStates = dict((str(v),v) for k,v in PyTango.DevState.values.items())
        self._locals.update(self.TangoStates)
        
        if _locals: self._locals.update(_locals) #New submitted methods have priority over the old ones

        # Internal object references
        self.__prepared = False
        self.myClass = None
        
        ## This dictionary stores XAttr valid arguments and AttributeProxy/TauAttribute objects
        self._external_attributes = dict()
        self._external_listeners = dict() #CaselessDefaultDict(set)
        self._external_commands = dict()

        self.time0 = time.time()
        self.simulationMode = False #If it is enabled the ForceAttr command overwrites the values of dyn_values
        self.clientLock=False #TODO: This flag allows clients to control the device edition, using isLocked(), Lock() and Unlock()
        self.lastAttributeValue = None #TODO: This variable will be used to keep value/time/quality of the last attribute read using a DeviceProxy
        self.last_state_exception = ''
        self.last_attr_exception = ''
        self._hook_epoch = 0
        self._cycle_start = 0
        self._total_usage = 0
        self._last_period = {}
        self._last_read = {}
        self._read_times = {}
        self._eval_times = {}
        self._polled_attr_ = []
        self.GARBAGE = []

        self.useDynStates = useDynStates
        if self.useDynStates:
            self.warning('useDynamicStates is set, disabling automatic State generation by attribute config.'+
                    'States fixed with set/get_state will continue working.')
            self.State=self.rawState      
        self.call__init__('Device_4Impl' in dir(PyTango) and PyTango.Device_4Impl or PyTango.Device_3Impl,cl,name)

    def delete_device(self):
        self.warning( 'DynamicDS.delete_device(): ... ')
        ('Device_4Impl' in dir(PyTango) and PyTango.Device_4Impl or PyTango.Device_3Impl).delete_device(self)
        
    def get_parent_class(self):
        return type(self).mro()[type(self).mro().index(DynamicDS)+1]

    def prepare_DynDS(self):
        """
        This code is placed here because its proper execution cannot be guaranteed during init_device().
        """
        if self.myClass is None:
            self.myClass = self.get_device_class()
        return

    @self_locked
    def always_executed_hook(self):
        #print "In DynamicDS::always_executed_hook()"
        try:
            self._hook_epoch = time.time() #Internal debugging
            if not self.__prepared: self.prepare_DynDS() #This code is placed here because its proper execution cannot be guaranteed during init_device()
            self.myClass.DynDev=self #VITAL: It tells the admin class which device attributes are going to be read
            if self.dyn_states: self.check_state()
            if self.DynamicStatus: self.check_status()
        except:
            self.last_state_exception = 'Exception in DynamicDS::always_executed_hook():\n'+str(traceback.format_exc())
            self.error(self.last_state_exception)
        return
            
    def read_attr_hardware(self,data):
        self.debug("In DynDS::read_attr_hardware()")
        ## Edit this code in child classes if needed
        #try:
            #attrs = self.get_device_attr()
            #for d in data:
                #a_name = attrs.get_attr_by_ind(d).get_name()
                #if a_name in self.dyn_attrs:
                    #pass
        #except Exception,e:
            #self.last_state_exception = 'Exception in read_attr_hardware: %s'%str(e)
            #self.error('Exception in read_attr_hardware: %s'%str(e))

    def get_DynDS_properties(self,db=None):
        """
        It forces DynamicDevice properties reading using the Database device.
        It has to be used as subclasses may not include all Dynamic* properties in their class generation.
        It is used by self.updateDynamicAttributes() and required in PyTango<3.0.4
        """
        ## THIS FUNCTION IS USED FROM updateDynamicAttributes
        self.get_device_properties(self.get_device_class()) #It will reload all subclass specific properties
        self._db = getattr(self,'_db',None) or PyTango.Util.instance().get_database() #PyTango.Database()
        
        #Loading class properties
        if not getattr(self,'DynamicSpectrumSize',False):
            U = PyTango.Util.instance()
            props = self._db.get_class_property(self.get_name(),['DynamicSpectrumSize'])
            for p in props.keys(): self.info(self.get_name()+'.'+str(p)+'="'+str(props[p])+'"')
            self.DynamicSpectrumSize=props['DynamicSpectrumSize']
        
        #Loading DynamicDS specific properties
        #targets = [p for p in DynamicDSClass.device_property_list.keys() if p not in getattr(self.get_device_class(),'device_property_list',[])]
        targets = DynamicDSClass.device_property_list.keys()
        props = self._db.get_device_property(self.get_name(),list(targets)+['polled_attr'])
        [setattr(self,PROPERTY,props[PROPERTY]) for PROPERTY in targets if props[PROPERTY]]
        self._polled_attr_=[a.lower() for a in props['polled_attr']]
        #Loading non-spectrum properties
        try: 
            self.LogLevel=props['LogLevel'][0]
            self.setLogLevel(self.LogLevel)
        except Exception,e: 
            if not getattr(self,'LogLevel',None):
                self.error('Error in get_DynDS_properties(LogLevel): %s'%str(e))
                self.LogLevel=DynamicDSClass.device_property_list['LogLevel'][2][0]
                self.setLogLevel(self.LogLevel)
        try: self.CheckDependencies=bool(props['CheckDependencies'][0])
        except Exception,e: 
            if getattr(self,'CheckDependencies',None) is None:
                self.error('Error in get_DynDS_properties(CheckDependencies): %s'%str(e))
                self.CheckDependencies=DynamicDSClass.device_property_list['CheckDependencies'][2][0]
        try: self.KeepTime=float(props['KeepTime'][0])
        except Exception,e: 
            if not getattr(self,'KeepTime',None):
                self.error('Error in get_DynDS_properties(KeepTime): %s'%str(e))
                self.KeepTime=DynamicDSClass.device_property_list['KeepTime'][2][0]
        
        for p in targets: 
            self.info(self.get_name()+'.'+str(p)+'="'+str(getattr(self,p,None))+'"')
        return
        
    def get_device_property(self,property,update=False):
        if update or not hasattr(self,property):
            setattr(self,property,self._db.get_device_property(self.get_name(),[property])[property])
        value = getattr(self,property) 
        return value[0] if type(value) is list else value

    def check_polled_attributes(self,db=None,new_attr={},use_admin=False):
        '''
        If a PolledAttribute is removed of the Attributes declaration it can lead to SegmentationFault at Device Startup.
        polled_attr property must be verified to avoid that.
        The method .get_device_class() cannot be called to get the attr_list value for this class,
        therefore new_attr must be used to add to the valid attributes any attribute added by subclasses
        Polling configuration configured through properties has preference over the hard-coded values.
        '''
        self.info('In check_polled_attributes(%s)'%new_attr)
        self._db = getattr(self,'_db',None) or PyTango.Database()
        my_name = self.get_name()
        
        new_attr = dict.fromkeys(new_attr,self.DEFAULT_POLLING_PERIOD) if isinstance(new_attr,list) else new_attr
        props = self._db.get_device_property(my_name,['DynamicAttributes','polled_attr'])
        npattrs = []
        
        dyn_attrs = [k.split('=')[0].lower().strip() for k in props['DynamicAttributes'] if k and not k.startswith('#')]
        dyn_attrs.extend(k.lower() for k in new_attr.keys()) #dyn_attrs will contain both dynamic attributes and new aggregated attributes.
        dyn_attrs.extend(['state','status'])
        
        ## The Admin device server can be used only if the server is already running; NOT at startup!
        if use_admin: 
            print 'Getting Util.instance()'
            admin = PyTango.Util.instance().get_dserver_device()                
            pattrs = []
            for st in admin.DevPollStatus(name):
                lines = st.split('\n')
                try: pattrs.extend([lines[0].split()[-1],lines[1].split()[-1]])
                except: pass
        else:        
            pattrs = props['polled_attr']
        
        #First: propagate all polled_attrs if they appear in the new attribute list
        for i in range(len(pattrs))[::2]:
            att = pattrs[i].lower()
            period = pattrs[i+1]
            if att in npattrs: 
                continue #remove duplicated
            elif att.lower() in dyn_attrs: 
                (npattrs.append(att.lower()),npattrs.append(period))
            else: 
                self.info('Removing Attribute %s from %s.polled_attr Property' % (pattrs[i],my_name))
                if use_admin:
                    try: admin.RemObjPolling([name,'attribute',att])
                    except: print traceback.format_exc()
                
        #Second: add new attributes to the list of attributes to configure; attributes where value is None will not be polled
        for n,v in new_attr.iteritems():
            if n.lower() not in npattrs and v:
                (npattrs.append(n.lower()),npattrs.append(v))
                self.info('Attribute %s added to %s.polled_attr Property' % (n,my_name))
                
        if use_admin:
            for i in range(len(npattrs))[::2]:
                try:
                    att,period = npattrs[i],npattrs[i+1]
                    if att not in pattrs:
                        admin.AddObjPolling([[int(period)],[name,'attribute',att]])
                    else:
                        admin.UpdObjPolling([[int(period)],[name,'attribute',att]])
                except:
                    print 'Unable to set %s polling' % (npattrs[i])
                    print traceback.format_exc()
        else:
           self._db.put_device_property(my_name,{'polled_attr':npattrs})
        self.info('Out of check_polled_attributes ...')
        
    def attribute_polling_report(self):
        print('-'*80)
        now = time.time()
        self._cycle_start = now-self._cycle_start
        self.info('Last complete reading cycle took: %f seconds' % self._cycle_start)
        print 'Attribute\tinterval\tread_time\teval_time\tcpu'
        print '-'*80
        for t,key in reversed(sorted((v,k) for k,v in self._read_times.items())):
            #self.info('%s read after %s s; needed %f s; eval in %f s; %f of the usage' % (key, self._last_period[key],self._read_times[key],self._eval_times[key],self._read_times[key]/self._total_usage))
            print('%s\t%d\t%1.2e\t%1.2e\t%1.2f%%'%(key, 
                int(1e3*self._last_period[key]),
                self._read_times[key],
                self._eval_times[key],
                100*self._eval_times[key]/(self._total_usage or 1.)))
        self.info('%f s empty seconds in total; %f of CPU Usage' % (self._cycle_start-self._total_usage,self._total_usage/self._cycle_start))
        self.info('%f of time used in expressions evaluation' % (sum(self._eval_times.values())/(sum(self._read_times.values()) or 1)))
        if False: #GARBAGE_COLLECTION:
            if not gc.isenabled(): gc.enable()
            gc.collect()
            grb = gc.get_objects()
            self.info('%d objects in garbage collector, %d objects are uncollectable.'%(len(grb),len(gc.garbage)))
            try:
                if self.GARBAGE:
                    NEW_GARBAGE = [o for o in grb if o not in self.GARBAGE]
                    self.info('New objects added to garbage are: %s' % ([str(o) for o in NEW_GARBAGE]))
            except:
                print traceback.format_exc()
            self.GARBAGE = grb
        if MEM_CHECK:
            h = HEAPY.heap()
            self.info(str(h))
        self._cycle_start = now
        self._total_usage = 0
        self.info('-'*80)
        
    def check_attribute_events(self,aname,poll=False):
        self.UseEvents = [u.lower().strip() for u in self.UseEvents]
        if not len(self.UseEvents): return False
        elif self.UseEvents[0] in ('no','false'): return False
        elif aname.lower().strip() == 'state': return True
        elif any(fun.matchCl(s,aname) for s in self.UseEvents): return True #Attrs explicitly set doesn't need event config
        elif self.UseEvents[0] in ('yes','true') and any(self.check_events_config(aname)): return True
        else: return False
    
    def check_events_config(self,aname):
        cabs,crel = 0,0
        try:
            ac = self.get_attribute_config_3(aname)[0]
            try: cabs = float(ac.event_prop.ch_event.abs_change)
            except: pass
            try: crel = float(ac.event_prop.ch_event.rel_change)
            except: pass
        except:pass
        return cabs,crel
    
    def check_changed_event(self,aname,new_value):
        if aname not in self.dyn_values: return False
        try:
            v = self.dyn_values[aname].value
            new_value = getattr(new_value,'value',new_value)
            cabs,crel = self.check_events_config(aname)
            self.info('In check_changed_event(%s,%s): %s!=%s > (%s,%s)?'%(aname,shortstr(new_value),v,shortstr(new_value),cabs,crel))
            if fun.isSequence(v) and cabs>0 and crel>0: 
                self.info('In check_changed_event(%s,%s): list changed!'%(aname,shortstr(new_value)))
                return bool(v!=new_value)
            else:
                try: v,new_value = (float(v) if v is not None else None),float(new_value)
                except: 
                    self.info('In check_changed_event(%s,%s): values not evaluable (%s,%s)'%(aname,new_value,v,new_value))
                    return False
                if v is None:
                    self.info('In check_changed_event(%s,%s): first value read!'%(aname,new_value))
                    return True
                elif cabs>0 and not v-cabs<new_value<v+cabs: 
                    self.info('In check_changed_event(%s,%s): absolute change!'%(aname,new_value))
                    return True
                elif crel>0 and not v*(1-crel/100.)<new_value<v*(1+crel/100.): 
                    self.info('In check_changed_event(%s,%s): relative change!'%(aname,new_value))
                    return True
                else: 
                    self.info('In check_changed_event(%s,%s): nothing changed'%(aname,new_value))
                    return False
        except: #Needed to prevent fails if attribute_config_3 is not available
            print traceback.format_exc()
        return False
        
    #------------------------------------------------------------------------------------------------------
    #   Attribute creators and read_/write_ related methods
    #------------------------------------------------------------------------------------------------------

    ## Dynamic Attributes Creator
    def dyn_attr(self):
        """
        Dynamic Attributes Creator: It initializes the device from DynamicAttributes and DynamicStates properties.
        It is called by all DeviceNameClass classes that inherit from DynamicDSClass.
        It MUST be an static method, to bound dynamic attributes and avoid being read by other devices from the same server.
        This is why Read/Write attributes are staticmethods also. (in other devices lambda is used)
        """
        self.info('\n'+'='*80+'\n'+'DynamicDS.dyn_attr( ... ), entering ...'+'\n'+'='*80)
        self.KeepAttributes = [s.lower() for s in self.KeepAttributes]
        
        ## Lambdas not used because using staticmethods
        #read_method = lambda attr,fire_event=True,s=self: s.read_dyn_attr(attr,fire_event)
        #write_method = lambda attr,fire_event=True,s=self: s.write_dyn_attr(attr,fire_event)

        if not hasattr(self,'DynamicStates'):
            self.error('DynamicDS property NOT INITIALIZED!')
            
        if self.DynamicStates:
            self.dyn_states = SortedDict()
            def add_state_formula(st,formula):
                self.dyn_states[st]={'formula':formula,'compiled':compile(formula,'<string>','eval')}
                self.info(self.get_name()+".dyn_attr(): new DynamicState '"+ st+"' = '"+formula+"'")
            for line in self.DynamicStates:
                # The character '#' is used for comments
                if not line.strip() or line.strip().startswith('#'): continue
                fields = (line.split('#')[0]).split('=',1)
                if not fields or len(fields) is 1 or '' in fields:
                    self.debug( self.get_name()+".dyn.attr(): wrong format in DynamicStates Property!, "+line)
                    continue

                st,formula = fields[0].upper().strip(),fields[1].strip()
                if st in self.TangoStates:
                    add_state_formula(st,formula)
                elif st == 'STATE':
                    [add_state_formula(s,'int(%s)==int(%s)'%(s,formula))
                        for s in self.TangoStates if not any(l.startswith(s) for l in self.DynamicStates)]
                else:
                    self.debug( self.get_name()+".dyn.attr(): Unknown State: %s"%line)

        polled_attrs = set(self._polled_attr_[::2])
        for line in self.DynamicAttributes:
            if not line.strip() or line.strip().startswith('#'): continue
            fields=[]
            # The character '#' is used for comments in Attributes specification
            if '#' in line: fields = (line.split('#')[0]).split('=',1)[0]
            else: fields = line.split('=',1)
            if fields is None or len(fields) is 1 or '' in fields:
                self.debug(self.get_name()+".dyn_attr(): wrong format in DynamicAttributes Property!, "+line)
                continue
            else:
                aname,formula=fields[0].strip(),fields[1].strip()
                self.info(self.get_name()+".dyn_attr(): new Attribute '"+aname+"' = '"+formula+"'")
                
                ## How to compare existing formulas?
                # Strip the typename from the beginning (so all typenames must be identified!)
                # .strip() spaces and compare
                # if the code is the same ... don't touch anything
                # if the code or the type changes ... remove the attribute!
                # dyn_attr() will create the attributes only if they don't exist.
                if aname not in self.dyn_values:
                    create = True
                    self.dyn_values[aname]=DynamicAttribute()
                    self.dyn_values[aname].keep = self.KeepAttributes and (not 'no' in self.KeepAttributes) and any(q.lower() in self.KeepAttributes for q in [aname,'*','yes','true'])
                    self.dyn_types[aname]=None
                else: create = False

                is_allowed = (lambda s,req_type,a=aname: type(self).is_dyn_allowed(s,req_type,a))
                max_size = hasattr(self,'DynamicSpectrumSize') and self.DynamicSpectrumSize
                AttrType = PyTango.AttrWriteType.READ_WRITE if 'WRITE' in formula else PyTango.AttrWriteType.READ
                for typename,dyntype in DynamicDSTypes.items():
                    if max([formula.startswith(label) for label in dyntype.labels]):
                        self.debug(self.get_name()+".dyn_attr():  '"+line+ "' matches " + typename + "=" + str(dyntype.labels))
                        if formula.startswith(typename):
                            formula=formula.lstrip(typename)
                        
                        if dyntype.dimx==1:
                            if (create): self.add_attribute(PyTango.Attr(aname,dyntype.tangotype, AttrType), \
                                self.read_dyn_attr,self.write_dyn_attr,is_allowed)
                                #self.read_dyn_attr,self.write_dyn_attr,self.is_dyn_allowed)
                        else:
                            if (create): self.add_attribute(PyTango.SpectrumAttr(aname,dyntype.tangotype, AttrType,max_size or dyntype.dimx), \
                                self.read_dyn_attr,self.write_dyn_attr,is_allowed)
                                #self.read_dyn_attr,self.write_dyn_attr,self.is_dyn_allowed)
                        self.dyn_types[aname]=dyntype
                        break

                if not self.dyn_types[aname]:
                    self.debug("DynamicDS.dyn_attr(...): Type not matched for '"+line+"', using DevDouble by default"    )
                    if max(map(formula.startswith,['list(','['])):
                            dyntype = DynamicDSTypes['DevVarDoubleArray']
                            if (create): self.add_attribute(PyTango.SpectrumAttr(aname,dyntype.tangotype, AttrType,max_size or dyntype.dimx), \
                                self.read_dyn_attr,self.write_dyn_attr,is_allowed)
                                #self.read_dyn_attr,self.write_dyn_attr,self.is_dyn_allowed)
                            self.dyn_types[aname]=dyntype
                    else:
                        if (create): self.add_attribute(PyTango.Attr(aname,PyTango.ArgType.DevDouble, AttrType), \
                            self.read_dyn_attr,self.write_dyn_attr,is_allowed)
                            #self.read_dyn_attr,self.write_dyn_attr,self.is_dyn_allowed)
                        self.dyn_types[aname]=DynamicDSTypes['DevDouble']

                #print 'Type of Dynamic Attribute "',aname,'=',formula,'" is "',str(self.dyn_types[aname].labels),'"'
                self.dyn_attrs[aname]=formula
                #TODO: Some day self.dyn_values should substitute both dyn_attrs and dyn_types
                self.dyn_values[aname].formula=formula
                try: self.dyn_values[aname].compiled=compile(formula.strip(),'<string>','eval')
                except: self.error(traceback.format_exc())
                self.dyn_values[aname].type=self.dyn_types[aname]
                self.dyn_values[aname].formula=self.dyn_attrs[aname]

                #Adding attributes to DynamicStates queue:
                for k,v in self.dyn_states.items():
                    if aname in v['formula']:
                        #self.dyn_values[aname]=None
                        self.dyn_values[aname].states_queue.append(k)
                        self.info("DynamicDS.dyn_attr(...): Attribute %s added to attributes queue for State %s"%(aname,k))
                        
                #Setting up change events:
                if self.check_attribute_events(aname):
                    self._locals[aname] = None
                    if aname in polled_attrs: self.set_change_event(aname,True,False)
                    else: polled_attrs.add(aname)
                elif self.dyn_values[aname].keep:
                    self._locals[aname] = None
                
        if hasattr(self,'DynamicQualities') and self.DynamicQualities:
            ## DynamicQualities: (*)_VAL = ALARM if $_ALRM else VALID
            self.info('Updating Dynamic Qualities ........')
            import re
            self.dyn_qualities,exprs = {},{}
            vals = [(line.split('=')[0].strip(),line.split('=')[1].strip()) for line in self.DynamicQualities if '=' in line and not line.startswith('#')]
            for exp,value in vals:
                if '*' in exp and '.*' not in exp: exp=exp.replace('*','.*')
                if not exp.endswith('$'): exp+='$'
                exprs[exp] = value
            for aname in self.dyn_values.keys():
                for exp,value in exprs.items():
                    try:
                        match = re.match(exp,aname)
                        if match:
                            self.info('There is a Quality for this attribute!: '+str((aname,exp,shortstr(value))))
                            for group in (match.groups()): #It will replace $ in the formula for all strings matched by .* in the expression
                                value=value.replace('$',group,1) #e.g: (.*)_VAL=ATTR_ALARM if ATTR('$_ALRM') ... => RF_VAL=ATTR_ALARM if ATTR('RF_ALRM') ...
                            self.dyn_qualities[aname.lower()] = value
                    except Exception,e:
                        self.warning('In dyn_attr(qualities), re.match(%s(%s),%s(%s)) failed' % (type(exp),exp,type(aname),aname))
                        print traceback.format_exc()
                        
        #Setting up state events:
        if self.check_attribute_events('State'): 
            if 'state' in polled_attrs: self.set_change_event('State',True,False)
            else: polled_attrs.add('state')
        
        try:
            self.check_polled_attributes(new_attr=dict.fromkeys(polled_attrs,self.DEFAULT_POLLING_PERIOD))
        except:
            'DynamicDS.dyn_attr( ... ), unable to set polling for (%s): \n%s'%(list(polled_attrs),traceback.format_exc())
        
        print 'DynamicDS.dyn_attr( ... ), finished. Attributes ready to accept request ...'

    #dyn_attr MUST be an static method, to avoid attribute mismatching (self will be always passed as argument)
    dyn_attr=staticmethod(dyn_attr) 

    def get_dyn_attr_list(self):
        """Gets all dynamic attribute names."""
        return self.dyn_attrs.keys()

    def is_dyn_allowed(self,req_type,attr_name=''):
        return True

    #@Catched #Catched decorator is not compatible with PyTango_Throw_Exception
    @self_locked
    def read_dyn_attr(self,attr,fire_event=True):
        aname = attr.get_name()
        tstart=time.time()
        keep = aname in self.dyn_values and self.dyn_values[aname].keep or self.check_attribute_events(aname)
        self.debug("DynamicDS("+self.get_name()+")::read_dyn_atr("+attr.get_name()+"), entering at "+time.ctime()+"="+str(tstart)+"...")
        #raise Exception,'DynamicDS_evalAttr_NotExecuted: searching memory leaks ...'
        try:
            if keep and self.KeepTime and self._last_read.get(aname,0) and time.time()<(self._last_read[aname]+(self.KeepTime/1e3)):
                v = self.dyn_values[aname]
                self.info('Returning cached (%s) value for %s: %s(%s)'%(time.ctime(self._last_read[aname]),aname,type(v.value),shortstr(v.value)))
                return attr.set_value_date_quality(v.value,v.date,v.quality)
        except Exception,e:
            self.warning('Unable to reload Kept values, %s'%str(e))
        try:
            result = self.evalAttr(aname)
            quality = getattr(result,'quality',self.get_quality_for_attribute(aname,result))
            date = self.get_date_for_attribute(aname,result)
            result = self.dyn_types[aname].pytype(result)

            if hasattr(attr,'set_value_date_quality'):
              attr.set_value_date_quality(result,date,quality)
            else: #PyTango<7
              if type(result) in (list,set,tuple):
                attr_DynAttr_read = []
                for r in result: attr_DynAttr_read.append(r)
                try: PyTango.set_attribute_value_date_quality(attr_DynAttr_read,date,quality,len(attr_DynAttr_read),0)
                except: attr.set_value(attr_DynAttr_read)
              else: 
                try: PyTango.set_attribute_value_date_quality(attr,result,date,quality)
                except: attr.set_value(result)
                
            text_result = (type(result) is list and result and '%s[%s]'%(type(result[0]),len(result))) or str(result)
            now=time.time()
            self._last_period[aname]=now-self._last_read.get(aname,0)
            self._last_read[aname]=now
            self._read_times[aname]=now-self._hook_epoch
            self._eval_times[aname]=now-tstart
            self._total_usage += now-self._hook_epoch
            self.debug('DynamicDS('+self.get_name()+").read_dyn_attr("+aname+")="+text_result+
                    ", ellapsed %1.2e"%(self._eval_times[aname])+" seconds.\n")
                    #", finished at "+time.ctime(now)+"="+str(now)+", timestamp is %s"%str(date)+", difference is "+str(now-date))
            if (aname=='POLL' if 'POLL' in self.dyn_values else 
                (time.time()>(self._cycle_start+self.PollingCycle*1e-3) if hasattr(self,'PollingCycle') else aname==self.dyn_values.keys()[-1])
                ):
                self.attribute_polling_report()
        except Exception, e:           
            now=time.time()
            self.dyn_values[aname].update(e,now,PyTango.AttrQuality.ATTR_INVALID) #Exceptions always kept!
            self._last_period[aname]=now-self._last_read.get(aname,0)
            self._last_read[aname]=now
            self._read_times[aname]=now-self._hook_epoch #Internal debugging
            self._eval_times[aname]=now-tstart #Internal debugging
            if aname==self.dyn_values.keys()[-1]: self._cycle_start = now
            #last_exc = getLastException()
            #last_exc = '\n'.join([str(e)]*4)
            last_exc = str(e)
            self.error('DynamicDS_read_%s_Exception: %s' % (aname,last_exc))
            print traceback.format_exc()
            raise Exception('DynamicDS_read_%s_Exception: %s' % (aname,last_exc))
            #PyTango.Except.throw_exception('DynamicDS_read_dyn_attr_Exception',str(e),last_exc)
    
    ##This hook has been used to force self to be passed always as argument and avoid dynattr missmatching
    read_dyn_attr=staticmethod(read_dyn_attr)

    @Catched
    @self_locked
    def write_dyn_attr(self,attr,fire_event=True):
        aname = attr.get_name()
        self.debug("DynamicDS("+self.get_name()+")::write_dyn_atr("+aname+"), entering at "+time.ctime()+"...")
        data=[]
        attr.get_write_value(data)
        if self.dyn_types[aname].dimx==1: data=data[0]
        self.setAttr(aname,data)
        #self.dyn_values[aname].update(result,time.time(),PyTango.AttrQuality.ATTR_VALID)
        ##if fire_event: self.fireAttrEvent(aname,data)
    write_dyn_attr=staticmethod(write_dyn_attr)

    #------------------------------------------------------------------------------------------------------
    #   Attributes and State Evaluation Methods
    #------------------------------------------------------------------------------------------------------

    # DYNAMIC ATTRIBUTE EVALUATION ... Copy it to your device and add any method you will need
    def evalAttr(self,aname,WRITE=False,VALUE=None,_locals=None):
        ''' SPECIFIC METHODS DEFINITION DONE IN self._locals!!! 
        @remark Generators don't work  inside eval!, use lists instead
        '''
        self.debug("DynamicDS("+self.get_name()+ ")::evalAttr("+aname+"): ... last value was %s"%shortstr(getattr(self.dyn_values.get(aname,None),'value',None)))
        
        if aname in self.dyn_values:
            formula,compiled = self.dyn_values[aname].formula,self.dyn_values[aname].compiled#self.dyn_attrs[aname]       
        else:#Getting a caseless attribute that match
            try:
                aname,formula,compiled = ((k,self.dyn_values[k].formula,self.dyn_values[k].compiled) for k in self.dyn_values if k.lower()==aname.lower()).next()
            except: 
                self.warning('DynamicDS.evalAttr: %s doesnt match any Attribute name, trying to evaluate ...'%aname)
                formula,compiled=aname,None

        try:
            #Checking attribute dependencies
            if self.CheckDependencies and aname in self.dyn_values:
                if self.dyn_values[aname].dependencies is None:
                    self.debug("In evalAttr ... setting dependencies")
                    self.dyn_values[aname].dependencies = set()
                    for k,v in self.dyn_values.items():
                        found = fun.searchCl("(^|[^'\"_0-9a-z])%s($|[^'\"_0-9a-z])"%k,formula)
                        if found and k.lower().strip()!=aname.lower().strip():
                            self.dyn_values[aname].dependencies.add(k)
                            self.dyn_values[k].keep = True
                            
                #Updating Last Attribute Values
                if self.dyn_values[aname].dependencies:
                    now = time.time()
                    for k in (self.dyn_values[aname].dependencies or []):
                        self.debug("In evalAttr(%s) ... updating dependencies (%s)"%(aname,k))
                        if self.KeepTime and (not self._last_read.get(k,0) or now>(self._last_read[k]+(self.KeepTime/1e3))):
                            self.debug("In evalAttr ... updating %s value"%k)
                            self.read_dyn_attr(self,fandango.device.fakeAttributeValue(k))
                        v = self.dyn_values[k]
                        if k.lower().strip()!=aname.lower().strip() and isinstance(v.value,Exception): 
                            self.warning('evalAttr(%s): An exception is rethrowed from attribute %s'%(aname,k))
                            raise v.value #Exceptions are passed to dependent attributes
                        else: self._locals[k]=v.value #.value 
            else:
                self.debug("In evalAttr ... updating locals from dyn_values")
                for k,v in self.dyn_values.items():
                    if v.keep and k in formula:
                        self._locals[k]=v.value
            
            self.debug("In evalAttr ... updating locals defaults")
            self._locals.update({
                't':time.time()-self.time0,
                'WRITE':WRITE,
                'READ':bool(not WRITE),
                'ATTRIBUTE':aname,
                'NAME':self.get_name(),
                'VALUE':VALUE,
                'STATE':self.get_state(),
                'LOCALS':self._locals,
                }) #It is important to keep this values persistent; becoming available for quality/date/state/status management
            if _locals is not None: self._locals.update(_locals) #High Priority: variables passed as argument
            
            if not WRITE:
                self.debug('%s::evalAttr(): Attribute=%s; formula=%s;'%(self.get_name(),aname,formula,))
                #self.debug('vars in self._locals: %s'%self._locals.keys())
                result = eval(compiled or formula,self._globals,self._locals)
                quality = self.get_quality_for_attribute(aname,result)
                if hasattr(result,'quality'): result.quality = quality
                date = self.get_date_for_attribute(aname,result)
                has_events = self.check_attribute_events(aname)
                value = self.dyn_types[aname].pytype(result)
                #Events must be checked before updating the cache
                if has_events and self.check_changed_event(aname,result):
                    self.info('>'*80)
                    self.info('Pushing %s event!: %s(%s)'%(aname,type(result),result))
                    self.push_change_event(aname,value,date,quality)
                #Updating the cache:
                keep = aname in self.dyn_values and self.dyn_values[aname].keep or has_events
                if keep: 
                    old = self.dyn_values[aname].value
                    self.dyn_values[aname].update(value,date,quality)
                    (self.debug if self.KeepAttributes[0] in ('yes','true') else self.info)('evalAttr(%s): Value will be kept for later reuse' % (aname))
                    #Updating state if needed:
                    if old!=value and self.dyn_values.get(aname).states_queue:
                        self.check_state()
                return result
            else:
                self.debug('%s::evalAttr(WRITE): Attribute=%s; formula=%s; VALUE=%s'%(self.get_name(),aname,formula,shortstr(VALUE)))
                #self.debug('vars in self._locals: %s'%self._locals.keys())
                return eval(compiled or formula,self._globals,self._locals)

        except PyTango.DevFailed, e:
            if self.trace:
                print '-'*80
                print '\n'.join(['DynamicDS_evalAttr(%s)_WrongFormulaException:'%aname,'\t"%s"'%formula,str(traceback.format_exc())])
                print '\n'.join(traceback.format_tb(sys.exc_info()[2]))
                print '\n'.join([str(e.args[0])]) + '\n'+'*'*80
                print '-'*80
            #PyTango.Except.throw_exception('DynamicDS_evalAttr_WrongFormula','%s is not a valid expression!'%formula,str(e))
            err = e.args[0]
            raise e#Exception,';'.join([err.origin,err.reason,err.desc])
            #PyTango.Except.throw_exception(str(err.reason),str(err.desc),str(err.origin))
        except Exception,e:
            print '\n'.join(['DynamicDS_evalAttr_WrongFormulaException','%s is not a valid expression!'%formula,str(e)])
            print '\n'.join(traceback.format_tb(sys.exc_info()[2]))
            raise e#Exception,'DynamicDS_eval(%s): %s'%(formula,traceback.format_exc())
            #PyTango.Except.throw_exception('DynamicDS_evalAttr_WrongFormula','%s is not a valid expression!'%formula,str(traceback.format_exc()))
        finally:
            self._locals['ATTRIBUTE'] = ''

    # DYNAMIC STATE EVALUATION
    def evalState(self,formula,_locals={}):
        """
        Overloading the eval method to be used to evaluate State expressions
        ... To customize it: copy it to your device and add any method you will need
        @remark Generators don't work  inside eval!, use lists instead
        """
        self.debug('DynamicDS.evalState/evaluateFormula(%s)'%(isinstance(formula,str) and formula or 'code'))
        #MODIFIIED!! to use pure DynamicAttributes
        #Attr = lambda a: self.dyn_values[a].value
        t = time.time()-self.time0
        for k,v in self.dyn_values.items(): self._locals[k]=v#.value #Updating Last Attribute Values
        __locals=locals().copy() #Low priority: local variables
        __locals.update(self._locals) #Second priority: object statements
        __locals.update(_locals) #High Priority: variables passed as argument
        __locals.update({'STATE':self.get_state(),'t':time.time()-self.time0,'NAME': self.get_name()})
        #print 'IN EVALSTATE LOCALS ARE:\n',__locals
        return eval(formula,self._globals,__locals)

    #------------------------------------------------------------------------------------------------------
    #   Methods usable inside Attributes declaration
    #------------------------------------------------------------------------------------------------------

    def getAttr(self,aname):
        """Evaluates an attribute and returns its Read value."""
        return self.evalAttr(aname)

    def setAttr(self,aname,VALUE):
        """Evaluates the WRITE part of an Attribute, passing a VALUE."""
        self.evalAttr(aname,WRITE=True,VALUE=VALUE)
        
    def event_received(self,source,type_,attr_value):
        def log(prio,s): print '%s %s %s: %s' % (prio.upper(),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),self.get_name(),s)
        if type_ == tau.core.TauEventType.Config:
            log('debug','In DynamicDS.event_received(%s(%s),%s,%s(%s)): Not Implemented!'%(
                type(source).__name__,source,tau.core.TauEventType[type_],type(attr_value).__name__,getattr(attr_value,'value',attr_value))
                )
        else:
            log('info','In DynamicDS.event_received(%s(%s),%s,%s)'%(
                type(source).__name__,source,tau.core.TauEventType[type_],type(attr_value).__name__)
                )
            try:
                full_name = source.getFullName() #.get_full_name()
                if self._external_listeners[full_name]:
                    log('info','\t%s.listeners: %s'%(full_name,self._external_listeners[full_name]))
                    for aname in self._external_listeners[full_name]:
                        if self._locals['ATTRIBUTE'] == aname:
                            #Variable already being evaluated
                            continue 
                        else:
                            log('info','\tforwarding event to %s ...'%aname)
                            self.evalAttr(aname)
            except:
                print traceback.format_exc()
        return
        
    def getXDevice(self,dname):
        """
        This method returns a DeviceProxy to the given attribute.
        """
        if USE_TAU:
            return tau.Device(dname)
        else:
            return PyTango.DeviceProxy(dname)

    def getXAttr(self,aname,default=None,write=False,wvalue=None):
        """
        Performs an external Attribute reading, using a DeviceProxy to read own attributes.
        Argument could be: [attr_name] or [device_name](=State) or [device_name/attr_name]
        
        :returns: Attribute value or None
        """
        device,aname = ('/' not in aname) and (None,aname) or aname.count('/')==2 and (aname,'State') or aname.rsplit('/',1)
        self.debug("DynamicDS(%s)::getXAttr(%s): ..."%(device or self.get_name(),aname))
        result = default #Returning an empty list because it is a False iterable value that can be converted to boolean (and False or None cannot be converted to iterable)
        try:
            if not device:
                self.info('getXAttr accessing to device itself ... using getAttr instead')
                if write: 
                    self.setAttr(aname,wvalue)
                    result = wvalue
                else: result = self.getAttr(aname)
            else:
                devs_in_server = self.myClass.get_devs_in_server()
                if device in devs_in_server:
                    self.debug('getXAttr accessing a device in the same server ... using getAttr')
                    if aname.lower()=='state': result = devs_in_server[device].get_state()
                    elif aname.lower()=='status': result = devs_in_server[device].get_status() 
                    elif write: 
                        devs_in_server[device].setAttr(aname,wvalue) 
                        result = wvalue
                    else: result = devs_in_server[device].getAttr(aname)
                else:
                    full_name = (device or self.get_name())+'/'+aname
                    self.debug('getXAttr calling a proxy to %s' % full_name)
                    if full_name not in self._external_attributes:
                        if USE_TAU: 
                            a = tau.Attribute(full_name)
                            #full_name = a.getFullName() #If the host is external it must be specified in the formula
                            self._external_attributes[full_name] = a
                            self._external_attributes[full_name].changePollingPeriod(self.DEFAULT_POLLING_PERIOD)
                            if len(self._external_attributes) == 1: tau.core.utils.Logger.disableLogOutput()
                            if self._locals.get('ATTRIBUTE') and self.check_attribute_events(self._locals.get('ATTRIBUTE')):
                                self.info('\t%s.addListener(%s)'%(full_name,self._locals['ATTRIBUTE']))
                                if a.getFullName() not in self._external_listeners: self._external_listeners[a.getFullName()]=set()
                                self._external_listeners[a.getFullName()].add(self._locals['ATTRIBUTE'])
                            self._external_attributes[full_name].addListener(self.event_received)
                        else: self._external_attributes[full_name] = PyTango.AttributeProxy(full_name)
                    if write: 
                        self._external_attributes[full_name].write(wvalue)
                        result = wvalue
                    else:
                        attrval = self._external_attributes[full_name].read()
                        result = attrval.value
                    self.debug('%s.read() = %s ...'%(full_name,str(result)[:40])) 
        except:
            msg = 'Unable to read attribute %s from device %s: \n%s' % (str(aname),str(device),traceback.format_exc())
            print msg
            self.error(msg)
            self.last_attr_exception = time.ctime()+': '+ msg
            #Exceptions are not re_thrown to allow other commands to be evaluated if this fails.
        finally:
            if hasattr(self,'myClass') and self.myClass:
                self.myClass.DynDev=self #NOT REDUNDANT: If a call to another device in the same server occurs this pointer could have been modified.
                
        #Check added to prevent exceptions due to empty arrays
        if hasattr(result,'__len__') and not len(result):
            result = default if hasattr(default,'__len__') else []        
        elif result is None:
            result = default
        self.debug('Out of getXAttr()')
        return result

    def getXCommand(self,cmd,args=None,feedback=None,expected=None):
        """
        Performs an external Command reading, using a DeviceProxy
        :param cmd_name: a/b/c/cmd
        """
        self.info("DynamicDS(%s)::getXComm(%s,%s,%s,%s): ..."%(self.get_name(),cmd,args,feedback,expected))
        if feedback is None:
            device,cmd = cmd.rsplit('/',1) if '/' in cmd else (self.get_name(),cmd)
            full_name = device+'/'+cmd
            result = None
            try:
                if device == self.get_name():
                    self.info('getXCommand accessing to device itself ...')
                    result = getattr(self,cmd)(args)
                else:
                    devs_in_server = self.myClass.get_devs_in_server()
                    if device in devs_in_server:
                        self.debug('getXCommand accessing a device in the same server ...')
                        if cmd.lower()=='state': result = devs_in_server[device].get_state()
                        elif cmd.lower()=='status': result = devs_in_server[device].get_status() 
                        else: result = getattr(devs_in_server[device],cmd)(argin)
                    else:
                        self.debug('getXCommand calling a proxy to %s' % device)
                        if full_name not in self._external_commands:
                            if USE_TAU: 
                                self._external_commands[full_name] =  tau.Device(device)
                                if len(self._external_commands)==1: tau.core.utils.Logger.disableLogOutput()
                            else: self._external_commands[full_name] = PyTango.DeviceProxy(device)
                        self.debug('getXCommand(%s(%s))'%(full_name,args))
                        if args in (None,[],()):
                            result = self._external_commands[full_name].command_inout(cmd)
                        else:
                            result = self._external_commands[full_name].command_inout(cmd,args)
                        #result = self._external_commands[full_name].command_inout(*([cmd,argin] if argin is not None else [cmd]))
            except:
                self.last_attr_exception = time.ctime()+': '+ 'Unable to execute %s(%s): %s' % (full_name,args,traceback.format_exc())
                self.error(self.last_attr_exception)
                #Exceptions are not re_thrown to allow other commands to be evaluated if this fails.
            finally:
                if hasattr(self,'myClass') and self.myClass:
                    self.myClass.DynDev=self #NOT REDUNDANT: If a call to another device in the same server occurs this pointer could have been modified.
            return result
        else:
            if fun.isString(cmd):
                if '/' not in cmd: device = self.get_name()
                else: device,cmd =  cmd.rsplit('/',1)
            else: device = self.get_name()
            if fun.isString(feedback) and '/' not in feedback: feedback = device+'/'+feedback
            return fandango.device.TangoCommand(command=cmd,device=device,feedback=feedback,timeout=10.,wait=10.).execute(args,expected=expected)

    def get_quality_for_attribute(self,aname,attr_value):
        self.debug('In get_quality_for_attribute(%s,%s)' % (aname,shortstr(attr_value,15)[:10]))
        try:
            if aname.lower() in self.dyn_qualities:
                formula = self.dyn_qualities[aname.lower()]
                self._locals['VALUE'] = getattr(attr_value,'value',attr_value)
                self._locals['DEFAULT'] = getattr(attr_value,'quality',PyTango.AttrQuality.ATTR_VALID)
                quality = eval(formula,{},self._locals) or PyTango.AttrQuality.ATTR_VALID
            else:
                quality =  getattr(attr_value,'quality',PyTango.AttrQuality.ATTR_VALID)
            self.debug('\t%s.quality = %s'%(aname,quality))
            return quality
        except Exception,e:
            self.error('Unable to generate quality for attribute %s: %s'%(aname,traceback.format_exc()))
            return PyTango.AttrQuality.ATTR_VALID

    def get_date_for_attribute(self,aname,value):
        if type(value) is DynamicAttribute:
            return value.date
        return time.time()

    def ForceAttr(self,argin,VALUE=None):
        ''' Description: The arguments are AttributeName and an optional Value.<br>
            This command will force the value of the Attribute or will return the last forced value
            (if only one argument is passed). '''
        if type(argin) is not list: argin = [argin]
        if len(argin)<1: raise Exception('At least 1 argument required (AttributeName)')
        if len(argin)<2: value=VALUE
        else: value=argin[1]
        aname = argin[0]

        if aname not in self.dyn_values.keys(): raise Exception('Unknown State or Attribute : ', aname)
        elif value is not None:
            self.dyn_values[aname].forced=value
            if self.simulationMode:
                self.dyn_values[aname].value=value
        else: value = self.dyn_values[aname].forced
        return value
        
    def ForceVar(self,argin,VALUE=None):
        ''' Description: The arguments are VariableName and an optional Value.<br>
            This command will force the value of a Variable or will return the last forced value
            (if only one argument is passed). '''
        if type(argin) is not list: argin = [argin]
        if len(argin)<1: raise Exception('At least 1 argument required (AttributeName)')
        if len(argin)<2: value=VALUE
        else: value=argin[1]
        aname = argin[0]

        if value is not None: self.variables[aname] = value
        elif aname in self.variables: value = self.variables[aname]
        else: value = 0
        return value

#------------------------------------------------------------------------------------------------------
#   State related methods
#------------------------------------------------------------------------------------------------------

    def rawState(self):
        state = self.get_state()
        self.debug('In DynamicDS.State()='+str(state)+', overriding attribute-based State.')
        return state

    def set_state(self,state):
        self._locals['STATE']=state
        DynamicDS.get_parent_class(self).set_state(self,state)

    def check_state(self,set_state=True):
        '''    The thread automatically close if there's no activity for 5 minutes,
            an always_executed_hook call or a new event will restart the thread.
        '''
        if self.dyn_states:
            self.debug('In DynamicDS.check_state()')
            old_state = self.get_state()
            ## @remarks: the device state is not changed if none of the DynamicStates evaluates to True
            #self.set_state(PyTango.DevState.UNKNOWN)
            self.last_state_exception = ''
            for state,value in self.dyn_states.items():
                nstate,formula,code=state,value['formula'],value['compiled']
                if nstate not in self.TangoStates: continue
                result=None
                try: 
                    result=self.evalState(code) #Use of self.evalState allows to overload it
                except Exception,e:
                    self.error('DynamicDS(%s).check_state(): Exception in evalState(%s): %s'%(self.get_name(),formula,str(traceback.format_exc())))
                    self.last_state_exception += '\n'+time.ctime()+': '+str(traceback.format_exc())
                self.info('In DynamicDS.check_state(): %s = %s = %s' % (state,result,value['formula']))
                if result and self.TangoStates[nstate]!=old_state:
                    self.info('DynamicDS(%s.check_state(): New State is %s := %s'%(self.get_name(),nstate,formula))
                    if set_state:
                        self.set_state(self.TangoStates[nstate])
                        if self.check_attribute_events('state'): 
                            self.info('DynamicDS(%s.check_state(): pushing new state event'%(self.get_name()))
                            self.push_change_event('State',self.TangoStates[nstate],time.time(),PyTango.AttrQuality.ATTR_VALID)
                    break
        else: 
            state = self.get_state()
        return state
    
    def set_status(self,status):
        if not any('STATUS' in s for s in self.DynamicStatus):
            self._locals['STATUS']=status
        DynamicDS.get_parent_class(self).set_status(self,status)
        
    def set_full_status(self,status,set=True):
        if self.last_state_exception:
            status += '\nLast DynamicStateException was:\n\t'+self.last_state_exception
        if self.last_attr_exception:
            status += '\nLast DynamicAttributeException was:\n\t'+self.last_attr_exception
        if set: self.set_status(status)
        return status
    
    def check_status(self,set=True):
        status = self.get_status()
        if self.DynamicStatus:
            self.debug('In DynamicDS.check_status')
            try:
                status = '\n'.join([self.evaluateFormula(s) for s in self.DynamicStatus])
                if set: self.set_status(status)
            except Exception,e:
                self.warning('Unable to generate DynamicStatus:\n%s'%traceback.format_exc())
        return status

#------------------------------------------------------------------------------------------------------
#   Lock/Unlock Methods
#------------------------------------------------------------------------------------------------------

    def isLocked(self):
        return self.clientLock

    def Lock(self):
        self.clientLock=True

    def Unlock(self):
        self.clientLock=False

#------------------------------------------------------------------------------------------------------
#   DynamicAttribute manipulation methods
#------------------------------------------------------------------------------------------------------

    def updateDynamicAttributes(self):
        """Forces dynamic attributes update from properties.
        @warning : It will DELETE all attributes that does not appear in DynamicAttributes property or StaticAttributes list!
        """
        self.get_DynDS_properties()
        
        ##All attributes managed with dyn_attr() that does not appear in DynamicAttributes or StaticAttributes list will be removed!
        attrs_list = [name.split('=',1)[0].strip() for name in (self.DynamicAttributes + (hasattr(self,'StaticAttributes') and self.StaticAttributes or []))]
        for a in self.dyn_attrs:
            if a not in attrs_list:
                self.warning('DynamicDS.updateDynamicAttributes(): Removing Attribute!: %sn not in [%s]' % (a,attrs_list))
                try:
                    self.remove_attribute(a)
                except Exception,e:
                    self.error('Unable to remove attribute %s: %s' % (a,str(e)))
        DynamicDS.dyn_attr(self)
        
        #Updating DynamicCommands (just update of formulas)
        try: CreateDynamicCommands(type(self),type(self.get_device_class()))
        except: self.error('CreateDynamicCommands failed: %s'%traceback.format_exc)

    #------------------------------------------------------------------
    #    EvaluateFormula command:
    #
    #    Description: This execute eval(Expression), just to check if its sintax is adequate or not.
    #
    #    argin:  DevString    PyTango Expression to evaluate
    #    argout: DevString
    #------------------------------------------------------------------
    #Methods started with underscore could be inherited by child device servers for debugging purposes
    def evaluateFormula(self,argin):
        argout=str(self.evalState(str(argin)))
        return argout

    """
    #THE FOLLOWING COMMANDS HAVE BEEN COPIED FROM PySignalSimulator AND ARE NOT STILL PORTED TO THIS CLASS BEHAVIOUR!
    #------------------------------------------------------------------
    #    SetExpression command:
    #
    #    Description: The arguments are AttributeName,Expression.<br>This command will set the value of the Attribute to eval(Expression) each time that read_attribute is executed.
    #
    #    argin:  DevVarStringArray    AttributeName,Expression
    #------------------------------------------------------------------
    def SetExpression(self,argin):
        try:
            if len(argin)<2: raise Exception()
            aname = argin[0] ; exp = argin[1]
            if aname in self.dyn_attrs.keys():
                def Attr(_name): return self.getAttr(_name)
                t = time.time()-self.time0
                eval(exp)
                self.dyn_attrs[aname]=exp
            elif aname in self.TangoStates:
                i=-1
                for s in self.SimStates:
                    if aname in s:
                        i = self.SimStates.index(s)
                        self.SimStates[i]=str(aname+'='+exp)
                if i<0:
                    self.SimStates.append(str(aname+'='+exp))
            else:
                raise Exception('Unknown State or Attribute : ', aname)
        except Exception, e:
            PyTango.Except.throw_exception(str(e),'This is not a valid expression!','PySignalSimulator.SetExpression('+argin.__repr__()+')')
    """

    """
    #------------------------------------------------------------------
    #    StoreExpressions command:
    #
    #    Description: This command forces the actual expressions for each attribute to be stored in the database, by writing the SimAttributes Property.
    #------------------------------------------------------------------
        def StoreExpressions(self):
            prop=[]
            for att,val in self.dyn_attrs.items():
                prop.append(str(att+'='+val))
            db = PyTango.Database()
            db.put_device_property(self.get_name(),{'SimAttributes': prop, 'SimStates': self.SimStates})
    #------------------------------------------------------------------
    #    ListExpressions command:
    #
    #    Description: It returns a list with the expressions actually set for each attribute.
    #    argout: DevString
    #------------------------------------------------------------------
        def ListExpressions(self):
            argout='SimAttributes:\n'
            for att,val in self.dyn_attrs.items():
                argout=argout+'\t'+str(att+'='+val)+'\n'
            argout=argout+'\nSimStates:\n'
            for s in self.SimStates:
                argout=argout+'\t'+s+'\n'
            return argout
    """

#------------------------------------------------------------------------------------------------------
#   End Of DynamicDS class
#------------------------------------------------------------------------------------------------------

class DynamicDSClass(PyTango.DeviceClass):
    #This device will point to the device actually being readed; it is set by read_attr_hardware() method; it should be thread safe
    DynDev = None

    #    Class Properties
    class_property_list = {
        'DynamicSpectrumSize':
            [PyTango.DevLong,
            "It will fix the maximum size for all Dynamic Attributes.",
            [ 4096 ] ],    
        }

    #    Device Properties
    device_property_list = {
        'DynamicAttributes':
            [PyTango.DevVarStringArray,
            "Attributes and formulas to create for this device.\n\nThis Tango Attributes will be generated dynamically using this syntax:\n\nT3=int(SomeCommand(7007)/10.)\n\n\nSee the class description to know how to make any method available in attributes declaration.\n\nNOTE:Python generators dont work here, use comprehension lists instead.",
            [] ],
        'DynamicStates':
            [PyTango.DevVarStringArray,
            "This property will allow to declare new States dinamically based on\n\ndynamic attributes changes. The function Attr will allow to use the\n\nvalue of attributes in formulas.\n\n\n\nALARM=Attr(T1)>70\nOK=1",
            [] ],
        'DynamicQualities':
            [PyTango.DevVarStringArray,
            "This property will allow to declare formulas for Attribute Qualities.",
            [] ],
        'DynamicStatus':
            [PyTango.DevVarStringArray,
            "Each line generated by this property code will be added to status",
            [] ],
        'KeepAttributes':
            [PyTango.DevVarStringArray,
            "This property can be used to store the values of only needed attributes; values are 'yes', 'no' or a list of attribute names",
            ['yes'] ],
        'KeepTime':
            [PyTango.DevDouble,
            "The kept value will be returned if a kept value is re-asked within this milliseconds time (Cache).",
            [ 200 ] ],
        'CheckDependencies':
            [PyTango.DevBoolean,
            "This property manages if dependencies between attributes are used to check readability.",
            [True] ],
        'UseEvents':
            [PyTango.DevVarStringArray,
            "Value of this property will be yes/true,no/false or a list of attributes that will trigger push_event (if configured from jive)",
            ['false'] ],
        'LogLevel':
            [PyTango.DevString,
            "This property selects the log level (DEBUG/INFO/WARNING/ERROR)",
            ['INFO'] ],
        }

    #    Command definitions
    cmd_list = {
        'updateDynamicAttributes':
            [[PyTango.DevVoid, ""],
            [PyTango.DevVoid, ""],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],
        'evaluateFormula':
            [[PyTango.DevString, "formula to evaluate"],
            [PyTango.DevString, "formula to evaluate"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],
        }

    #    Attribute definitions
    attr_list = {
        }

    def dyn_attr(self,dev_list):
        print 'In DynamicDSClass.dyn_attr(%s)'%dev_list
        for dev in dev_list:
            DynamicDS.dyn_attr(dev)
            
    def get_devs_in_server(self,MyClass=None):
        """
        Method for getting a dictionary with all the devices running in this server
        """
        MyClass = MyClass or DynamicDS
        if not hasattr(MyClass,'_devs_in_server'):
            MyClass._devs_in_server = {} #This dict will keep an access to the class objects instantiated in this Tango server
        if not MyClass._devs_in_server:
            U = PyTango.Util.instance()
            for klass in U.get_class_list():
                for dev in U.get_device_list_by_class(klass.get_name()):
                    if isinstance(dev,DynamicDS):
                        MyClass._devs_in_server[dev.get_name()]=dev
        return MyClass._devs_in_server

#======================================================================================================
#
#   END OF DynamicDS AND DynamicDSClass CLASSES DECLARATION
#
#======================================================================================================

#======================================================================================================
#
#   Additional Classes for Attribute types management ...
#
#======================================================================================================


class DynamicDSType(object):
    """ Allows to parse all the Tango types for Attributes """
    def __init__(self,tangotype,labels,pytype,dimx=1,dimy=1):
        self.tangotype=tangotype
        self.labels=labels
        self.pytype=pytype
        self.dimx=dimx
        self.dimy=dimy
        pass
    pass

DynamicDSTypes={
            'DevState':DynamicDSType(PyTango.ArgType.DevState,['DevState','long','int'],int),
            'DevLong':DynamicDSType(PyTango.ArgType.DevLong,['DevLong','long','int'],int),
            'DevShort':DynamicDSType(PyTango.ArgType.DevShort,['DevShort','short'],int),
            'DevString':DynamicDSType(PyTango.ArgType.DevString,['DevString','str'],str),
            'DevBoolean':DynamicDSType(PyTango.ArgType.DevBoolean,['DevBoolean','bit','bool','Bit','Flag'],bool),
            'DevDouble':DynamicDSType(PyTango.ArgType.DevDouble,['DevDouble','float','double','DevFloat','IeeeFloat'],float),
            'DevVarLongArray':DynamicDSType(PyTango.ArgType.DevLong,['DevVarLongArray','list(long','[long','list(int','[int'],lambda l:[int(i) for i in list(l)],4096,1),
            'DevVarShortArray':DynamicDSType(PyTango.ArgType.DevShort,['DevVarShortArray','list(short','[short'],lambda l:[int(i) for i in list(l)],4096,1),
            'DevVarStringArray':DynamicDSType(PyTango.ArgType.DevString,['DevVarStringArray','list(str','[str'],lambda l:[str(i) for i in list(l)],4096,1),
            'DevVarBooleanArray':DynamicDSType(PyTango.ArgType.DevShort,['DevVarBooleanArray','list(bool','[bool'],lambda l:[bool(i) for i in list(l)],4096,1),
            'DevVarDoubleArray':DynamicDSType(PyTango.ArgType.DevDouble,['DevVarDoubleArray','list(double','[double','list(float','[float'],lambda l:[float(i) for i in list(l)],4096,1),
            }
            
def CreateDynamicCommands(ds,ds_class):
    """
    By convention all dynamic commands have argin=DevVarStringArray, argout=DevVarStringArray
    This function will check all dynamic devices declared within this server
    
    @todo an special declaration should allow to redefine that! DevComm(typein,typeout,code)
    
    The code to add a new command will be something like:
    #srubio: it has been added for backward compatibility
    PyPLC.WriteBit,PyPLCClass.cmd_list['WriteBit']=PyPLC.WriteFlag,[[PyTango.DevVarShortArray, "DEPRECATED, Use WriteFlag instead"], [PyTango.DevVoid, "DEPRECATED, Use WriteFlag instead"]]
    """
    U = PyTango.Util.instance()
    server = U.get_ds_name()
    print 'In DynamicDS.CreateDynamicCommands(%s)'%(server)
    db = U.get_database()
    #devices = DynamicDSClass('DynamicDS').get_devs_in_server()    
    classes = list(db.get_device_class_list(server))
    print 'class = %s; classes = %s' % (ds.__name__,classes)
    devs = [classes[i] for i in range(len(classes)-1) if classes[i+1]==ds.__name__]    
    print 'devs = %s'%devs
    
    arg_command = [[PyTango.DevVarStringArray, "ARGS"],[PyTango.DevString, "result"],]
    void_command = [[PyTango.DevVoid, "ARGS"],[PyTango.DevString, "result"],]
    if not hasattr(ds,'dyn_comms'): ds.dyn_comms = {}
    
    for dev in devs:
        print 'In DynamicDS.CreateDynamicCommands(%s.%s)'%(server,dev)
        prop =db.get_device_property(dev,['DynamicCommands'])['DynamicCommands']
        lines = [l for l in [d.split('#')[0].strip() for d in prop] if l]
        ds.dyn_comms.update([(dev+'/'+l.split('=',1)[0].strip(),l.split('=',1)[1].strip()) for l in lines])
        print 'dyn_comms = %s' % ds.dyn_comms
        for name,formula in ds.dyn_comms.items():
            name = name.rsplit('/',1)[-1]
            print 'In DynamicDS.CreateDynamicCommands(%s.%s.%s())'%(server,dev,name)
            if name.lower() in [s.lower() for s in dir(ds)]:
                print ('Dynamic Command %s Already Exists, skipping!!!'%name)
                continue
            name = ([n for n in ds_class.cmd_list.keys() if n.lower()==name.lower()] or [name])[0]
            ds_class.cmd_list[name] = arg_command if 'ARGS' in formula else void_command
            setattr(ds,name,
                lambda obj,argin=None,cmd_name=name: 
                    (obj._locals.__setitem__('ARGS',argin),
                    str(obj.evalAttr(ds.dyn_comms[obj.get_name()+'/'+cmd_name]))
                    )[1]
                )
    print 'Out of DynamicDS.CreateDynamicCommands(%s)'%(server)
    return
    
class DynamicAttribute(object):
    ''' This class provides a background for dynamic attribute management and interoperativity
        Future subclasses could override the operands of the class to manage quality and date modifications
    '''
    qualityOrder = [PyTango.AttrQuality.ATTR_VALID,PyTango.AttrQuality.ATTR_CHANGING,PyTango.AttrQuality.ATTR_WARNING,
                PyTango.AttrQuality.ATTR_ALARM,PyTango.AttrQuality.ATTR_INVALID]

    def __init__(self,value=None,date=0.,quality=AttrQuality.ATTR_VALID):
        self.value=value
        self.forced=None
        self.date=date
        self.quality=quality
        self.formula=None
        self.compiled = None
        self.states_queue=[]
        self.type=None
        self.keep = True
        self.dependencies = None #it will be initialized to set() in evalAttr
        self.primeOlder=False #
        #self.__add__ = lambda self,other: self.value.__add__(other)

    def getItem(self,index=None):
        if type(self.value) is list or list in self.value.__class__.__bases__:
            return self.value.__getitem__(index)
        elif not index:
            return value
        else:
            raise Exception,'InvalidIndex%sFor%s'%(str(index),str(value))

    def update(self,value,date,quality):
        self.value=value
        self.date=date
        self.quality=quality

    def __add__(self,other):
        result = DynamicAttribute()
        #This method is wrong, qualities are not ordered by criticity!
        result.update(self.value.__add__(other),min([self.date,other.date]),max([self.quality,other.quality]))
        return result.value

    def __repr__(self):
        r='DynamicAttribute{'
        r+='%s: %s, '%('value',str(self.value))
        r+='%s: %s, '%('date',time.ctime(self.date))
        r+='%s: %s, '%('quality',str(self.quality))
        if self.type: r+='%s: %s, '%('type',hasattr(self.type,'labels') and self.type.labels[0] or str(self.type))
        r+='}'
        return r

    def operator(self,op_name,other=None,unary=False,multipleargs=False):
        #print 'operator() called for %s(%s).%s(%s)'%(self.__class__,str(type(self.value)),op_name,other and other.__class__ or '')
        value = self.value
        if value is None:
            if op_name in ['__nonzero__','__int__','__float__','__long__','__complex__']: 
                value = 0
            else:
                return None

        result = DynamicAttribute()
        result.quality,result.date,result.primeOlder=self.quality,self.date,self.primeOlder

        if op_name == '__nonzero__' and type(value) is list:
            op_name = '__len__'
        if hasattr(type(value),op_name): #Be Careful, method from the class and from the instance don't get the same args
            method = getattr(type(value),op_name)
        #elif op_name in value.__class__.__base__.__dict__:
        #    method = value.__class__.__base__.__dict__[op_name]
        else:
            if op_name in ['__eq__','__lt__','__gt__','__ne__','__le__','__ge__'] and '__cmp__' in dir(value):
                if op_name is '__eq__': method = lambda s,x: not bool(s.__cmp__(x))
                if op_name is '__ne__': method = lambda s,x: bool(s.__cmp__(x))
                if op_name is '__lt__': method = lambda s,x: (s.__cmp__(x)<0)
                if op_name is '__le__': method = lambda s,x: (s.__cmp__(x)<=0)
                if op_name is '__gt__': method = lambda s,x: (s.__cmp__(x)>0)
                if op_name is '__ge__': method = lambda s,x: (s.__cmp__(x)>=0)
            else:
                raise Exception,'DynamicAttribute_WrongMethod%sFor%sType==(%s)'% (op_name,str(type(value)),value)

        if unary:
            if value is None and op_name in ['__nonzero__','__int__','__float__','__long__','__complex__']: 
                result.value = method(0)
            else:
                result.value = method(value)
        elif multipleargs:
            args=[value]+list(other)
            result.value = method(*args)
        elif isinstance(other,DynamicAttribute):
            #print str(self),'.',op_name,'(',str(other),')'
            result.quality = self.quality if self.qualityOrder.index(self.quality)>self.qualityOrder.index(other.quality) else other.quality
            result.date = min([self.date,other.date]) if self.primeOlder else max([self.date,other.date])
            result.value = method(value,other.value)
        else:
            result.value = method(value,other)
        if op_name in ['__nonzero__','__int__','__float__','__long__','__complex__','__index__','__len__','__str__',
                    '__eq__','__lt__','__gt__','__ne__','__le__','__ge__']:
            return result.value
        else:
            return result

    def __add__(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __mul__(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __pow__(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __sub__(  self, other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __mod__(  self, other):    return self.operator(inspect.currentframe().f_code.co_name,other)
    def __div__(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __rshift__(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __lshift__(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    #def __truediv__(self,other): return self.value.__class__.__dict__[inspect.currentframe().f_code.co_name](self.value,other)
    def __radd__(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __rmul__(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __rpow__(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __rsub__(  self, other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __rmod__(  self, other):    return self.operator(inspect.currentframe().f_code.co_name,other)
    def __rdiv__(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __rrshift__(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __rlshift__(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    #def __rtruediv__(self,other): return self.value.__class__.__dict__[inspect.currentframe().f_code.co_name](self.value,other)

    def __complex__(self): return self.operator(inspect.currentframe().f_code.co_name,unary=True)
    def __float__(self): return self.operator(inspect.currentframe().f_code.co_name,unary=True)
    def __int__(self): return self.operator(inspect.currentframe().f_code.co_name,unary=True)
    def __long__(self): return self.operator(inspect.currentframe().f_code.co_name,unary=True)
    def __nonzero__(self): return self.operator(inspect.currentframe().f_code.co_name,unary=True)
    def __len__(self): return self.operator(inspect.currentframe().f_code.co_name,unary=True)
    def __str__(self): return self.operator(inspect.currentframe().f_code.co_name,unary=True)

    def __lt__(  self, other): return self.operator(inspect.currentframe().f_code.co_name,other)#lower than
    def __le__(  self, other): return self.operator(inspect.currentframe().f_code.co_name,other)#lower/equal
    def __eq__(  self, other): return self.operator(inspect.currentframe().f_code.co_name,other)#equal
    def __ne__(  self, other): return self.operator(inspect.currentframe().f_code.co_name,other)#not equal
    def __gt__(  self, other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __ge__(  self, other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __cmp__(  self, other): return self.operator(inspect.currentframe().f_code.co_name,other)#returns like strcmp (neg=lower,0=equal,pos=greater)

    #List operations
    def __contains__(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __getitem__(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __getslice__(self,*args): return self.operator(inspect.currentframe().f_code.co_name,args,multipleargs=True)
    def __iter__(self,*args): return self.operator(inspect.currentframe().f_code.co_name,unary=True)
    def next(self,*args): return self.operator(inspect.currentframe().f_code.co_name,unary=True)
    def index(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def append(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)

    def count(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def extend(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def sort(self,other): return self.operator(inspect.currentframe().f_code.co_name,other)

    #Boolean operations
    def __and__(  self, other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __xor__(  self, other): return self.operator(inspect.currentframe().f_code.co_name,other)
    def __or__(  self, other): return self.operator(inspect.currentframe().f_code.co_name,other)

    #Called to implement the unary arithmetic operations (-, +, abs() and ~).
    def __neg__(  self): return self.operator(inspect.currentframe().f_code.co_name,unary=True)
    def __pos__(  self): return self.operator(inspect.currentframe().f_code.co_name,unary=True)
    def __abs__(  self): return self.operator(inspect.currentframe().f_code.co_name,unary=True)
    def __invert__(  self): return self.operator(inspect.currentframe().f_code.co_name,unary=True)
#
#if op = add or sub or mul or div:
#    __rop__ (self,other): These methods are called to implement the binary arithmetic operations (+, -, *, /, %, divmod(), pow(), **, <<, >>, &, ^, |) with reflected (swapped) operands. These functions are only called if the left operand does not support the corresponding operation and the operands are of different types
#
#    __iop__ (self,other): These methods are called to implement the augmented arithmetic operations (+=, -=, *=, /=, //=, %=, **=, <<=, >>=, &=, ^=, |=).
#l.__add__           l.__doc__           l.__gt__            l.__le__            l.__reduce__        l.__setitem__       l.index
#l.__class__         l.__eq__            l.__hash__          l.__len__           l.__reduce_ex__     l.__setslice__      l.insert
#l.__contains__      l.__ge__            l.__iadd__          l.__lt__            l.__repr__          l.__str__           l.pop
#l.__delattr__       l.__getattribute__  l.__imul__          l.__mul__           l.__reversed__      l.append            l.remove
#l.__delitem__       l.__getitem__       l.__init__          l.__ne__            l.__rmul__          l.count             l.reverse
#l.__delslice__      l.__getslice__      l.__iter__          l.__new__           l.__setattr__       l.extend            l.sort


