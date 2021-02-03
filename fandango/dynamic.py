#!/usr/bin/env python
"""
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
        #class PyPLC(PyTango.LatestDeviceImpl):
        class PyPLC(DynamicDS):
        #class PyPLCClass(PyTango.PyDeviceClass):
        class PyPLCClass(DynamicDSClass):

        NOTE: To make your devices Pogoable again you can substitute this change with 2 calls to:
            addTangoInterface(PyPLC,DynamicDS) and addTangoInterface(PyPLCClass,DynamicDSClass)
        This calls must be inserted in the __main__ method of your Class.py file and also at the end of the file.

    5.AND THE __init__ METHOD:
    df __init__(self,cl, name):
        #PyTango.LatestDeviceImpl.__init__(self,cl,name)
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

import PyTango,sys,threading,time,traceback,re,inspect
from PyTango import AttrQuality,DevState

import fandango as fn
import fandango.tango as tango
from fandango.tango.dynattr import *
import fandango.objects as objects
from fandango.excepts import *
from fandango.objects import self_locked, Cached
from fandango.linos import listdir
from fandango.dicts import SortedDict,CaselessDefaultDict,defaultdict,CaselessDict
from fandango.log import Logger,shortstr
import fandango.functional as fun
from fandango.functional import clmatch, clsearch, clsub, kmap, isSequence, \
    isCallable, isMapping, isString, list2lines, time2str, str2time, notNone

#The methods for reading/writing dynamic attributes must be Static for PyTango versions prior to 7.2.2
if getattr(PyTango,'__version_number__',0)<722:
    USE_STATIC_METHODS = True
    print('PyTango Version is %s: fandango.dynamic.USE_STATIC_METHODS = %s' \
        % (PyTango.__version__,USE_STATIC_METHODS))
else: 
    USE_STATIC_METHODS = False

import os
MEM_CHECK = str(os.environ.get('PYMEMCHECK')).lower() in ('yes','true','1')
if MEM_CHECK and 'HEAPY' not in locals():
    try: 
        import guppy
        HEAPY = guppy.hpy()
        HEAPY.setrelheap()    
    except:
        MEM_CHECK=False
else: MEM_CHECK = HEAPY = guppy = None

GARBAGE_COLLECTION=False
GARBAGE,NEW_GARBAGE = None,None
if GARBAGE_COLLECTION:
    import gc
        
#if 'LatestDeviceImpl' not in dir(PyTango): PyTango.LatestDeviceImpl = PyTango.Device_4Impl
if 'DeviceClass' not in dir(PyTango): PyTango.DeviceClass = PyTango.PyDeviceClass

MAX_ARRAY_SIZE = 8192
EVENT_TYPES = '(true|yes|push|archive|[0-9]+)$'

class DynamicDSImpl(PyTango.LatestDeviceImpl,Logger):
    
    EXTENSIONS = dict(list(tango.EXTENSIONS.items()))    
    
    def __init__(self,cl=None,name=None,_globals=None,
            _locals=None, useDynStates=True):
        
        print('> '+'~'*78)
        self.call__init__(PyTango.LatestDeviceImpl,cl,name)
        # Logger must be called after init to use Tango logs properly
        self.call__init__(Logger,name,format='%(levelname)-8s %(asctime)s'
                                        ' %(name)s: %(message)s',level='INFO')
        self.warning( ' in DynamicDSImpl(%s).__init__ ...'%str(name))
        self.trace=False

        #Tango Properties
        self.DynamicAttributes = []
        self.DynamicStates = []
        self.DynamicStatus = []
        self.Lambdas = {}
        self.CheckDependencies = True
        #Internals
        self.dyn_attrs = {}
        self.dyn_types = {}
        self.dyn_states = SortedDict()
        self.dyn_values = {} #<- That's the main cache used for attribute management
            #Should it be caseless?
        self.dyn_qualities = {} #<- It keeps the dynamic qualities variables
        self.variables = {}
        self.state_lock = threading.Lock()
        self.DEFAULT_POLLING_PERIOD = 3000.
        
        self.get_default_properties(update=True)
                        
        print('UseTaurus = %s'%getattr(self,'UseTaurus',False))
        if getattr(self,'UseTaurus',False): self.UseTaurus = bool(tango.loadTaurus())
        
        # Internal object references
        self._prepared = False
        self.myClass = None
        
        ## This dictionary stores XAttr valid arguments and AttributeProxy/TauAttribute objects
        self._external_attributes = CaselessDict()
        self._external_listeners = CaselessDict() #CaselessDefaultDict(set)
        self._external_commands = CaselessDict()

        self._events_paused = False
        self._events_queue = objects.Queue.Queue()
        self._events_lock = threading.Lock()        

        self.time0 = time.time() #<< Used by child devices to check startup time
        self.mem0 = None #MemUsage at startup, recorded at first Init()
        self.simulationMode = False #If it is enabled the ForceAttr command overwrites the values of dyn_values
        self.clientLock=False #TODO: This flag allows clients to control the device edition, using isLocked(), Lock() and Unlock()
        self.lastAttributeValue = None #TODO: This variable will be used to keep value/time/quality of the last attribute read using a DeviceProxy
        self.last_state_exception = ''
        self.last_state_change = 0
        self.last_attr_exception = None
        self._init_count = 0
        self._hook_epoch = 0
        self._cycle_start = 0
        self._total_usage = 0
        self._last_period = {}
        self._last_read = {}
        self._read_times = {}
        self._read_count = defaultdict(int)
        self._eval_times = {}
        self._polled_attr_ = {}
        self.GARBAGE = []
        
        self.init_locals(_globals,_locals)
        
        self.useDynStates = useDynStates
        if self.useDynStates:
            self.warning('useDynamicStates is set, '
                'disabling automatic State generation by attribute config.'
                'States fixed with set/get_state will continue working.')
            self.State = self.rawState
            self.dev_state = self.rawState
            
        print('< '+'~'*78)        
        
    def init_locals(self, _globals = None, _locals = None):
        ##Local variables and methods to be bound for the eval methods
        
        self._globals={} #globals().copy()
        if _globals: self._globals.update(_globals)
        self._locals = {}
                
        # Methods to access other device servers
        self._locals['Attr'] = lambda _name: self.getAttr(_name)
        self._locals['ATTR'] = lambda _name: self.getAttr(_name)
        self._locals['XAttr'] = lambda _name,default=None: self.getXAttr(_name,default=default)
        self._locals['XATTR'] = lambda _name,default=None: self.getXAttr(_name,default=default)
        self._locals['WATTR'] = lambda _name,value: self.getXAttr(_name,wvalue=value,write=True)
        self._locals['COMM'] = lambda _name,_argin=None,feedback=None,expected=None: self.getXCommand(_name,_argin,feedback,expected)
        self._locals['XDEV'] = lambda _name: self.getXDevice(_name)
        
        # Methods to manipulate internal variables
        self._locals['ForceAttr'] = lambda a,v=None: self.ForceAttr(a,v)
        self._locals['VAR'] = (lambda a=None,v=None,default=None,WRITE=None: 
                              self.ForceVar((a or self._locals.get('ATTRIBUTE')),VALUE=v,default=default,WRITE=WRITE))
        self._locals['VARS'] = self.variables
        self._locals['GET'] = (lambda a,default=None: 
                                self.ForceVar(a,default=default) 
                                if (a in self.variables or default is not None) 
                                else self._locals.get(a,default))
        self._locals['SET'] = lambda a,v: self.ForceVar(a,v)
        
        #self._locals['RWVAR'] = (lambda read_exp=(lambda arg=NAME:self.ForceVar(arg)),
                                #write_exp=(lambda arg=NAME,val=VALUE:self.ForceVar(arg,val)),
                                #aname=NAME, 
                                #_read=READ: 
                                    #(_read and read_exp or write_exp))
                                    
        self._locals['SetStatus'] = lambda status: [True,self.set_status(status)]
        self._locals['Add2Status'] = lambda status: [True,self.set_status(self.get_status()+status)]
        
        # Advance methods for evaluating formulas
        self._locals['self'] = self
        self._locals['EVAL'] = lambda formula: self.evaluateFormula(formula)
        self._locals['MATCH'] = lambda expr,cad: fun.matchCl(expr,cad)
        self._locals['DELAY'] = lambda secs: fn.wait(secs)
        self._locals['FILE'] = lambda filename: DynamicDS.open_file(filename,device=self) #This command will allow to setup attributes from config files
        self._locals['FORMULA'] = self.get_attr_formula
        self._locals['MODELS'] = self.get_attr_models
        self._locals['time2str'] = fn.time2str
        self._locals['ctime2time'] = fn.ctime2time
        self._locals['now'] = fn.now
        for k in dir(fn.functional):
            if '2' in k or k.startswith('to') or k.startswith('is'):
                self._locals[k] = getattr(fn.functional,k)
        
        # Methods for getting/writing properties
        self._locals['PGET'] = (
            lambda property,update=False: (
                self.get_device_property(property,update)))
        self._locals['PSET'] = (
            lambda property,value: (
                self._db.put_device_property(self.get_name(),
                    {property:[value]}),setattr(self,property,value)))
        self._locals['PROPERTY'] = self._locals['PGET']
        self._locals['WPROPERTY'] = self._locals['PSET']
        
        # Methods for managing attribute types
        self._locals['DYN'] = DynamicAttribute
        self._locals['SCALAR'] = lambda t,v: castDynamicType(dims=0,klass=t,value=v)
        self._locals['SPECTRUM'] = lambda t,v: castDynamicType(dims=1,klass=t,value=v)
        self._locals['IMAGE'] = lambda t,v: castDynamicType(dims=2,klass=t,value=v)

        if MEM_CHECK:
            self._locals['guppy'] = guppy
            self._locals['heapy'] = HEAPY
        [self._locals.__setitem__(str(quality),quality) for quality in AttrQuality.values.values()]
        [self._locals.__setitem__(k,dst.pytype) for k,dst in DynamicDSTypes.items()]
        
        #Adding states for convenience evaluation
        self.TangoStates = dict((str(v),v) for k,v in PyTango.DevState.values.items())
        self._locals.update(self.TangoStates)
        
        if _locals: 
            self._locals.update(_locals) #New submitted methods have priority over the old ones
            
    def locals(self,key=None):
        return self._locals if key is None else self._locals.get(key)
    
    def get_init_count(self):
        return self._init_count
        
    def get_parent_class(self):
        return type(self).mro()[type(self).mro().index(DynamicDSImpl)+1]
    
    def reset_memleak(self):
        self.mem0 = self.getMemUsage()
        self.time0 = time.time()

    def prepare_DynDS(self):
        """
        This code is placed here because its proper execution cannot be guaranteed during init_device().
        """
        try:
            if self.myClass is None:
                self.myClass = self.get_device_class()
            #Check polled to be repeated here but using admin (not allowed at Init()); not needed with Tango8 but needed again in Tango9!! (sigh)
            #if getattr(PyTango,'__version_number__',0) < 804:
            #self.check_polled_attributes(use_admin=True) ###@TODO REMOVE!!! IT IS CRASHING DEVICES IN TANGO9!!
        except Exception,e:
            print('prepare_DynDS failed!: %s' % str(e).replace('\n',';')) #traceback.format_exc()
        finally:
            self._prepared = True
        return    
    
    @staticmethod
    def get_db():
        DynamicDS._db = getattr(DynamicDS,'_db',None) or PyTango.Util.instance().get_database()
        return DynamicDS._db
    
    def get_default_properties(self,update=False):        
        """ Setting default values for Class/Device properties """
        dct = {}
        for d in (DynamicDSClass.class_property_list,
                  DynamicDSClass.device_property_list):
            
            for prop,value in d.items():
                if not hasattr(self,prop): 
                    if 'Array' in str(value[0]): 
                        value = value[-1]
                    elif (value and fun.isSequence(value[-1])): 
                        value = value[-1][0]
                    else:
                        value = value and value[-1]
                    dct[prop] = value
                    
                self.debug('default %s: %s' % (prop,value))
        if update:
            for prop,value in dct.items():
                setattr(self,prop,value)
            
        return dct
    
    def get_device_property(self,prop,update=False,value=None,compact=True):
        """
        Method used by PROPERTY command within formulas to obtain
        values of own properties stored in the database.
        """
        if update or not hasattr(self,prop) or value is not None:
            if value is None:
                value = self._db.get_device_property(self.get_name(),[prop])
                value = self.check_property_extensions(prop,value[prop])
            setattr(self,prop,value)
            
        value = getattr(self,prop)
        if compact and fn.isSequence(value) and len(value)==1:
            return value[0]
        else:
            return value      

    def get_DynDS_properties(self,db=None):
        """
        ## THIS FUNCTION IS USED FROM updateDynamicAttributes
        It forces DynamicDevice properties reading using the Database device.
        It has to be used as subclasses may not include all Dynamic* properties in their class generation.
        It is used by self.updateDynamicAttributes() and required in PyTango<3.0.4
        """
        print('#'*80)
        self.warning('In get_DynDS_properties(): updating DynamicDS properties from Database')
        
        #It will reload all subclass specific properties (with its own default values)
        self.get_device_properties(self.get_device_class()) 
        self._db = db or self.get_db()
        
        if self.LogLevel: 
            try: self.setLogLevel(self.LogLevel)
            except: self.warning('Unable to setLogLevel(%s)'%self.LogLevel)
            
        #Loading DynamicDS specific properties (from Class and Device)
        for method,target,config in (
                (self._db.get_class_property,
                    self.get_device_class().get_name(),
                    DynamicDSClass.class_property_list),
                (self._db.get_device_property,self.get_name(),
                    dict(list(DynamicDSClass.device_property_list.items())
                     +[('polled_attr',[PyTango.DevVarStringArray,[]])])),
            ):
            # Default property values already loaded in __init__; 
            # here we are just updating
            props = [(prop,value) for prop,value in 
                     method(target,list(config)).items() if value]
            
            for prop,value in props:
                self.warning('get_DynDS_properties(%s,%s)' % (prop,value))
                
                #Type of each property is adapted to python types
                dstype = DynamicDSTypes.get(str(config[prop][0]),
                                            DynamicDSType('','',pytype=list))
                try: 
                    value = dstype.pytype(value if 
                            dstype.dimx>1 or dstype.dimy>1 else value[0])
                except Exception,e:
                    self.warning('In get_DynDS_properties: %s(%s).%s '
                            'property parsing failed: %s -> %s' % (
                                type(self),self.get_name(),value,e))
                    value = (config[prop][-1] if dstype.dimx>1 or dstype.dimy>1 
                                else config[prop][-1][0])
                    
                if prop=='polled_attr': 
                  self._polled_attr_ = tango.get_polled_attrs(value)
                  
                elif prop=='StoredLambdas':
                    self.Lambdas = dict(l.split(':',1) for l in value 
                                        if ':' in l)
                    try: 
                        self.Lambdas = dict((k,eval(v)) for k,v in self.Lambdas.items())
                    except: 
                        traceback.print_exc()
                  
                else:
                    #APPLYING @COPY/@FILE property extensions
                    value = self.check_property_extensions(prop,value)
                    if prop.lower() == 'checkdependencies':
                        if isSequence(value) and len(value)==1:
                            value = value[0]
                        if isSequence(value):
                            value = dict(t.split(':',1) for t in value)
                        elif str(value).lower().strip() in ('no','false',''):
                            value = False
                    setattr(self,prop,value)
                  
            self.info('In get_DynDS_properties: %s(%s) properties are: %s' 
                      % (type(self),self.get_name(),[t[0] for t in props]))
            [self.info('\t'+self.get_name()+'.'+str(p)+'='
                       +str(getattr(self,p,None))) for p in config]
            
        if self.UseTaurus:
            self.UseTaurus = (tango.TAU or tango.loadTaurus()) and self.UseTaurus
            
        if self.LoadFromFile:
            DynamicDS.load_from_file(device=self)
            
        #Adding Static Attributes if defined in the SubClass
        if getattr(self,'StaticAttributes',None):
            self.parseStaticAttributes(add=True,keep=True)
            
        return
    
    def parseStaticAttributes(self,add=True,keep=True):
        """ Parsing StaticAttributes if defined. """
        attrs = []
        dynamics = [d.split('=')[0].strip().lower() 
                    for d in self.DynamicAttributes]
        if hasattr(self,'StaticAttributes'): 
            for a in self.StaticAttributes:
                aname = a.split('#')[0].split('=')[0].strip()
                if aname:
                    attrs.append(aname)
                    if aname.lower() in dynamics:
                        self.info('StaticAttribute %s overriden by '
                                  'DynamicAttributes Property'%(aname))
                    else:
                        self.debug('Adding StaticAttribute %s to '
                                   'DynamicAttributes list'%(aname))
                        self.DynamicAttributes.append(a)
                if keep:
                    # Adds to KeepAttributes if default value is overriden,
                    # works if dyn_attr is called after init_device (Tango7)
                    if not any(k.lower()==aname.lower() for k in 
                               self.KeepAttributes):
                        self.KeepAttributes.append(aname)
                    self.KeepAttributes = [k for k in self.KeepAttributes 
                                           if 'no'!=k.lower().strip()]
            return attrs
        else: 
            return []   
    
    @staticmethod
    def check_property_extensions(prop,value,db=None,extensions=EXTENSIONS):
        #THIS METHOD PROVIDES EXTENSIONS AND MULTILINE PARSING!
        return tango.check_property_extensions(prop,value,
            extensions=DynamicDS.EXTENSIONS,db=DynamicDS.get_db(),
            filters=DynamicDSClass.device_property_list)

    def check_polled_attributes(self,db=None,new_attr={},use_admin=False):
        '''
        If a PolledAttribute is removed of the Attributes declaration it can lead to SegmentationFault at Device Startup.
        polled_attr property must be verified to avoid that.
        
        The method .get_device_class() cannot be called to get the attr_list value for this class,
        therefore new_attr must be used to add to the valid attributes any attribute added by subclasses
        Polling configuration configured through properties has preference over the hard-coded values; 
        but it seems that Tango does not always update that and polling periods have to be updated.
        
        Must be called twice (solved in PyTango8)
         - at dyn_attr to remove unwanted attributes from polled_attr
         - at prepareDynDS to update polling periods using the admin device
         
        '''
        self.warning('In check_polled_attributes(%s,use_admin=%s)'%(new_attr,use_admin))
        my_name = self.get_name()
        if use_admin:
            U = PyTango.Util.instance()
            admin = U.get_dserver_device()
        else:
            self._db = getattr(self,'_db',None) or PyTango.Database()
        new_attr = dict.fromkeys(new_attr,self.DEFAULT_POLLING_PERIOD) if isinstance(new_attr,list) else new_attr
        dyn_attrs = list(set(map(str.lower,['state','status']+self.dyn_attrs.keys()+new_attr.keys())))
        pattrs = self.get_polled_attrs()
        npattrs = []
        self.info('Already polled: '+str(pattrs))
        #First: propagate all polled_attrs if they appear in the new attribute list or remove them if don't
        for att,period in pattrs.items():
            if att in npattrs: continue #remove duplicated
            elif att.lower() in dyn_attrs: 
                (npattrs.append(att.lower()),npattrs.append(period))
            else: 
                self.info('Removing Attribute %s from %s.polled_attr Property' % (att,my_name))
                if use_admin:
                    try: admin.rem_obj_polling([my_name,'attribute',att])
                    except: print(traceback.format_exc())
        #Second: add new attributes to the list of attributes to configure; attributes where value is None will not be polled
        for n,v in new_attr.iteritems():
            if n.lower() not in npattrs and v:
                (npattrs.append(n.lower()),npattrs.append(v))
                self.info('Attribute %s added to %s.polled_attr Property' % (n,my_name))
        #Third: apply the new configuration
        if use_admin:
            for i in range(len(npattrs))[::2]:
                try:
                    att,period = npattrs[i],npattrs[i+1]
                    if att not in pattrs:
                        admin.add_obj_polling([[int(period)],[my_name,'attribute',att]])
                    else:
                        admin.upd_obj_polling_period([[int(period)],[my_name,'attribute',att]])
                except:
                    print('Unable to set %s polling' % (npattrs[i]))
                    print(traceback.format_exc())
        else:
           self.info('Updating polled_attr: %s'%(npattrs,))
           self._db.put_device_property(my_name,{'polled_attr':npattrs})
        self.info('Out of check_polled_attributes ...')
        
    def updateDynamicAttributes(self):
        """Forces dynamic attributes update from properties.
        @warning : It will DELETE all attributes that does not appear in DynamicAttributes property or StaticAttributes list!
        """
        self.warning('In updateDynamicAttributes(): reloading DynamicDS properties from Database')
        self.get_DynDS_properties()
        
        ##All attributes managed with dyn_attr() that does not appear 
        # in DynamicAttributes or StaticAttributes list will be removed!
        attrs_list = [name.split('=',1)[0].strip() for name in 
            (self.DynamicAttributes + (getattr(self,'StaticAttributes',None) 
                                       or []))]
        for a in self.dyn_attrs:
            if a not in attrs_list:
                self.warning('DynamicDS.updateDynamicAttributes(): '
                    'Removing Attribute!: %sn not in [%s]' % (a,attrs_list))
                try:
                    self.remove_attribute(a)
                except Exception,e:
                    self.error('Unable to remove attribute %s: %s'%(a,str(e)))
        DynamicDS.dyn_attr(self)
        
        #Updating DynamicCommands (just update of formulas)
        try: 
            CreateDynamicCommands(type(self),type(self.get_device_class()))
        except: 
            print('CreateDynamicCommands failed: %s'%traceback.format_exc())        

###############################################################################
    
class DynamicDSAttrs(DynamicDSImpl):

    
    dyn_comms = {} # To be defined here, not at __init__ nor init_device as it is shared by all instances


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
        
        ## Lambdas not used because using staticmethods; @TODO: test how it works in PyTango 7.1.2!
        #read_method = lambda attr,fire_event=True,s=self: s.read_dyn_attr(attr,fire_event)
        #write_method = lambda attr,fire_event=True,s=self: s.write_dyn_attr(attr,fire_event)

        if not hasattr(self,'DynamicStates'): self.error('DynamicDS property NOT INITIALIZED!')
            
        if self.DynamicStates:
            self.dyn_states = SortedDict()
            def _add_state_formula(st,formula):
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
                    _add_state_formula(st,formula)
                elif st == 'STATE':
                    [_add_state_formula(s,'int(%s)==int(%s)'%(s,formula))
                        for s in self.TangoStates if not any(l.startswith(s) for l in self.DynamicStates)]
                else:
                    self.debug( self.get_name()+".dyn.attr(): Unknown State: %s"%(line,))
        
        #Attributes may be added to polling if having Events
        new_polled_attrs = CaselessDict(self.get_polled_attrs().items())
        self.info('In %s.dyn_attr(): inspecting %d attributes ...' %(self.get_name(),len(self.DynamicAttributes)))
        for line in self.DynamicAttributes:
            
            if not line.strip() or line.strip().startswith('#'): continue
            fields=[]
            # The character '#' is used for comments in Attributes specification
            if '#' in line: fields = (line.split('#')[0]).split('=',1)
            else: fields = line.split('=',1)
            
            if fields is None or len(fields) is 1 or '' in fields:
                self.warning(self.get_name()+".dyn_attr(): wrong format in DynamicAttributes Property!, "+line)
                continue

            ###################################################################
            aname,formula=fields[0].strip(),fields[1].strip()
            self.info(self.get_name()+".dyn_attr(): new Attribute '"+aname+"' = '"+formula+"'")
            
            ## How to compare existing formulas?
            # Strip the typename from the beginning (so all typenames must be identified!)
            # .strip() spaces and compare
            # if the code is the same ... don't touch anything
            # if the code or the type changes ... remove the attribute!
            # dyn_attr() will create the attributes only if they don't exist.
            aname = self.get_attr_name(aname)
            if not any(k.lower()==aname.lower() for k in self.dyn_values):
                #if aname not in self.dyn_values:
                create = True
                self.dyn_values[aname]=DynamicAttribute(name=aname)
                self.dyn_types[aname]=None
            else: 
                self.info('\tAttribute %s already exists'%(aname,))
                create = False

            #These 3 options may vary depending on PyTango>3; 
            #don't remove them from the code yet
            if 0: 
                #Works on PyTango7
                _is_allowed = (lambda s,req_type,a=aname: 
                            type(self).is_dyn_allowed(s,req_type,a))
            elif 0:
                #May trigger exceptions because attr_name is None
                _is_allowed = self.is_dyn_allowed 
            else:
                #Works on PyTango8
                def _is_allowed(req_type, attr_name=aname,s=self):
                    return s.is_dyn_allowed(req_type,attr_name)
                _is_allowed.__name__ = 'is_%s_allowed'%aname.lower()
                setattr(self,_is_allowed.__name__,_is_allowed)
            
            max_size = hasattr(self,'DynamicSpectrumSize') and self.DynamicSpectrumSize
            AttrType = (PyTango.AttrWriteType.READ_WRITE 
                            if 'WRITE' in fun.re.split('[\[\(\]\)\ =,\+]',formula) 
                            else PyTango.AttrWriteType.READ)
            
            for typename,dyntype in DynamicDSTypes.items():
                
                if dyntype.match(formula):
                    
                    self.debug(self.get_name()+".dyn_attr():  '"+line+ "' matches " + typename + "=" + str(dyntype.labels))
                    if formula.startswith(typename+'('): #DevULong should not match DevULong64
                        formula=formula.lstrip(typename)
                    self.debug('Creating attribute (%s,%s,dimx=%s,%s)'%(aname,dyntype.tangotype,dyntype.dimx,AttrType))
                    
                    if dyntype.dimx==1:
                        if (create): 
                            self.add_attribute(PyTango.Attr(aname,dyntype.tangotype, AttrType),
                                self.read_dyn_attr,self.write_dyn_attr,_is_allowed)
                                #self.read_dyn_attr,self.write_dyn_attr,self.is_dyn_allowed)
                    elif dyntype.dimy==1:
                        if (create): 
                            self.add_attribute(PyTango.SpectrumAttr(aname,dyntype.tangotype, 
                                                        AttrType,max_size or dyntype.dimx),
                                self.read_dyn_attr,self.write_dyn_attr,_is_allowed)
                                #self.read_dyn_attr,self.write_dyn_attr,self.is_dyn_allowed)
                    else:
                        if (create): 
                            self.add_attribute(PyTango.ImageAttr(aname,dyntype.tangotype, AttrType,
                                                max_size or dyntype.dimx,max_size or dyntype.dimy),
                                self.read_dyn_attr,self.write_dyn_attr,_is_allowed)
                                #self.read_dyn_attr,self.write_dyn_attr,self.is_dyn_allowed)
                    
                    self.dyn_types[aname]=dyntype
                    break

            if not self.dyn_types[aname]:
                self.debug("DynamicDS.dyn_attr(...): Type not matched for '"+line+"', using DevDouble by default"    )
                if max(map(formula.startswith,['list(','['])):
                        dyntype = DynamicDSTypes['DevVarDoubleArray']
                        self.info('Creating attribute (%s,%s,dimx=%s,%s)'%(aname,dyntype.tangotype,dyntype.dimx,AttrType))
                        if (create): self.add_attribute(PyTango.SpectrumAttr(aname,dyntype.tangotype, AttrType,max_size or dyntype.dimx), \
                            self.read_dyn_attr,self.write_dyn_attr,_is_allowed)
                            #self.read_dyn_attr,self.write_dyn_attr,self.is_dyn_allowed)
                else:
                    dyntype = DynamicDSTypes['DevDouble']
                    self.debug('Creating attribute (%s,%s,dimx=%s,%s)'%(aname,dyntype.tangotype,dyntype.dimx,AttrType))
                    if (create): 
                        self.add_attribute(PyTango.Attr(aname,PyTango.ArgType.DevDouble, AttrType), \
                            self.read_dyn_attr,self.write_dyn_attr,_is_allowed)
                        #self.read_dyn_attr,self.write_dyn_attr,self.is_dyn_allowed)
                self.dyn_types[aname]=dyntype

            #print 'Type of Dynamic Attribute "',aname,'=',formula,'" is "',str(self.dyn_types[aname].labels),'"'
            self.dyn_attrs[aname]=formula
            #TODO: Some day self.dyn_values should substitute both dyn_attrs and dyn_types
            self.dyn_values[aname].formula=formula
            try: 
                self.dyn_values[aname].compiled=compile(formula.strip(),'<string>','eval')
            except: 
                self.error(traceback.format_exc())
            self.dyn_values[aname].type=self.dyn_types[aname]

            #Adding attributes to DynamicStates queue:
            for k,v in self.dyn_states.items():
                if aname in v['formula']:
                    #self.dyn_values[aname]=None
                    self.dyn_values[aname].states_queue.append(k)
                    self.info("DynamicDS.dyn_attr(...): Attribute %s added to attributes queue for State %s"%(aname,k))
                    
            #Setting up change events and caching:
            events = self.check_attribute_events(aname) 
            self.dyn_values[aname].keep = events or (self.KeepAttributes and 
                (not 'no' in self.KeepAttributes) and any(q.lower() 
                in self.KeepAttributes for q in [aname,'*','yes','true']))
                
            if events:
                self._locals[aname] = None
                if create and events:
                    # THIS IS CONFIGURING EVENTS TO BE "MANUAL", 
                    # pushed=True, filtered=False (ignore Jive settings)
                    self.set_change_event(aname.lower(),True,False)
                    if 'archive' in events:
                        self.set_archive_event(aname.lower(),True,False)
                        
                if fun.isNumber(events) and aname not in new_polled_attrs:
                    new_polled_attrs[aname] = int(events)
                    
            elif self.dyn_values[aname].keep:
                self._locals[aname] = None
                    
            ## END OF ATTR CONFIG LOOP
                
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
                            self.info('There is a Quality for this attribute!:'
                                +str((aname,exp,shortstr(value))))
                            # It will replace $ in the formula for all strings 
                            # matched by .* in the expression
                            for group in (match.groups()): 
                                # e.g: (.*)_VAL=ATTR_ALARM if ATTR('$_ALRM') ... 
                                # => RF_VAL=ATTR_ALARM if ATTR('RF_ALRM') ...
                                value=value.replace('$',group,1) 
                                
                            self.dyn_qualities[aname.lower()] = value
                    except Exception,e:
                        self.warning('In dyn_attr(qualities), re.match(%s(%s),'
                          '%s(%s)) failed' % (type(exp),exp,type(aname),aname))
                        print(traceback.format_exc())
                        
        if self.CheckDependencies:
            [self.check_dependencies(aname) for aname in self.dyn_values]
                        
        ##Setting up state events:
        #THESE SETTINGS ARE STILL NEEDED IN TANGO >= 7
        for x in ('state','memusage',):
            # Both State and MemUsage shall be polled to have events!
            events = self.check_attribute_events(x)
            if events and x not in new_polled_attrs:
                #To be added at next restart
                self.warning('%s events will be polled (%s)'%(x,events))
                new_polled_attrs[x] = int(events) if fun.isNumber(events) \
                    else self.DEFAULT_POLLING_PERIOD
            if x!='state': 
                self.set_change_event(x,True,False)
                if 'archive' in events:
                    self.set_archive_event(x,True,False)
        try:
            self.check_polled_attributes(new_attr=new_polled_attrs)
        except:
            print('DynamicDS.dyn_attr( ... ), unable to set polling for (%s):'
                  ' \n%s'%(new_polled_attrs,traceback.format_exc()))
        
        print('DynamicDS.dyn_attr( ... ), finished. '
                'Attributes ready to accept request ...')

    #dyn_attr MUST be an static method, to avoid attribute mismatching (self will be always passed as argument)
    dyn_attr=staticmethod(dyn_attr)         
        
    #------------------------------------------------------------------------------------------------------
    #   Attribute creators and read_/write_ related methods
    #------------------------------------------------------------------------------------------------------

    def is_dyn_allowed(self,req_type,attr_name=''):
        return (time.time()-self.time0) > 1e-3*self.StartupDelay
    
    @Cached(depth=1024,expire=15.)
    def check_attribute_events(self,aname,poll=False):
        """
        It parses the contents of UseEvents property, that can be:
         - [ 'yes/no/true/false' ]
         - [  'archive|change' ]
         - [ 'attr1', 'attr2:push', 'attr3:archive' ]
        
        In the first two cases, the value specified applies to all attributes.
        
        In the last case, each config applies only to the specified attribute.
        
        Setting yes/true will enable only change events if configured from Jive.
        
        Setting archive will enable both change and archive events.
        
        Setting push will also enable the pushing from code.
        """
        self.UseEvents = filter(bool,
                (u.split('#')[0].strip().lower() for u in self.UseEvents))
        self.debug('check_attribute_events(%s,%s,%s)'
                   %(aname,poll,self.UseEvents))

        if self._events_paused:
            self.warning('Events paused externally!')
            return '' #False
        if not len(self.UseEvents) or self.UseEvents[0] in ('no','false'):
            return ''
        elif clmatch('state$',aname):
            return 'true'
        elif clmatch(EVENT_TYPES,self.UseEvents[0]):
            return self.UseEvents[0]

        for s in self.UseEvents:
            s,e = s.split(':',1) if ':' in s else (s,'True')
            if clmatch(s,aname):
                return e if clmatch(EVENT_TYPES,e.strip()) else ''
            
        return ''
    
    @Cached(depth=1024,expire=15.)
    def check_events_config(self,aname):
        cabs,crel = 0,0
        try:
            ac = self.get_attribute_config_3(aname)[0]
            try: 
                cabs = float(ac.event_prop.ch_event.abs_change)
            except: 
                pass
            try: 
                crel = float(ac.event_prop.ch_event.rel_change)
            except: 
                pass
        except:
            pass
        return cabs,crel
    
    def check_changed_event(self,aname,new_value,events=None,config=None):
        """
        Events will be always pushed if array,state,bool,string values change
        If UseEvents=always, it will be always pushed
        if UseEvents=push, will always push on any change, ignoring config
        if UseEvents=True, then Tango DB config prevails, and is checked
        """
        aname = self.get_attr_name(aname)
        
        if aname not in self.dyn_values: 
            self.warning('Unknown %s attribute!'%aname)
            return False
        if self._events_paused:
            self.warning('Events paused externally!')
            return False
        
        try:
            v = self.dyn_values[aname].value
            new_value = getattr(new_value,'value',new_value)
            
            events = events or self.check_attribute_events(aname)
            
            self.info('In check_changed_event(%s,%s,%s): %s!=%s'
                % (aname,events,config,shortstr(v),shortstr(new_value) ))
            if v is None:
                self.info('In check_changed_event(%s,%s): first value read!'
                          %(aname,shortstr(new_value)))
                return True
            
            elif events and clsearch('always',events):
                return True
            
            elif fun.isSequence(new_value) or fun.isSequence(v):
                # Event pushed ignoring cabs/crel config!
                v,new_value = fun.notNone(v,[]),fun.notNone(new_value,[])
                
                changed = len(v)!=len(new_value) \
                    or any(v!=vv for v,vv in zip(v,new_value))
                
                self.info('In check_changed_event(%s,%s): changed = %s'
                    %(aname,shortstr(new_value),changed))
                
                return changed
            
            else:
                try: 
                    v,new_value = (float(v) if v is not None else None),\
                                    float(new_value)
                except Exception,e: 
                    self.debug(str(e))
                    self.info('In check_changed_event(%s): '
                              'non-numeric, checking raw diff (%s,%s)'
                              %(aname,shortstr(v),shortstr(new_value)))
                    try:
                        return v!=new_value #and (cabs>0 or crel>0)
                    except:
                        return str(v)!=str(new_value)
                
                if clsearch('push',events): #UseEvents = push #on any change
                    #cabs,crel = 1e-12,1e-12
                    if v != new_value: #It should be only if UseEvents=push
                        self.info('In check_changed_event(%s,%s): '
                            'push on any change'%(aname,shortstr(new_value)))
                        return True                    
                
                #If events = True or number
                cabs,crel = config or self.check_events_config(aname)
                
                if cabs>0 and not v-cabs<new_value<v+cabs: 
                    self.info('In check_changed_event(%s,%s): absolute change!'
                              %(aname,shortstr(new_value)))
                    return True
                
                elif crel>0 and not v*(1-crel/100.)<new_value<v*(1+crel/100.): 
                    self.info('In check_changed_event(%s,%s): relative change!'
                              %(aname,shortstr(new_value)))
                    return True
                
                #elif v != new_value: #It should be only if UseEvents=push
                    #self.info('In check_changed_event(%s,%s): '
                        #'push on any change'%(aname,shortstr(new_value)))
                    #return True
                
                else: 
                    self.debug('In check_changed_event(%s,%s): nothing changed'
                               %(aname,shortstr(new_value)))
                    return False
                
        except: #Needed to prevent fails if attribute_config_3 is not available
            print(traceback.format_exc())
            
        return False
    
    @Cached
    def check_dependencies(self, aname):
        #Checking attribute dependencies
        aname = self.get_attr_name(aname)
        if aname not in self.dyn_values:
            aname,formula,compiled = self.get_attr_formula(aname,full=True)
            
        if self.CheckDependencies and aname in self.dyn_values:
            
            if self.dyn_values[aname].dependencies is None:
                self.debug("In evalAttr ... setting dependencies")
                self.dyn_values[aname].dependencies = set()
                a = aname.lower().strip()
                formula = self.dyn_values[aname].formula
                fs = (formula+'\n'+self.dyn_qualities.get(a,'')).lower()

                # Get dependencies from existing attributes
                for k,v in self.dyn_values.items():
                    ks = k.lower().strip()
                    if a==ks: 
                        continue
                    if ks in fun.re.split("[^'\"_0-9a-zA-Z]",fs): 
                        #fun.searchCl("(^|[^'\"_0-9a-z])%s($|[^'\"_0-9a-z])"%k,formula):
                        self.dyn_values[aname].dependencies.add(k) 
                        #Dependencies are case sensitive
                        self.dyn_values[k].keep = True
                        
                if isMapping(self.CheckDependencies):
                    for k,v in self.CheckDependencies.items():
                        if clmatch(k,aname) or clmatch(k,formula):
                            self.dyn_values[aname].dependencies.add(v)
            
            r = self.dyn_values[aname].dependencies
        else:
            r = None
        self.debug('check_dependencies(%s): %s' % (aname,r))
        return r      
        
    def update_dependencies(self, aname = None):
        ##Checking attribute dependencies
        # dependencies assigned at dyn_attr by self.check_dependencies()
        #Updating Last Attribute Values
        now = time.time()
        changed = False
        aname = self.get_attr_name(aname)
        for k in (self.dyn_values[aname].dependencies or []):
            self.debug("In update_dependencies(%s): "
                " (%s,last read at %s, KeepTime is %s)"
                %(aname,k,self._last_read.get(k,0),self.KeepTime))
            
            old = self._locals.get(k)
            updated = self.dyn_values[k].updated
            if self.KeepTime and (
                    not updated or now>(updated+(self.KeepTime/1e3))):
                self.debug("In update_dependencies(%s): read value"%(k,))
                if USE_STATIC_METHODS: 
                    self.read_dyn_attr(self,tango.fakeAttributeValue(k))
                else: 
                    self.read_dyn_attr(tango.fakeAttributeValue(k))
                
            v = self.dyn_values[k]
            
            if (k.lower().strip()!=aname.lower().strip() 
                    and isinstance(v.value,Exception)):
                self.warning('evalAttr(%s): An exception is rethrowed '
                             'from attribute %s'%(aname,k))
                print(k,aname,v.value)
                #Exceptions are passed to dependent attributes
                raise RethrownException(v.value) 
            else: 
                self._locals[k]=v.value #.value
                
            try:
                if self._locals[k] != old:
                    changed = True
            except:
                changed = True
                
        return changed      

    #@Catched #Catched decorator is not compatible with PyTango_Throw_Exception
    @self_locked
    def read_dyn_attr(self,attr,fire_event=True):
        """
        Method to evaluate attributes from external clients.
        Internally, evalAttr is used instead, triggering push_event if needed
        """
        #if not USE_STATIC_METHODS: self = self.myClass.DynDev
        attr = tango.fakeAttributeValue(attr) if isString(attr) else attr
        aname = self.get_attr_name(attr.get_name())
        result = None
        tstart=time.time()
        self.debug("DynamicDS(%s)::read_dyn_atr(%s), entering at %s\n%s"
                   % (self.get_name(),aname,time2str(tstart),'<'*80))

        v = self.get_attr_cache(aname)
        if v is not None:
            self.debug('Returning cached (%s) value for %s: %s(%s)'%(
                time2str(v.updated),aname,type(v.value),shortstr(v.value)))
            return attr.set_value_date_quality(v.value,v.date,v.quality)            
            
        try:
            self.debug("DynamicDS(%s)::read_dyn_atr(%s) => evalAttr()"
                   % (self.get_name(),aname))
            result = self.evalAttr(aname) #push is done here
            quality = getattr(result,'quality',
                              self.get_attr_quality(aname,result))
            date = self.get_attr_date(aname,result)
            result = self.dyn_types[aname].pytype(result)
            attr.set_value_date_quality(result,date,quality)
                
            text_result = (type(result) is list and result and '%s[%s]'
                           %(type(result[0]),len(result))) or str(result)
            now=time.time()
            self._last_period[aname]=now-self._last_read.get(aname,0)
            self._last_read[aname]=now
            self._read_times[aname]=now-self._hook_epoch
            self._total_usage += now-self._hook_epoch
            self.debug('DynamicDS('+self.get_name()+
                ").read_dyn_attr("+aname+")="+text_result+
                ", ellapsed %1.2e"%(self._eval_times[aname])+" seconds.\n")

            if 'debug' in str(self.getLogLevel()) and \
                (time.time()>(self._cycle_start+self.PollingCycle*1e-3) \
                    if hasattr(self,'PollingCycle') \
                        else aname==sorted(self.dyn_values.keys())[-1]):
                self.attribute_polling_report()
                
        except Exception, e:           
            now=time.time()
            self.dyn_values[aname].update(e,now,AttrQuality.ATTR_INVALID) #Exceptions always kept!
            self._last_period[aname]=now-self._last_read.get(aname,0)
            self._last_read[aname]=now
            self._read_times[aname]=now-self._hook_epoch #Internal debugging
            self._eval_times[aname]=now-tstart #Internal debugging
            if aname==self.dyn_values.keys()[-1]: self._cycle_start = now
            last_exc = str(e)
            self.error('DynamicDS_read_%s_Exception: %s\n\tresult=%s' 
                       % (aname,last_exc,result))
            if not isinstance(e,RethrownException): 
                print(traceback.format_exc())
            raise Exception('DynamicDS_read_%s_Exception: %s' % (aname,last_exc))
    
    ##This hook has been used to force self to be passed always as argument and avoid dynattr missmatching
    if USE_STATIC_METHODS: read_dyn_attr=staticmethod(read_dyn_attr)

    #@Catched
    @self_locked
    def write_dyn_attr(self,attr,fire_event=True):
        aname = attr.get_name()
        self.info("DynamicDS("+self.get_name()+")::write_dyn_atr("+aname+"), entering at "+time.ctime()+"...")
        
        #THIS CHANGE MUST BE TESTED AGAINST PYTANGO7!!!! For Scalar/Spectrum/Image R/W Attrs!!
        try: #PyTango8
            data = attr.get_write_value()
        except:
            data = []
            attr.get_write_value(data)
            
        if fun.isSequence(data) and self.dyn_types[aname].dimx==1: 
            data = data[0]
        elif self.dyn_types[aname].dimy!=1:
            x = attr.get_max_dim_x()
            data = [data[i:i+x] for i in range(len(data))[::x]]
        self.setAttr(aname,data)
        #self.dyn_values[aname].update(result,time.time(),PyTango.AttrQuality.ATTR_VALID)
        ##if fire_event: self.fireAttrEvent(aname,data)
    
    ##This hook has been used to force self to be passed always as argument and avoid dynattr missmatching
    if USE_STATIC_METHODS: write_dyn_attr=staticmethod(write_dyn_attr)
    
    def push_dyn_attr(self,aname,value=None,date=None,quality=None,
            events=None,changed=None,queued=False):
        try:
            aname = self.get_attr_name(aname)
            queued = queued and self.MaxEventStream
            
            if fun.clmatch('state$',aname):
                aname = 'State'
                events,changed = True,True
                value = value if value is not None else self.get_state()
                date,quality = time.time(),AttrQuality.ATTR_VALID

            t = self.dyn_values.get(aname,DynamicAttribute())
            value = notNone(value,t.value)
            date = notNone(date,fun.now())
            quality = notNone(quality,t.quality)
                
            if events is None:
                # That call parses the contents of UseEvents property
                events = self.check_attribute_events(aname)
            if changed is None:
                changed = self.check_changed_event(aname,value,events)
            if not events or not changed:
                return 'nothing to do'
                
            self.info('push_dyn_attr(%s,%s)=%s(%s))\n%s'%(aname,
                queued and 'queued' or 'pushed',type(value),
                shortstr(value),'<'*80))
            
            if queued:
                try:
                    self._events_lock.acquire()
                    self._events_queue.put((aname,value,date,quality,events))
                finally:
                    self._events_lock.release()
                return 'queued'
            else:
                if aname.lower() in ('state','status'):
                    self.push_change_event(aname)
                else:
                    self.push_change_event(aname,value,date,quality)
                if fun.clsearch('archive',events):
                    if aname.lower() in ('state','status'):
                        self.push_archive_event(aname)
                    else:
                        self.push_archive_event(aname,value,date,quality)

                return 'pushed'
            
        except Exception as e:
            self.error('push_dyn_attr(%s,%s(%s),%s,%s) failed!\n%s' % 
                (aname,type(value),value,date,quality,traceback.format_exc()))

    #--------------------------------------------------------------------------
    #   Attributes and State Evaluation Methods
    #--------------------------------------------------------------------------

    ## DYNAMIC ATTRIBUTE EVALUATION ... 
    # Copy it to your device and add any method you will need
    def evalAttr(self,aname,WRITE=False,VALUE=None,_locals=None, push=False):
        ''' 
        SPECIFIC METHODS DEFINITION DONE IN self._locals!!! 
        @remark Generators don't work  inside eval!, use lists instead
        If push=True, any result is considered as change
        '''
        aname,formula = self.get_attr_name(aname),''
        self.debug("DynamicDS(%s)::evalAttr(%s,%s): ... last value was %s"
            % (self.get_name(), aname, push, shortstr(
                getattr(self.dyn_values.get(aname,None),'value',None))))
        tstart = time.time()
        
        try:
            aname,formula,compiled = self.get_attr_formula(aname,full=True)
        
            ##Checking attribute dependencies
            # dependencies assigned at dyn_attr by self.check_dependencies()
            deps = False
            
            if (self.CheckDependencies and aname in self.dyn_values and
                self.dyn_values[aname].dependencies):
                    deps = self.update_dependencies(aname)
            else:
                self.debug("In evalAttr ... updating locals from dyn_values")
                for k,v in self.dyn_values.items():
                    if v.keep and k in formula:
                        self._locals[k]=v.value            
            
            cache = self.get_attr_cache(aname) if (
                not WRITE and not push and not deps) else None
            if cache is not None:
                self.debug('Returning cached (%s) value for %s: %s(%s)'
                    %(fun.time2str(cache.date),aname,type(cache.value),
                      shortstr(cache.value)))                
                return cache.value
            
            if formula in self.Lambdas:
                f = self.Lambdas[formula]
                self.info("In evalAttr(push=%s) ... using Lambdas[%s] = %s" 
                          % (push,formula,f))
                if fun.isString(f):
                    f = self._locals.get(f,self.__getattr__(f,None))
                result = (f() if fun.isCallable(f) else f)
                
            else:
                self.debug("In evalAttr ... updating locals defaults")
                try:
                    self._locals.update({
                        't':time.time()-self.time0,
                        'WRITE':WRITE,
                        'READ':bool(not WRITE),
                        'ATTRIBUTE':aname,
                        'NAME':self.get_name(),
                        'VALUE':(VALUE if VALUE is None or aname not in self.dyn_types 
                            else self.dyn_types[aname].pytype(VALUE)),
                        'STATE':self.get_state(),
                        'LOCALS':self._locals,
                        'ATTRIBUTES':sorted(self.dyn_values.keys()),
                        'FORMULAS':dict((k,v.formula) for k,v in self.dyn_values.items()),                  
                        'XATTRS':self._external_attributes,
                        }) #It is important to keep this values persistent; becoming available for quality/date/state/status management
                    
                    # Redundant but needed
                    [self._locals.__setitem__(str(quality),quality) for quality in AttrQuality.values.values()]
                    [self._locals.__setitem__(k,dst.pytype) for k,dst in DynamicDSTypes.items()]
                    #Adding states for convenience evaluation
                    #self.TangoStates = dict((str(v),v) for k,v in PyTango.DevState.values.items())
                    #self._locals.update(self.TangoStates)                  

                    if _locals is not None: 
                        #High Priority: variables passed as argument
                        self._locals.update(_locals) 

                except Exception,e:
                    self.error('<'*80)
                    self.error(traceback.format_exc())
                    for t in (
                        VALUE,type(VALUE),aname,self.dyn_types.get(aname,None),aname 
                        in self.dyn_types and self.dyn_types[aname].pytype):
                        self.warning(str(t))
                    self.error('<'*80)
                    raise e
            
                if WRITE: 
                    self.debug('%s::evalAttr(WRITE): Attribute=%s; formula=%s; VALUE=%s'%(self.get_name(),aname,formula,shortstr(VALUE)))
                elif aname in self.dyn_values: 
                    self.debug('%s::evalAttr(READ): Attribute=%s; formula=%s;'%(self.get_name(),aname,formula,))
                else: 
                    self.info('%s::evalAttr(COMMAND): formula=%s;'%(self.get_name(),formula,))

                ###################################################################
                result = eval(compiled or formula,self._globals,self._locals)
            ###################################################################
            
            self.debug('eval result: '+str(result))
            if aname not in self.dyn_values:
                return result
            elif WRITE:
                if self.ReadOnWrite:
                    self.evalAttr(aname,WRITE=False,_locals=_locals,push=push)
                return result            

            ###################################################################
            #Push/Keep Read Attributes

            quality = self.get_attr_quality(aname,result)
            if hasattr(result,'quality'): 
                result.quality = quality
            date = self.get_attr_date(aname,result)
            value = self.dyn_types[aname].pytype(result)

            #UseEvents must be checked before updating the cache
            events = self.check_attribute_events(aname)
            check = events and (
                        push or self.check_changed_event(aname,result,events))
            
            et = 1e3*(fn.now()-tstart)
            cached = events or self.dyn_values[aname].keep
            (self.debug if et < 1. else self.warning)(
                'evalAttr(%s): events = %s, check = %s, cached = %s, '
                'eval_ms = %d' % (aname,events,check,cached,et))
            if events and check:
                self.push_dyn_attr(aname,value=value,
                                   events=events,changed=1,queued=1)
            
            #Updating the cache
            if cached: 
                old = self.dyn_values[aname].value
                self.dyn_values[aname].update(value,date,quality)
                self._locals[aname] = value
                self.debug('evalAttr(%s):Value kept for reuse' % (aname,))
                #Updating state if needed:
                try:
                    if old!=value and self.dyn_values.get(aname).states_queue:
                        self.check_state()
                except:
                    self.warning('Unable to check state!')
                    self.warning(traceback.format_exc())            

            return result

        except PyTango.DevFailed, e:
            if self.trace:
                print('-'*80)
                print('\n'.join(['DynamicDS_evalAttr(%s)_WrongFormulaException:'%aname,'\t"%s"'%(formula,),str(traceback.format_exc())]))
                print('\n'.join([str(e.args[0])]) + '\n'+'*'*80)
                print('-'*80)
            err = e.args[0]
            self.error(e)
            raise e #Exception,';'.join([err.origin,err.reason,err.desc])
        
        except Exception,e:
            if self.last_attr_exception and self.last_attr_exception[0]>tstart:
                e = self.last_attr_exception[-1]
            if 1:
                print('\n'.join(['DynamicDS_evalAttr_WrongFormulaException','%s is not a valid expression!'%(formula,),]))
            s = traceback.format_exc()
            #self.error(s)
            print(s)
            raise e #Exception(s)
        
        finally:
            self._eval_times[aname] = fun.now()-tstart
            self._locals['ATTRIBUTE'] = ''
            
    def evalCommand(self,cmd,argin=None):
        """This method will execute a command declared using DynamicCommands property"""
        k = cmd if '/' in cmd else self.get_name()+'/'+cmd
        assert k in self.dyn_comms.keys(),('%s command not declared in properties!'%(k,))
        return self.evalAttr(self.dyn_comms[k],_locals={'ARGS':argin})            

    # DYNAMIC STATE EVALUATION
    def evalState(self,formula,_locals={}):
        """
        Overloading the eval method to be used to evaluate State expressions
        ... To customize it: copy it to your device and add any method you will need
        @remark Generators don't work  inside eval!, use lists instead
        
        The main difference with evalAttr is that evalState will not Check Dependencies nor push events
        """
        self.debug('DynamicDS.evalState/evaluateFormula(%s)'%(isinstance(formula,str) and formula or 'code'))
        #MODIFIIED!! to use pure DynamicAttributes
        #Attr = lambda a: self.dyn_values[a].value
        if formula in self.Lambdas:
            self.info('DynamicDS.evalState: using Lambdas')
            f = self.Lambdas[formula]
            return f() if fun.isCallable(f) else f
            
        t = time.time()-self.time0            
        for k,v in self.dyn_values.items(): self._locals[k]=v#.value #Updating Last Attribute Values
        __locals = {}#__locals=locals().copy() #Low priority: local variables
        __locals.update(self._locals) #Second priority: object statements
        __locals.update(_locals) #High Priority: variables passed as argument
        __locals.update(
            {'STATE':self.get_state(),'t':time.time()-self.time0,'NAME': self.get_name(),
            'ATTRIBUTES':sorted(self.dyn_values.keys()),#'ATTRIBUTES':dict((a,getattr(self.dyn_values[a],'value',None)) for a in self.dyn_values if a in self._locals),
            'FORMULAS':dict((k,v.formula) for k,v in self.dyn_values.items()),
            'WRITE':False,
            'VALUE':None,
            })
        return eval(formula,self._globals,__locals)
    
    def rawState(self):
        self.debug('In DynamicDS.rawState(), overriding attribute-based State.')
        state = self.get_state()
        self.debug('In DynamicDS.State()='+str(state))
        return state        
    
    def check_state(self,set_state=True,current=None):
        '''    The thread automatically close if there's no activity for 5 minutes,
            an always_executed_hook call or a new event will restart the thread.
        '''
        new_state = self.get_state()
        try:
            if self.state_lock.locked(): 
                self.debug('In DynamicDS.check_state(): lock already acquired')
                return new_state
            
            self.state_lock.acquire()
            if self.dyn_states:
                self.info('In DynamicDS.check_state()')
                old_state = new_state if current is None else current
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
                    self.info('In DynamicDS.check_state(): %s : %s ==> %s' % (state,value['formula'],result))
                    
                    if result:
                        new_state = self.TangoStates[nstate]
                        if new_state!= old_state:
                            self.info('DynamicDS(%s.check_state(): New State is %s := %s'%(self.get_name(),nstate,formula))
                            if set_state:
                                self.set_state(new_state,push=True)
                        break
        except Exception,e:
            print(traceback.format_exc())
            raise e
        finally:
            if self.state_lock.locked(): self.state_lock.release()
        return new_state    
    
    def check_status(self,set=True):
        status = self.get_status()
        if self.DynamicStatus:
            self.debug('In DynamicDS.check_status')
            try:
                status = ''
                for s in self.DynamicStatus:
                    try:
                        t = s and self.evaluateFormula(s) or ''
                        status += t+'\n'
                    except Exception,x:
                        self.warning('\tevaluateStatus(%s) failed: %s'%(s,traceback.format_exc()))
                if set: self.set_status(status,save=False)
            except Exception,e:
                self.warning('Unable to generate DynamicStatus:\n%s'%traceback.format_exc())
        return status.strip()    

    def processEvents(self):
        """
        Polled command to process the internal event queue
        MaxEventStream must be configured
        """
        try:
            c = 0
            self._events_lock.acquire()            
            t0 = fun.now()            
            if (not self.MaxEventStream or 
                    not self.check_attribute_events('state')):
                self.debug('Events not queued ...')
                return 0
            self.info('*'*80)
            self.info('In processEvents(%d/%d)'
                % (self.MaxEventStream,self._events_queue.qsize()))
            self.info('*'*80)
            if self._events_queue.empty():
                return 0
            for i in range(self.MaxEventStream):
                try:
                    a,v,d,q,e = self._events_queue.get(False)
                    self.push_dyn_attr(a,v,d,q,e,changed=True,queued=False)
                    c+=1
                except objects.Queue.Empty:
                    break
                except Exception as e:
                    self.warning('push(%s) failed!' % str((a,v,d,q,e)))
                    traceback.print_exc()
        except:
            self.warning(traceback.format_exc())
        finally:
            self._events_lock.release()
            self.debug('events lock released')
        return c
            
######################################################################################################
# INTERNAL DYNAMIC DEVICE SERVER METHODS
######################################################################################################
            
    
class DynamicDSHelpers(DynamicDSAttrs):
    ''' Check fandango.dynamic.__doc__ for more information ...'''
    
    def get_dyn_attr_list(self):
        """Gets all dynamic attribute names."""
        return sorted(self.dyn_attrs.keys())
    
    @Cached(depth=200,expire=15.)
    def get_polled_attrs(self,load=False):
        #@TODO: Tango8 has its own get_polled_attr method; check for incompatibilities
        if load or not getattr(self,'_polled_attr_',None):
            self._polled_attr_ = tango.get_polled_attrs(self)
        return self._polled_attr_   
    
    def get_attr_name(self,aname):
        if aname not in self.dyn_values:
            for k in self.dyn_values:
                if k.lower() == str(aname).strip().lower().split('/')[-1]:
                    return k
        return aname
    
    def get_attr_date(self,aname,value):
        aname = self.get_attr_name(aname)
        if type(value) is DynamicAttribute:
            return value.date
        return time.time()    
      
    def get_attr_formula(self,aname,full=False):
        """
        Returns the formula for the given attribute
        The as_tuple flag will return an attr,formula,compiled tuple
        """
        aname = self.get_attr_name(aname)
        if aname in self.dyn_values:
            formula = self.dyn_values[aname].formula
            compiled = self.dyn_values[aname].compiled
            
        else:
            #Getting a caseless attribute that match
            try:
                aname,formula,compiled = ((k,self.dyn_values[k].formula,
                                           self.dyn_values[k].compiled) for 
                                          k in self.dyn_values if 
                                          k.lower()==aname.lower()).next()
            except: 
                self.warning('DynamicDS.evalAttr: %s doesnt match any Attribute name,'
                             ' trying to evaluate ...'%(aname,))
                formula,compiled=aname,None
        if full:
            return aname,formula,compiled
        else:
            #If no attribute is matching, attribute name is returned
            return formula
      
    def get_attr_models(self,attribute):
        """
        Given a dynamic attribute name or formula, it will return a 
        list of tango models appearing on it
        """
        formula = self.get_attr_formula(attribute)
        matches = re.findall(tango.retango,formula)
        #Matches are models split in parts, need to be joined
        return ['/'.join(filter(bool,s)) for s in matches]   
    
    def get_attr_quality(self,aname,attr_value):
        aname = self.get_attr_name(aname)
        formula = self.dyn_qualities.get(aname.lower()) or 'Not specified'
        self.debug('In get_attr_quality(%s,%s): %s' 
            % (aname,shortstr(attr_value,15)[:10],formula))
        try:
            if aname.lower() in self.dyn_qualities:
                self._locals['ATTRIBUTE'] = aname.lower()
                self._locals['FORMULAS'] = dict((k,v.formula) for k,v in self.dyn_values.items())
                self._locals['VALUE'] = getattr(attr_value,'value',attr_value)
                self._locals['DEFAULT'] = getattr(attr_value,'quality',AttrQuality.ATTR_VALID)
                quality = eval(formula,{},self._locals) or AttrQuality.ATTR_VALID
            else:
                quality =  getattr(attr_value,'quality',AttrQuality.ATTR_VALID)
            self.debug('\t%s.quality = %s'%(aname,quality))
            return quality
        except Exception,e:
            self.error('Unable to generate quality for attribute %s: %s\n%s'%(aname,formula,traceback.format_exc()))
            return AttrQuality.ATTR_VALID
        
    def get_attr_cache(self, aname):
        if aname not in self.dyn_values:
            self.warning('get_attr_cache(%s): Unknown?' % aname)
        keep = aname in self.dyn_values and self.dyn_values[aname].keep
        try:
            updated = self.dyn_values[aname].updated
            #self.info('%s,keep=%s,keeptime=%s,updated=%s' 
                    #% (aname,keep,self.KeepTime,updated))            
            if (keep and self.KeepTime and updated
                    and time.time()<(updated+(self.KeepTime/1e3))):
                v = self.dyn_values[aname]
                return v
        except Exception,e:
            self.warning('Unable to reload %s kept values, %s'%(aname,str(e))) 
            
        return None
    
    #------------------------------------------------------------------------------------------------------
    #   Methods usable inside Attributes declaration
    #------------------------------------------------------------------------------------------------------

    def getAttr(self,aname,default=None,write=False,wvalue=None):
        """Evaluates an attribute and returns its Read value."""
        try:
          al = aname.lower()
          if '/' in aname:
              value = self.getXAttr(aname,default,write,wvalue)
          elif al=='state': 
              value = self.get_state()
          elif al=='status': 
              value = self.get_status()
          elif al in map(str.lower,self.dyn_values.keys()):
              value = self.evalAttr(aname,WRITE=write,VALUE=fun.notNone(wvalue,default))
          else:
              #Getting an Static attribute that match:
              method = getattr(self,'read_%s'%aname,getattr(self,'read_%s'%al,None))
              if method is not None:
                  self.warning('DynamicDS.getAttr: %s is an static attribute ...'%(aname,))
                  attr = tango.fakeAttributeValue(aname)
                  method(attr)
                  value = attr.value
              else:
                  self.warning('DynamicDS.getAttr: %s doesnt match any Attribute name, trying to evaluate ...'%(aname,))
                  value = default
          return value
        except Exception,e:
          if default is not None:
            return default
          else:
            traceback.print_exc()
            raise e

    def setAttr(self,aname,VALUE):
        """Evaluates the WRITE part of an Attribute, passing a VALUE."""
        self.evalAttr(aname,WRITE=True,VALUE=VALUE)
        
    def ForceAttr(self,argin,VALUE=None):
        ''' Description: The arguments are AttributeName and an optional Value.<br>
            This command will force the value of the Attribute or will return the last forced value
            (if only one argument is passed). '''
        if type(argin) is not list: argin = [argin]
        if len(argin)<1: raise Exception('At least 1 argument required (AttributeName)')
        if len(argin)<2: value=VALUE
        else: value=argin[1]
        aname = argin[0]
        aname = self.get_attr_name(aname)
        if aname not in self.dyn_values.keys(): 
            raise Exception('Unknown State or Attribute : ', aname)
        elif value is not None:
            self.dyn_values[aname].forced=value
            if self.simulationMode:
                self.dyn_values[aname].value=value
        else: value = self.dyn_values[aname].forced
        return value
        
    def ForceVar(self,argin,VALUE=None,default=None,WRITE=None):
        ''' 
        Management of "Forced Variables" in dynamic servers
        
        Description: The arguments are VariableName and an optional Value.<br>
        This command will force the value of a Variable or will return the last forced value
        (if only one argument is passed). 
        
        There are several syntaxes that can be used to call variables.
        - VAR("MyVariable",default=0) : return Value if initialized, else 0
        - VAR("MyVariable",VALUE) : Writes Value into variable
        - VAR("MyVariable",WRITE=True) : Writes VALUE as passed from a write_attribute() call; reads otherwise
        - This syntax replaces (VAR("MyVar",default=0) if not WRITE else VAR("MyVar",VALUE))
        - GET("MyVariable") : helper to read variable
        - SET("MyVariable",VALUE) : helper to write variable
        
        :param default: value to initialize variable at first read
        :param WRITE: if True, VALUE env variable will overwrite VALUE argument
        '''
        
        if type(argin) is not list: argin = [argin]
        if len(argin)<1: raise Exception('At least 1 argument required (AttributeName)')
        if len(argin)<2: value=VALUE
        else: value=argin[1]
        aname = argin[0]
        is_write = self._locals.get('WRITE') 
        
        self.debug('VAR(%s,%s,%s,%s & %s)'%(aname,value,default,WRITE,is_write))

        if WRITE and is_write:
            value = fun.notNone(self._locals.get('VALUE'),value)
            self.debug('Writing %s into %s'%(value,aname))
            
        if value is not None: 
            self.variables[aname] = value
            
        elif self.variables.get(aname) is None: 
            self.variables[aname] = default
            
        value = self.variables[aname]
        return value            
        
    def getXDevice(self,dname):
        """
        This method returns a DeviceProxy to the given attribute.
        """
        if self.UseTaurus:
            return tango.TAU.Device(dname)
        else:
            return PyTango.DeviceProxy(dname)

    def getXAttr(self,aname,default=None,write=False,wvalue=None):
        """
        Performs an external Attribute reading, using a DeviceProxy to read own attributes.
        Argument could be: [attr_name] or [device_name](=State) or [device_name/attr_name]
        
        :returns: Attribute value or None
        """
        params = tango.parse_tango_model(aname,use_host=False) #Device will contain TANGO_HOST only if differs from current
        if params: 
            device,aname = params.get('devicemodel',None),params.get('attribute',aname)
        else: 
            device,aname = aname.rsplit('/',1) if '/' in aname else '',aname
        
        (self.info if write else self.debug)("DynamicDS.getXAttr(%s,%s,write=%s): ..."
            %(device or self.get_name(),aname,write and '%s(%s)'%(type(wvalue),wvalue)))
        
        # Returning an empty list because it is a False iterable value that can be converted 
        # to boolean (and False or None cannot be converted to iterable)
        result = default 
        try:
            if not device:
                self.info('getXAttr accessing to device itself ... using getAttr instead')
                if write: 
                    self.setAttr(aname,wvalue)
                    result = wvalue
                else: result = self.getAttr(aname)
            else:
                devs_in_server = self.myClass and self.myClass.get_devs_in_server() or []
                if device in devs_in_server:
                    #READING FROM AN INTERNAL DEVICE
                    self.debug('getXAttr accessing a device in the same server ... using getAttr')
                    if aname.lower()=='state': result = devs_in_server[device].get_state()
                    elif aname.lower()=='status': result = devs_in_server[device].get_status() 
                    elif write: 
                        devs_in_server[device].setAttr(aname,wvalue) 
                        result = wvalue
                    else: result = devs_in_server[device].getAttr(aname)
                else:
                    #READING FROM AN EXTERNAL DEVICE
                    full_name = (device or self.get_name())+'/'+aname
                    if full_name not in self._external_attributes:
                        self.debug('%s.getXAttr: creating %s proxy to %s' % (self._locals.get('ATTRIBUTE'),'taurus' if self.UseTaurus else 'PyTango',full_name))
                        if self.UseTaurus: 
                            #USING TAURUS+EVENTS = CACHED VALUES
                            a = tango.TAU.Attribute(full_name)
                            #full_name = tango.get_model_name(a) #If the host is external it must be specified in the formula
                            self._external_attributes[full_name] = a
                            a.changePollingPeriod(self.DEFAULT_POLLING_PERIOD)
                            if len(self._external_attributes) == 1: 
                                tango.TAU_LOGGER.disableLogOutput()

                            # Check UseEvents
                            if (self._locals.get('ATTRIBUTE') 
                                    and self.check_attribute_events(self._locals.get('ATTRIBUTE'))):
                                #If Attribute has events evalAttr() will be called at every event_received
                                #If there's no events, then will be not necessary
                                self.info('\t%s.addListener(%s)'%(full_name,self._locals['ATTRIBUTE']))
                                if tango.get_model_name(a) not in self._external_listeners: 
                                    self._external_listeners[tango.get_model_name(a)]=set()
                                    
                                self._external_listeners[tango.get_model_name(a)].add(self._locals['ATTRIBUTE'])

                            self._external_attributes[full_name].addListener(self.event_received)
                        else: 
                            #USING PLAIN PYTANGO (POLLING UNCACHED VALUES)
                            cap = tango.CachedAttributeProxy(full_name,
                                    keeptime=max((100,self.KeepTime)))#keeptime=self.KeepTime)
                            self._external_attributes[full_name] = cap
                    else:
                        self.debug('%s.getXAttr: using %s proxy to %s' % (self._locals.get('ATTRIBUTE'),'taurus' if self.UseTaurus else 'PyTango',full_name))
                    if write: 
                        self.info('getXAttr(Write): %s(%s)'%(type(wvalue),wvalue))
                        self._external_attributes[full_name].write(wvalue)
                        result = wvalue
                    else:
                        attrval = self._external_attributes[full_name].read()
                        result = attrval.value
                        
                    self.debug('%s.read() = %s ...'%(full_name,str(result)[:40])) 
        except Exception,e:
            msg = 'Unable to read attribute %s from device %s: \n%s' % (str(aname),str(device),traceback.format_exc())
            print(msg)
            self.error(msg)
            self.last_attr_exception = (time.time(),msg,e)
            #Exceptions are not re_thrown to allow other commands to be evaluated if this fails.
        finally:
            if hasattr(self,'myClass') and self.myClass:
                self.myClass.DynDev=self #NOT REDUNDANT: If a call to another device in the same server occurs this pointer could have been modified.
                
        #Check added to prevent exceptions due to empty arrays
        if hasattr(result,'__len__') and not len(result):
            result = default if hasattr(default,'__len__') else []
        elif result is None:
            result = default
        self.debug('Out of getXAttr(%s)'%shortstr(result,40))
        return result
    
    def event_received(self,source,type_,attr_value):
        """
        This method is needed to re-trigger events in attributes that
        receive events from other devices (e.g. use XATTR in formula)
        """

        etype = tango.fakeEventType.get(type_,type_)
        def _log(prio,s,obj=self): #,level=self.log_obj.level): 
            if obj.getLogLevel(prio)>=obj.log_obj.level:
                print('%s(%s) %s %s: %s' % (
                  prio.upper(),
                  (obj.getLogLevel(prio),obj.log_obj.level),
                  time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),
                  obj.get_name(),s))

        if clmatch('config|attr_conf',etype):
            _log('debug','In DynamicDS.event_received(%s(%s),%s,%s): Config Event Not Implemented!'%(
                type(source).__name__,source,etype,type(attr_value).__name__,#getattr(attr_value,'value',attr_value)
                ))
        else:
            _log('info','In DynamicDS.event_received(%s(%s),%s,%s)'%(
                type(source).__name__,source,etype,type(attr_value).__name__)
                )
            try:
                if type_ in ('Error','error',tango.fakeEventType['Error']):
                    _log('error','Error received from %s: %s'%(source, attr_value))
                full_name = tango.get_model_name(source) #.get_full_name()
                if full_name not in self._external_listeners:
                    self.debug('%s does not trigger any dynamic attribute event'%full_name)
                elif self._external_listeners[full_name]:
                    _log('info','\t%s.listeners: %s'%(full_name,self._external_listeners[full_name]))
                    for aname in self._external_listeners[full_name]:
                        if self._locals['ATTRIBUTE'] == aname:
                            #Variable already being evaluated
                            continue 
                        else:
                            _log('info','\tforwarding event to %s ...'%aname)
                            self.evalAttr(aname)
            except:
                print(traceback.format_exc())
        return    

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
                        self.debug('getXCommand calling a proxy to %s' % (device,))
                        if full_name not in self._external_commands:
                            if self.UseTaurus: 
                                self._external_commands[full_name] =  tango.TAU.Device(device)
                                if len(self._external_commands)==1: tango.TAU_LOGGER.disableLogOutput()
                            else: self._external_commands[full_name] = PyTango.DeviceProxy(device)
                        self.debug('getXCommand(%s(%s))'%(full_name,args))
                        if args in (None,[],()):
                            result = self._external_commands[full_name].command_inout(cmd)
                        else:
                            result = self._external_commands[full_name].command_inout(cmd,args)
                        #result = self._external_commands[full_name].command_inout(*([cmd,argin] if argin is not None else [cmd]))
            except Exception,e:
                msg = 'Unable to execute %s(%s): %s' % (full_name,args,traceback.format_exc())
                self.last_attr_exception = (time.time(),msg,e)
                self.error(msg)
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
            return tango.TangoCommand(command=cmd,device=device,feedback=feedback,timeout=10.,wait=10.).execute(args,expected=expected)
    
    @staticmethod
    def open_file(filename,device=None):
        print('DynamicDS().open_file(%s)'%(filename))
        r = []
        try:
            if device:
                if not hasattr(device,'PATH'): device.PATH = device.get_device_property('PATH') or ''
                if device.PATH: filename = device.PATH+'/'+filename
            f = open(filename)
            r = f.readlines()
            f.close()
        except: print(traceback.format_exc())
        return r

    @staticmethod
    def load_from_file(filename=None,device=None):
        """ This line is put in a separate method to allow subclasses to override this behavior"""
        filename = filename or device.LoadFromFile
        data = DynamicDS.open_file(filename,device=device) if filename.lower().strip() not in ('no','false','') else []
        if data and device: device.DynamicAttributes = list(data)+list(device.DynamicAttributes)
        return data
    
    

###############################################################################        
###############################################################################
            
class DynamicDS(DynamicDSHelpers):
    ''' 
    This Class keeps all DynamicDS methods exported to Tango API
    
    Check fandango.dynamic.__doc__ for more information ...
    '''
        
        
    def init_device(self):
        self.info( 'DynamicDS.init_device(%d)'%(self.get_init_count()))
        try:
            if not type(self) is DynamicDS and not self.get_init_count():
                self.get_DynDS_properties()
            else:
                self.updateDynamicAttributes()
            for c,f in self.dyn_comms.items(): 
                k = c.split('/')[-1]
                if self.get_name().lower() in c.lower() \
                    and k not in self._locals:
                   self._locals.update({k:
                        (lambda argin,cmd=k:self.evalCommand(cmd,argin))})
            for i in self.InitDevice:
                if str(i).strip().lower() in ('','false'):
                    continue
                elif i not in self.dyn_comms:
                    self.warning('Unknown %s cmd at init, ignored' % str(i))
                else:
                    try:
                        self.evalAttr(i)
                    except Exception,e:
                        self.error('Unable to execute InitDevice(%s)' % str(i))
                        traceback.print_exc()
                        raise e
        except: 
            print(traceback.format_exc()) #self.warning(traceback.format_exc())

        self.reset_memleak()
        self._init_count +=1

    def delete_device(self):
        self.warning( 'DynamicDS.delete_device(): ... ')
        PyTango.LatestDeviceImpl.delete_device(self)
        
    @self_locked
    def always_executed_hook(self):
        self.debug("In DynamicDS::always_executed_hook(TAU=%s)"%tango.TAU)
        try:
            self._hook_epoch = time.time() #Internal debugging
            if not self._prepared: self.prepare_DynDS() #This code is placed here because its proper execution cannot be guaranteed during init_device()
            self.myClass.DynDev=self #VITAL: It tells the admin class which device attributes are going to be read
            if self.dyn_states: self.check_state()
            if self.DynamicStatus: self.check_status()
        except:
            self.last_state_exception = 'Exception in DynamicDS::always_executed_hook():\n'+str(traceback.format_exc())
            self.error(self.last_state_exception)
        return
    
#------------------------------------------------------------------------------------------------------
#   State related methods
#------------------------------------------------------------------------------------------------------

    def set_state(self,state,push=False):
        now = time.time()
        old,self._locals['STATE'] = self._locals.get('STATE',None),state
        last = now - self.last_state_change
        diff = (state,(last > self.DEFAULT_POLLING_PERIOD/1e3 and last))
        try:
            if diff != (old,False):
                self.last_state_change = now
                self.push_dyn_attr('State',state,changed=push,queued=True)
        except Exception,e: 
            self.warning('DynamicDS.set_state(%s) failed!: %s'%(state,e))
            
        DynamicDS.get_parent_class(self).set_state(self,state)
    
    def set_status(self,status,save=True):
        if save: #not any('STATUS' in s for s in self.DynamicStatus): #adds STATUS to locals only if not used in DynamicStatus?
            self._locals['STATUS']=status
        self.debug('STATUS: %s'%(status,))
        DynamicDS.get_parent_class(self).set_status(self,status)
        
    def set_full_status(self,status,set=True):
        if self.last_state_exception:
            status += '\nLast DynamicStateException was:\n\t'+self.last_state_exception
        if self.last_attr_exception:
            status += '\nLast DynamicAttributeException was:\n\t%s:%s'%(time.ctime(self.last_attr_exception[0]),str(self.last_attr_exception[1]))
        if set: self.set_status(status)
        return status
    
    ##########################################################################    
            
    def read_attr_hardware(self,data):
        self.debug("In DynDS::read_attr_hardware()")
        attrs = self.get_device_attr()
        read_attrs = [attrs.get_attr_by_ind(d).get_name() for d in data]
        for a in read_attrs: self._read_count[a]+=1
        return read_attrs
        #self.info("read_attr_hardware([%d]=%s)"%(len(data),str(read_attrs)[:80]))        
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
            
    ###########################################################################
    # EXTERNAL COMMANDS
    ###########################################################################

    def Help(self,str_format='text'):
        """This command returns help for this device class and its parents"""
        return tango.get_device_help(self,str_format)            
        
    def setPauseEvents(self,argin):
        ov = self._events_paused
        self._events_paused = bool(fun.clmatch('yes|true',argin))
        if not self._events_paused and ov:
            for a,v in self.dyn_values.items():
                events = self.check_attribute_events(a)
                self.push_dyn_attr(aname,events=events,changed=1,queued=1)
                
        return str(self.check_attribute_events('state'))
    
    #------------------------------------------------------------------
    #    GetDynamicConfig command:
    #
    #    Description: Return current property values
    #
    #    argin:  DevVoid
    #    argout: DevString      Return current property values
    #------------------------------------------------------------------
    #Methods started with underscore could be inherited by child device servers for debugging purposes
    def getDynamicConfig(self):
        exclude = 'DynamicAttributes','DynamicCommands','DynamicStates','DynamicStatus'
        return '\n'.join(sorted('%s: %s'%(k,getattr(self,k,None)) 
            for l in (DynamicDSClass.class_property_list,DynamicDSClass.device_property_list)
            for k in l if k not in exclude))
    
    #------------------------------------------------------------------
    #    getDynamicAttributes command:
    #
    #    Description: Return current dynamic attributes
    #
    #    argin:  DevVoid
    #    argout: DevVarStringArray      Return current dynamic attributes
    #------------------------------------------------------------------
    #Methods started with underscore could be inherited by child device servers for debugging purposes
    def getDynamicAttributes(self):
        return self.get_dyn_attr_list()
    
    #------------------------------------------------------------------
    #    GetMemUsage command:
    #
    #    Description: Returns own process RSS memory usage (Kb).
    #
    #    argin:  DevVoid
    #    argout: DevString      Returns own process RSS memory usage (Kb)
    #------------------------------------------------------------------
    #Methods started with underscore could be inherited by child device servers for debugging purposes
    def getMemUsage(self):
        """ returns memory usage in kb """
        m = fn.linos.get_memory()/1e3
        if self.mem0:
            self.memleak = float(m-self.mem0) / (time.time() - self.time0)
        return m
    
    #------------------------------------------------------------------
    #    Read MemUsage attribute
    #------------------------------------------------------------------
    def read_MemUsage(self, attr):
        """ returns memory usage in kb """
        self.debug("In read_MemUsage()")
        
        #    Add your own code here
        m = self.getMemUsage()
        self.push_change_event('MemUsage',m)
        attr.set_value(m)
        
    #------------------------------------------------------------------
    #    Read EventQueueSize attribute
    #------------------------------------------------------------------
    def read_EventQueueSize(self, attr):
        self.debug("In read_EventQueueSize()")
        
        #    Add your own code here
        attr.set_value(self._events_queue.qsize())        
        
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
        t0 = time.time()
        self.info('\tevaluateFormula(%s)'%(argin,))
        e = self.evalState(str(argin))
        argout=str(e)
        self.info('\tevaluateFormula took %s seconds'%(time.time()-t0))
        return argout        
    
    def pushAttribute(self,argin):
        try:
            return self.push_dyn_attr(argin,changed=True,queued=True)
        except:
            return(traceback.format_exc())
    
    #------------------------------------------------------------------
    #    getAttrFormula command:
    #
    #    Description: Return DynamicAttribute formula
    #
    #    argin:  DevString    PyTango Expression to evaluate
    #    argout: DevString
    #------------------------------------------------------------------
    #Methods started with underscore could be inherited by child device servers for debugging purposes
    def getAttrFormula(self,argin):
        return self.get_attr_formula(argin)
    
    #------------------------------------------------------------------------------------------------------
    #   Lock/Unlock Methods
    #------------------------------------------------------------------------------------------------------

    def isLocked(self):
        return self.clientLock

    def Lock(self):
        self.clientLock=True

    def Unlock(self):
        self.clientLock=False            
        
        
    def attribute_polling_report(self):
        self.debug('\n'+'-'*80)
        try:
            now = time.time()
            self._cycle_start = now-self._cycle_start
            if 'POLL' in self.dyn_values: self.debug('dyn_values[POLL] = %s ; locals[POLL] = %s' % (self.dyn_values['POLL'].value,self._locals['POLL']))
            self.info('Last complete reading cycle took: %f seconds' % self._cycle_start)
            self.info('There were %d attribute readings.'%(sum(self._read_count.values() or [0])))
            head = '%24s\t\t%10s\t\ttype\tinterval\tread_count\tread_time\teval_time\tcpu'%('Attribute','value')
            lines = []
            target = list(t[-1] for t in reversed(sorted((v,k) for k,v in self._read_times.items())))[:7]
            target.extend(list(t[-1] for t in reversed(sorted((v,k) for k,v in self._read_count.items())) if t not in target)[:7])
            for key in target:
                value = (self.dyn_values[key].value if key in self.dyn_values else 'NotKept')
                value = str(value)[:16-3]+'...' if len(str(value))>16 else str(value)
                lines.append('\t'.join([
                    '%24s'%key[:24],
                    '\t%10s'%value[:16],
                    '%s'%type(value).__name__ if value is not None else '...',
                    '%d'%int(1e3*self._last_period[key]),
                    '%d'%self._read_count[key],
                    '%1.2e'%self._read_times[key],
                    '%1.2e'%self._eval_times[key],
                    '%1.2f%%'%(100*self._eval_times[key]/(self._total_usage or 1.))]))
            print(head)
            print('-'*max(len(l)+4*l.count('\t') for l in lines))
            print('\n'.join(lines))
            print('')
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
                        self.info('New objects added to garbage are: %s' % ([str(o) for o in NEW_GARBAGE],))
                except:
                    print(traceback.format_exc())
                self.GARBAGE = grb
                
            #if MEM_CHECK:
                #self._locals['heap'] = h = HEAPY.heap()
                #self.info(str(h))
                
            for a in self._read_count: self._read_count[a] = 0
            self._cycle_start = now
            self._total_usage = 0
        except:
            self.error('DynamicDS.attribute_polling_report() failed!\n%s'%traceback.format_exc())
        self.info('-'*80)        


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
            [ MAX_ARRAY_SIZE ] ],    
        }

    #    Device Properties
    device_property_list = {
        'DynamicAttributes':
            [PyTango.DevVarStringArray,
            "Attributes and formulas to create for this device.\n"\
            "This Tango Attributes will be generated dynamically using this syntax:\n"\
            "\tT3=int(SomeCommand(7007)/10.)\n\n"\
            "See the class description to know how to make any method available in attributes declaration.\n"\
            "NOTE:Python generators dont work here, use comprehension lists instead.",
            [ '#Write here your Attribute formulas' ] ],
        'DynamicStates':
            [PyTango.DevVarStringArray,
            "This property will allow to declare new States dinamically based on\n"\
            "dynamic attributes changes. The function Attr will allow to use the\n"\
            "value of attributes in formulas.\n\n\n\nALARM=Attr(T1)>70\nOK=1",
            [ '#Write here your State formulas' ] ],
        'DynamicCommands':
            [PyTango.DevVarStringArray,
            "This property will allow to declare new Commands at startup with formulas like: \n"\
            "\tSendStrings=DevLong(WATTR(NAME+'/Channel',SPECTRUM(str,ARGS)))",
            [ '#Write here your Command formulas' ] ],            
        'DynamicQualities':
            [PyTango.DevVarStringArray,
            "This property will allow to declare formulas for Attribute Qualities.",
            [] ],           
        'DynamicStatus':
            [PyTango.DevVarStringArray,
            "Each line generated by this property code will be added to status",
            [] ],
        'DynamicSpectrumSize':
            [PyTango.DevLong,
            "It will fix the maximum size for all Dynamic Attributes.",
            [ MAX_ARRAY_SIZE ] ],
        'StoredLambdas':
            [PyTango.DevVarStringArray,
            "regexp:method ; this property allows to declare accelerated calls,"
            " whenever a formula matches regexp, method will be called without"
            " executing an eval.",
            [ 'test:0#Write here your accelerators' ] ],
        'LoadFromFile':
            [PyTango.DevString,
            "If not empty, a file where additional attribute formulas can be declared. It will be parsed BEFORE DynamicAttributes",
            ['no'] ],
        'InitDevice':
            [PyTango.DevVarStringArray,
            "False/True/Attributes/Code, formulas to evaluate at init()"
            "(True to load all attributes)",
            ['False'] ],
        'KeepAttributes':
            [PyTango.DevVarStringArray,
            "This property can be used to store the values of only needed attributes; values are 'yes', 'no' or a list of attribute names",
            ['yes'] ],
        'KeepTime':
            [PyTango.DevDouble,
            "The kept value will be returned if a kept value is re-asked within this milliseconds time (Cache).",
            [ 200 ] ],
        'StartupDelay':
            [PyTango.DevDouble,
            "The device server will wait this time in milliseconds before starting.",
            [ 1000 ] ],
        'CheckDependencies':
            [PyTango.DevVarStringArray,
            "This property manages if dependencies between attributes are used to check readability.",
            ['True'] ],
        'ReadOnWrite':
            [PyTango.DevBoolean,
            "When True, this will trigger a read attribute just after writing (e.g. for pushing events on write).",
            [False] ],            
        'UseEvents':
            [PyTango.DevVarStringArray,
            "Value of this property will be yes/true,no/false or a list of "
            "attributes that will trigger push_event (if configured from jive)",
            ['false'] ],
        'MaxEventStream':
            [PyTango.DevLong,
            "Max number of events to be pushed by processEvents()",
            [ 0 ] ],             
        'UseTaurus':
            [PyTango.DevBoolean,
            "This property manages if Taurus or PyTango will be used to read external attributes.",
            [False] ],
        'LogLevel':
            [PyTango.DevString,
            "This property selects the log level (DEBUG/INFO/WARNING/ERROR)",
            ['INFO'] ],
        }

    #    Command definitions
    cmd_list = {
        'updateDynamicAttributes':
            [[PyTango.DevVoid, "Reloads properties and updates attributes"],
            [PyTango.DevVoid, "Reloads properties and updates attributes"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],
        'evaluateFormula':
            [[PyTango.DevString, "formula to evaluate"],
            [PyTango.DevString, "formula to evaluate"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],
        'setPauseEvents':
            [[PyTango.DevString, "Enable/Disable events"],
            [PyTango.DevString, "Enable/Disable events"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],            
        'Help':
            [[PyTango.DevVoid, ""],
            [PyTango.DevString, "python docstring"],],
        'getDynamicConfig':
            [[PyTango.DevVoid, "Print current property values"],
            [PyTango.DevString, "Print current property values"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],     
        'getDynamicAttributes':
            [[PyTango.DevVoid, "Get current dynamic attributes"],
            [PyTango.DevVarStringArray, "Get current dynamic attributes"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],             
        'getAttrFormula':
            [[PyTango.DevString, "Get current attribute formula"],
            [PyTango.DevString, "Get current attribute formula"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],                   
        'getMemUsage':
            [[PyTango.DevVoid, "Returns own process RSS memory usage (Kb)"],
            [PyTango.DevDouble, "Returns own process RSS memory usage (Kb)"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],
        'processEvents':
            [[PyTango.DevVoid, "process the event queue"],
            [PyTango.DevLong, "number of events processed"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
                'Polling period': 3000,
            } ],
        'pushAttribute':
            [[PyTango.DevString, "Get current attribute formula"],
            [PyTango.DevString, "Get current attribute formula"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],                   
        }

    #    Attribute definitions
    attr_list = {
       'MemUsage':
           [[PyTango.DevDouble,
           PyTango.SCALAR,
           PyTango.READ],
            {
                'Display level':PyTango.DispLevel.EXPERT,
                'Polling period': 3000,
            } ],
        'EventQueueSize':
           [[PyTango.DevLong,
           PyTango.SCALAR,
           PyTango.READ]],
        }
        
    @staticmethod
    def __new__(cls,*args,**kwargs):
        """
        Adding own Properties/Commands to subclasses
        """
        print('In DynamicDSClass.__new__(%s): updating properties'%(cls,))
        dicts = ('class_property_list','device_property_list','cmd_list','attr_list')
        for d in dicts:
            dct = getattr(cls,d)
            for p,v in getattr(DynamicDSClass,d).items():
                if p not in dct: 
                    dct[p] = v
        #cls = cls if cls is not DynamicDSClass else PyTango.DeviceClass
        instance = PyTango.DeviceClass.__new__(cls,*args,**kwargs)
        return instance

    def dyn_attr(self,dev_list):
        print('In DynamicDSClass.dyn_attr(%s)'%(dev_list,))
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
    print('#'*80)
    print('In DynamicDS.CreateDynamicCommands(%s)'%(server,))
    db = U.get_database()
    #devices = DynamicDSClass('DynamicDS').get_devs_in_server()    
    classes = list(db.get_device_class_list(server))
    print('class = %s; classes = %s' % (ds.__name__,classes))
    devs = [classes[i] for i in range(len(classes)-1) if classes[i+1]==ds.__name__]    
    print('devs = %s'%(devs,))
    if not hasattr(ds,'dyn_comms'): ds.dyn_comms = CaselessDict()
    
    for dev in devs:
        prop = db.get_device_property(dev,['DynamicCommands'])['DynamicCommands']
        print('In DynamicDS.CreateDynamicCommands(%s.%s): %s'%(server,dev,prop))
        prop = DynamicDS.check_property_extensions('DynamicCommands',prop)
        #lines = [(dev+'/'+l.split('=',1)[0].strip(),l.split('=',1)[1].strip()) 
                 #for l in [d.split('#')[0].strip() for d in prop if d] if l]
        lines = []
        for i,d in enumerate(prop):
            try:
                if d:
                    l = dd = d.split('#')[0].strip()
                    if l:
                        l0 = dev+'/'+l.split('=',1)[0].strip()
                        l1 = l.split('=',1)[1].strip()
                        l = (l0,l1)
                        lines.append(l)
            except:
                print('CreateDynamicCommands(%s): Unable to parse' % d)
                        
        ds.dyn_comms.update(lines)
        for name,formula in lines: #ds.dyn_comms.items():
            name = name.rsplit('/',1)[-1]
            if name.lower() in [s.lower() for s in dir(ds)]:
                print('Dynamic Command %s.%s Already Exists, skipping!!!'%(type(ds),name))
                continue

            name = ([n for n in ds_class.cmd_list.keys() if n.lower()==name.lower()] or [name])[0]
            return_type = PyTango.CmdArgType.names.get(formula.split('(')[0],PyTango.DevString)
            itype = ('SCALAR(int,ARGS)' in formula and PyTango.DevLong or
                     'SCALAR(float,ARGS)' in formula and PyTango.DevDouble or
                     'SCALAR(str,ARGS)' in formula and PyTango.DevString or
                     'SCALAR(bool,ARGS)' in formula and PyTango.DevBoolean or
                     'SPECTRUM(int,ARGS)' in formula and PyTango.DevVarLongArray or
                     'SPECTRUM(float,ARGS)' in formula and PyTango.DevVarDoubleArray or
                     'SPECTRUM(str,ARGS)' in formula and PyTango.DevVarStringArray or
                     'SPECTRUM(bool,ARGS)' in formula and PyTango.DevVarBooleanArray or
                     'ARGS' in formula and PyTango.DevVarStringArray or
                     PyTango.DevVoid)
            ds_class.cmd_list[name] = [[itype, "ARGS"],[return_type, "result"],]
            #USING STATIC METHODS; THIS PART MAY BE SENSIBLE TO PyTANGO UPGRADES
            setattr(ds,name,lambda obj,argin=None,cmd_name=name:obj.evalCommand(cmd_name,argin))
            #lambda obj,argin=None,cmd_name=name: (obj._locals.update((('ARGS',argin),)),obj.evalAttr(ds.dyn_comms[obj.get_name()+'/'+cmd_name]))[-1])
    print('Out of DynamicDS.CreateDynamicCommands(%s)'%(server,))
    return

#==================================================================
#
#    Fandango DynamicDS Server main method
#
#==================================================================

class DynamicServer(object):
    """
    The DynamicServer class provides .util .instance .db .classes to have access to Tango DS internals.
    
    To load your own custom classes you can override the load_class method to modify how classes are generated (see CopyCatDS as example)
    """
    
    PROPERTY = 'PYTHON_CLASSPATH'
    
    def __init__(self,name='',classes={},add_debug=False,log='-v2',orb=[]):
        if not name:
            server,instance,logs,orb = self.parse_args(log=log)
            self.name = server+'/'+instance
        else:
            self.name,server,instance,logs = \
                name,name.split('/')[0],name.split('/')[-1],log
        self.args = [server,instance,logs]+orb
        
        print('In DynamicServer(%s)'%(self.args,))
        self.util = PyTango.Util(filter(bool,self.args))
        self.instance = self.util.instance()
        self.db = self.instance.get_database()
        class_list = self.db.get_device_class_list(self.instance.get_ds_name()) #Device,Class object list
        self.classes = fn.dicts.defaultdict(list)
        [self.classes[c].append(d) for d,c in zip(class_list[::2],class_list[1::2]) if c.lower()!='dserver']
        for C,devs in classes.items():
            for d in devs:
                if C not in self.classes or d not in self.classes[C]:
                    fn.tango.add_new_device(self.name,C,d)
                    self.classes[C].append(d)
        self.path = (self.db.get_property(self.PROPERTY,['DeviceClasses'])['DeviceClasses'] or [''])[0]
        if self.path: sys.path.append(self.path)
        self.modules = {}
        [self.load_class(c) for c in self.classes]
        print('\nDynamicDS: %d classes loaded: %s'%(len(self.classes),','.join(self.classes)))
        if add_debug and 'DDebug' not in self.classes:
            from fandango.device import DDebug
            DDebug.addToServer(self.util,*(self.name.split('/')))
        
    def parse_args(self,args=[],log='-v2'):
        import sys
        if not args:args = sys.argv
        assert len(args)>=2,'1 argument required!:\n\tpython dynamic.py instance [-vX]'
        print(args)
        server = args[0] if not fn.re.match('^(.*[/])?dynamic.py$',args[0]) else 'DynamicServer'
        instance = args[1]
        logs,orb = log if instance!='-?' else '',[]
        for i in (2,3):
            if args[i:]:
                if args[i].startswith('-v'):
                    logs = args[i]
                else:
                    orb = args[i:i+2]
                    break
            else: break
        ds_name = server+'/'+instance
        return (server,instance,logs,orb)
                    
    def load_class(self,c):
        try:
            if c in locals():
                return locals[c]
            p = (self.db.get_property(self.PROPERTY,[c])[c] or [''])[0]
            print('\nLoading %s from %s' % (c,p or self.path))
            if p:
                self.modules[c] = fn.objects.loadModule(p)
            elif c in dir(fn.device):
                self.modules[c] = fn.device
            elif c in dir(fn.interface):
                self.modules[c] = fn.interface
            else:
                try:
                    self.modules[c] = fn.objects.loadModule(c)
                    assert getattr(self.modules[c],c+'Class')
                except:
                    m = self.path+'/%s/%s.py'%(c,c)
                    print('\nLoading %s from %s' % (c,m))
                    self.modules[c] = fn.objects.loadModule(m)
            k, i, n = getattr(self.modules[c],c+'Class'),getattr(self.modules[c],c),c
            self.util.add_TgClass(k,i,n)
            CreateDynamicCommands(i,k)
        except:
            traceback.print_exc()
            sys.exit(-1)
        
    def main(self,args=None):
        #Args argument has no effect! @TODO
        print('DynamicDS.main(%s)'%(args or sys.argv,))
        U = self.util.instance()
        U.server_init()
        U.server_run()

__doc__ = fn.doc.get_fn_autodoc(__name__,vars(),module_vars=['DynamicDSTypes'])
        
if __name__ == '__main__':
    print('.'*80)
    pyds = DynamicServer(add_debug=True)
    print('loaded ...')
    pyds.main()
    print('launched ...')
    
    #try:
        #py = PyTango.Util(sys.argv)
        ## Adding all commands/properties from fandango.DynamicDS
        #PySignalSimulator,PySignalSimulatorClass = FullTangoInheritance('PySignalSimulator',PySignalSimulator,PySignalSimulatorClass,DynamicDS,DynamicDSClass,ForceDevImpl=True)
        #py.add_TgClass(PySignalSimulatorClass,PySignalSimulator,'PySignalSimulator')

        #U = PyTango.Util.instance()
        #fandango.dynamic.CreateDynamicCommands(PySignalSimulator,PySignalSimulatorClass)
        #U.server_init()
        #U.server_run()

    #except PyTango.DevFailed,e:
        #print '-------> Received a DevFailed exception:',traceback.format_exc()
    #except Exception,e:
        #print '-------> An unforeseen exception occured....',traceback.format_exc()
#else:
    ##Enabling subclassing
    #PySignalSimulator,PySignalSimulatorClass = FullTangoInheritance('PySignalSimulator',PySignalSimulator,PySignalSimulatorClass,DynamicDS,DynamicDSClass,ForceDevImpl=True)    
    
    
