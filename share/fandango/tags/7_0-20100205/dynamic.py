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
import sys
import inspect
import threading
import time
import traceback
from PyTango import AttrQuality
from PyTango import DevState
import log
from excepts import *
#from .excepts import Catched,ExceptionManager
#from  . import log

print 'LOADING DYNAMIC DEVICE SERVER TEMPLATE, released 2009/11/17'
if 'Device_4Impl' not in dir(PyTango): PyTango.Device_4Impl = PyTango.Device_3Impl
if 'DeviceClass' not in dir(PyTango): PyTango.DeviceClass = PyTango.PyDeviceClass

class DynamicDS(PyTango.Device_4Impl,log.Logger):
    ''' Check fandango.dynamic.__doc__ for more information ...'''

    ######################################################################################################
    # INTERNAL DYNAMIC DEVICE SERVER METHODS
    ######################################################################################################

    def __init__(self,cl=None,name=None,_globals=globals(),_locals={}, useDynStates=True):
        self.call__init__(log.Logger,name,format='%(levelname)-8s %(asctime)s %(name)s: %(message)s')
        self.setLogLevel('DEBUG')
        self.info( ' in DynamicDS.__init__ ...')
        self.trace=False

        #Tango Properties
        self.DynamicAttributes = []
        self.DynamicStates = []
        #Internals
        self.dyn_attrs = {}
        self.dyn_types = {}
        self.dyn_states = {}
        self.dyn_values = {}
        self.variables = {}

        ##Local variables and methods to be bound for the eval methods
        self._globals=globals().copy()
        self._globals.update(_globals)
        self._locals={'self':self}
        self._locals['Attr'] = lambda _name: self.getAttr(_name)
        self._locals['ATTR'] = lambda _name: self.getAttr(_name)
        self._locals['XAttr'] = lambda _name: self.getXAttr(_name)
        self._locals['XATTR'] = lambda _name: self.getXAttr(_name)
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
        [self._locals.__setitem__(str(quality),quality) for quality in AttrQuality.values.values()]
        for k,v in DevState.values.items():
            self._locals[str(v)]=k
        self._locals.update(_locals) #New submitted methods have priority over the old ones

        # Internal object references
        self.__prepared = False
        self.myClass = None
        
        ## This list stores XAttr valid arguments, must be replaced some day by a TauFactory() call
        self._external_attributes = set()

        self.time0 = time.time()
        self.simulationMode = False #If it is enabled the ForceAttr command overwrites the values of dyn_values
        self.clientLock=False #TODO: This flag allows clients to control the device edition, using isLocked(), Lock() and Unlock()
        self.lastAttributeValue = None #TODO: This variable will be used to keep value/time/quality of the last attribute read using a DeviceProxy
        self.last_state_exception = ''
        self.last_attr_exception = ''
        self._hook_epoch = 0
        self._cycle_start = 0
        self._total_usage = 0
        self._read_times = {}
        self._eval_times = {}

        self.TangoStates = ['ON','OFF','CLOSE','OPEN','INSERT','EXTRACT','MOVING','STANDBY','FAULT','INIT','RUNNING','ALARM','DISABLE','UNKNOWN']
        self.useDynStates = useDynStates
        if self.useDynStates:
            self.info('useDynamicStates is set, disabling automatic State generation by attribute config.'+
                    'States fixed with set/get_state will continue working.')
            self.State=self.rawState

        self.call__init__('Device_4Impl' in dir(PyTango) and PyTango.Device_4Impl or PyTango.Device_3Impl,cl,name)

    def delete_device(self):
        self.info( 'DynamicDS.delete_device(): ... ')
        ('Device_4Impl' in dir(PyTango) and PyTango.Device_4Impl or PyTango.Device_3Impl).delete_device(self)

    def prepare_DynDS(self):
        """
        This code is placed here because its proper execution cannot be guaranteed during init_device().
        """
        if self.myClass is None:
            self.myClass = self.get_device_class()
        #if self.myDeviceProxy is None:
            ##self.lock.acquire()
            #self.myDeviceProxy=PyTango.DeviceProxy(self.get_name())
            ##if not self.myDeviceProxy.is_attribute_polled('State'): #TODO: It forces State attribute polling
                ##pass
            ##self.lock.release()
        return

    def always_executed_hook(self):
        #print "In DynamicDS::always_executed_hook()"
        try:
            self._hook_epoch = time.time() #Internal debugging
            if not self.__prepared: self.prepare_DynDS() #This code is placed here because its proper execution cannot be guaranteed during init_device()
            self.myClass.DynDev=self #VITAL: It tells the admin class which device attributes are going to be read
            if self.dyn_states: self.check_state()
        except:
            self.last_state_exception = 'Exception in DynamicDS::always_executed_hook():\n'+str(traceback.format_exc())
            self.error(self.last_state_exception)
        return
            
    def read_attr_hardware(self,data):
        self.debug("In DynDS::read_attr_hardware()")
        try:
            attrs = self.get_device_attr()
            for d in data:
                a_name = attrs.get_attr_by_ind(d).get_name()
                if a_name in self.dyn_attrs:
                    pass
        except Exception,e:
            self.last_state_exception = 'Exception in read_attr_hardware: %s'%str(e)
            self.error('Exception in read_attr_hardware: %s'%str(e))                

    def get_DynDS_properties(self,db=None):
        """
        It forces Device properties reading using the Database device.
        It is used by self.updateDynamicAttributes() and required in PyTango<3.0.4
        """
        if not db: db = PyTango.Database()
        
        props = db.get_class_property(self.get_name(),['DynamicSpectrumSize'])
        for p in props.keys(): self.info(self.get_name()+'.'+str(p)+'="'+str(props[p])+'"')
        self.DynamicSpectrumSize=props['DynamicSpectrumSize']        
        
        props = db.get_device_property(self.get_name(),['DynamicAttributes','DynamicStates','DynamicImports','DynamicQualities'])
        for p in props.keys(): self.info(self.get_name()+'.'+str(p)+'="'+str(props[p])+'"')
        self.DynamicAttributes=props['DynamicAttributes']
        self.DynamicStates=props['DynamicStates']
        self.DynamicImports=props['DynamicImports']
        self.DynamicQualities=props['DynamicQualities']
        
    def get_device_property(self,property,update=False):
        if update or not hasattr(self,property):
            setattr(self,property,PyTango.Database().get_device_property(self.get_name(),[property])[property])
        value = getattr(self,property) 
        return value[0] if type(value) is list else value

    def check_polled_attributes(self,db=None,new_attr={}):
        '''
        If a PolledAttribute is removed of the Attributes declaration it can lead to SegmentationFault at Device Startup.
        polled_attr property must be verified to avoid that.
        The method .get_device_class() cannot be called to get the attr_list value for this class,
        therefore new_attr must be used to add to the valid attributes any attribute added by subclasses
        Polling configuration configured through properties has preference over the hard-coded values.
        '''
        self.info('In check_polled_attributes ...')
        self.db = db = db or (hasattr(self,'db') and getattr(self,'db')) or PyTango.Database()
        my_name = self.get_name()
        
        new_attr = dict.fromkeys(new_attr,3000) if isinstance(new_attr,list) else new_attr
        props = db.get_device_property(my_name,['DynamicAttributes','polled_attr'])
        pattrs,npattrs = props['polled_attr'],[]
        
        dyn_attrs = [k.split('=')[0].lower() for k in props['DynamicAttributes'] if k and not k.startswith('#')]
        dyn_attrs.extend(k.lower() for k in new_attr.keys()) #dyn_attrs will contain both dynamic attributes and new aggregated attributes.
        dyn_attrs.extend(['state','status'])
        
        #First: propagate all polled_attrs if they appear in the new attribute list
        for i in range(len(pattrs))[::2]:
            att = pattrs[i].lower()
            period = att in new_attr and new_attr[att] or pattrs[i+1]
            if att in dyn_attrs: 
                (npattrs.append(att),npattrs.append(period))
            else: 
                self.info('Attribute %s removed from %s.polled_attr Property' % (pattrs[i],my_name))
                
        #Second: add new attributes to the list of attributes to configure; attributes where value is None will not be polled
        for n,v in new_attr.iteritems():
            if n not in npattrs and v:
                (npattrs.append(n),npattrs.append(v))
                self.info('Attribute %s added to %s.polled_attr Property' % (n,my_name))
                
        db.put_device_property(my_name,{'polled_attr':npattrs})
        self.info('Out of check_polled_attributes ...')

    #------------------------------------------------------------------------------------------------------
    #   Attribute creators and read_/write_ related methods
    #------------------------------------------------------------------------------------------------------

    ## Dynamic Attributes Creator
    def dyn_attr(self):
        """
        Dynamic Attributes Creator: It initializes the device from DynamicAttributes and DynamicStates properties.
        It is called by all DeviceNameClass classes that inherit from DynamicDSClass.
        It is an static method.
        """
        self.debug('DynamicDS.dyn_attr( ... ), entering ...')

        if not hasattr(self,'DynamicStates'):
            self.error('DynamicDS property NOT INITIALIZED!')
            
        for line in self.DynamicStates:
            # The character '#' is used for comments
            if not line.strip() or line.strip().startswith('#'): continue
            fields = (line.split('#')[0]).split('=',1)
            if not fields or len(fields) is 1 or '' in fields:
                self.debug( self.get_name()+".dyn.attr(): wrong format in DynamicStates Property!, "+line)
                continue
            else:
                self.dyn_states[fields[0].upper()]={'formula':fields[1],'compiled':compile(fields[1].strip(),'<string>','eval')}
                self.info(self.get_name()+".dyn_attr(): new DynamicState '"+ fields[0]+"' = '"+fields[1]+"'")

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
                if bool(aname not in self.dyn_values): 
                    create = True
                    self.dyn_values[aname]=DynamicAttribute()
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
                except: pass
                self.dyn_values[aname].type=self.dyn_types[aname]
                self.dyn_values[aname].type=self.dyn_attrs[aname]

                #Adding attributes to DynamicStates queue:
                for k,v in self.dyn_states.items():
                    if aname in v['formula']:
                        #self.dyn_values[aname]=None
                        self.dyn_values[aname].states_queue.append(k)
                        self.info("DynamicDS.dyn_attr(...): Attribute %s added to attributes queue for State %s"%(aname,k))
        print 'DynamicDS.dyn_attr( ... ), finished. Attributes ready to accept request ...'

    #dyn_attr=staticmethod(dyn_attr) #dyn_attr is an static method.

    def get_dyn_attr_list(self):
        """Gets all dynamic attribute names."""
        return self.dyn_attrs.keys()

    def is_dyn_allowed(self,req_type,attr_name=''):
        return True

    #@Catched #Catched decorator is not compatible with PyTango_Throw_Exception
    def read_dyn_attr(self,attr,fire_event=True):
        aname = attr.get_name()
        tstart=time.time()
        self.debug("DynamicDS("+self.get_name()+")::read_dyn_atr("+attr.get_name()+"), entering at "+time.ctime()+"="+str(tstart)+"...")
        #raise Exception,'DynamicDS_evalAttr_NotExecuted: searching memory leaks ...'
        try:
            result = self.evalAttr(aname)
            quality = self.get_quality_for_attribute(aname,result)
            date = self.get_date_for_attribute(aname,result)
            result = self.dyn_types[aname].pytype(result)

            if hasattr(attr,'set_value_date_quality'): 
              attr.set_value_date_quality(result,date,quality)
            else:
              if type(result) in (list,set,tuple):
                attr_DynAttr_read = []
                for r in result: attr_DynAttr_read.append(r)
                PyTango.set_attribute_value_date_quality(attr_DynAttr_read,date,quality,len(attr_DynAttr_read),0)
              else: PyTango.set_attribute_value_date_quality(attr,result,date,quality)

            ##if fire_event: self.fireAttrEvent(aname,result)
            #Value must be updated after fire Event
            self.dyn_values[aname].update(result,date,quality)

            text_result = type(result) is list and '%s[%s]'%(type(result[0]),len(result)) or str(result)
            now=time.time()
            self.debug('DynamicDS('+self.get_name()+").read_dyn_attr("+aname+")="+text_result+
                    ", ellapsed %1.2e"%(now-date)+" seconds.\n")
                    #", finished at "+time.ctime(now)+"="+str(now)+", timestamp is %s"%str(date)+", difference is "+str(now-date))
            self._read_times[aname]=now-self._hook_epoch
            self._eval_times[aname]=now-tstart
            self._total_usage += now-self._hook_epoch
            if aname==self.dyn_values.keys()[-1]: 
                self.info('-'*80)
                self._cycle_start = now-self._cycle_start
                self.info('Last complete reading cycle took: %f seconds' % self._cycle_start)
                for key in self._read_times:
                    self.info('%s read in %f s; eval in %f s; %f of the usage' % (key, self._read_times[key],self._eval_times[key],self._read_times[key]/self._total_usage))
                self.info('%f s empty seconds in total; %f of CPU Usage' % (self._cycle_start-self._total_usage,self._total_usage/self._cycle_start))
                self.info('%f of time used in expressions evaluation' % (sum(self._eval_times.values())/sum(self._read_times.values())))
                self._cycle_start = now
                self._total_usage = 0
                self.info('-'*80)
        except Exception, e:           
            now=time.time()
            self.dyn_values[aname].update(None,now,PyTango.AttrQuality.ATTR_INVALID)
            self._read_times[aname]=now-self._hook_epoch #Internal debugging
            self._eval_times[aname]=now-tstart #Internal debugging
            if aname==self.dyn_values.keys()[-1]: self._cycle_start = now
            #last_exc = getLastException()
            #last_exc = '\n'.join([str(e)]*4)
            last_exc = str(e)
            self.error('DynamicDS_read_dyn_attr_Exception: %s' % last_exc)
            print traceback.format_exc()
            raise Exception, 'DynamicDS_read_dyn_attr_Exception: %s' % last_exc
            #PyTango.Except.throw_exception('DynamicDS_read_dyn_attr_Exception',str(e),last_exc)

    read_dyn_attr=staticmethod(read_dyn_attr)

    @Catched
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
    def evalAttr(self,aname,WRITE=False,VALUE=None,_locals={}):
        ''' SPECIFIC METHODS DEFINITION DONE IN self._locals!!! 
        @remark Generators don't work  inside eval!, use lists instead
        '''
#            self.debug("DynamicDS("+self.get_name()+ ")::evalAttr("+aname+"): ...")
        if aname in self.dyn_attrs:
            formula,compiled = self.dyn_values[aname].formula,self.dyn_values[aname].compiled#self.dyn_attrs[aname]
        elif not any(aname in d for d in [_locals,self._globals,self._locals]) and aname.lower() in [s.lower() for s in self.dyn_attrs.keys()]:
            print 'Trying to find a caseless Attribute that match'
            for k in self.dyn_attrs:
                if k.lower()==aname.lower():
                    #formula = self.dyn_attrs[k]
                    formula,compiled = self.dyn_values[k].formula,self.dyn_values[k].compiled
                    break
        else:
            self.warning('DynamicDS.evalAttr: %s doesnt match any Attribute name, trying to evaluate ...'%aname)
            formula,compiled=aname,None
        try:
            __locals={}#locals().copy() #Low priority: local variables
            for k,v in self.dyn_values.items(): self._locals[k]=v#.value #Updating Last Attribute Values
            self._locals.update({
                't':time.time()-self.time0,
                'WRITE':WRITE,
                'READ':bool(not WRITE),
                'NAME':aname,
                'VALUE':VALUE,
                }) #It is important to keep this values persistent; becoming available for quality/date/state/status management
            __locals.update(self._locals) #Second priority: object statements
            __locals.update(_locals) #High Priority: variables passed as argument
            if not WRITE:
                result = eval(compiled or formula,self._globals,__locals)
                #text_result = type(result) is list and '%s[%s]'%(type(result[0]),len(result)) or str(result)
                #self.dyn_types[aname].pytype(result)
                return result
            else:
                self.debug('%s::evalAttr(WRITE): Attribute=%s; formula=%s; VALUE=%s'%(self.get_name(),aname,formula,str(VALUE)))
                return eval(compiled or formula,self._globals,__locals)

        except PyTango.DevFailed, e:
            if self.trace:
                print '\n'.join(['DynamicDS_evalAttr_WrongFormulaException','%s is not a valid expression!'%formula,str(traceback.format_exc())])
                print '\n'.join(traceback.format_tb(sys.exc_info()[2]))
                print '\n'.join([str(e.args[0])]) + '\n'+'*'*80
            #PyTango.Except.throw_exception('DynamicDS_evalAttr_WrongFormula','%s is not a valid expression!'%formula,str(e))
            err = e.args[0]
            raise Exception,';'.join([err.origin,err.reason,err.desc])
            #PyTango.Except.throw_exception(str(err.reason),str(err.desc),str(err.origin))

        except Exception,e:
            print '\n'.join(['DynamicDS_evalAttr_WrongFormulaException','%s is not a valid expression!'%formula,str(e)])
            print '\n'.join(traceback.format_tb(sys.exc_info()[2]))
            raise Exception,'DynamicDS_eval(%s): %s'%(formula,traceback.format_exc())
            #PyTango.Except.throw_exception('DynamicDS_evalAttr_WrongFormula','%s is not a valid expression!'%formula,str(traceback.format_exc()))
            
        finally: 
            print 'deleting __locals'
            del __locals

    # DYNAMIC STATE EVALUATION
    def evalState(self,formula,_locals={}):
        """
        Overloading the eval method to be used to evaluate State expressions
        ... To customize it: copy it to your device and add any method you will need
        @remark Generators don't work  inside eval!, use lists instead
        """
        self.debug('DynamicDS.evalState('+str(formula)+')')
        #MODIFIIED!! to use pure DynamicAttributes
        #Attr = lambda a: self.dyn_values[a].value
        t = time.time()-self.time0
        for k,v in self.dyn_values.items(): self._locals[k]=v#.value #Updating Last Attribute Values
        __locals=locals().copy() #Low priority: local variables
        __locals.update(self._locals) #Second priority: object statements
        __locals.update(_locals) #High Priority: variables passed as argument
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

    def getXAttr(self,aname):
        """
        Performs an external Attribute reading, using a DeviceProxy to read own attributes.
        Argument could be: [attr_name] or [device_name](=State) or [device_name/attr_name]
        """
        device,aname = ('/' not in aname) and (None,aname) or aname.count('/')==2 and (aname,'State') or aname.rsplit('/',1)
        self.debug("DynamicDS(%s)::getXAttr(%s): ..."%(device or self.get_name(),aname))
        result = None
        try:
            if not device:
                self.info('getXAttr accessing to device itself ... using getAttr instead')
                result = self.getAttr(aname)
            else:
                devs_in_server = self.myClass.get_devs_in_server()

                if device in devs_in_server:
                    self.debug('getXAttr accessing a device in the same server ... using getAttr')
                    if aname.lower()=='state': result = devs_in_server[device].get_state()
                    elif aname.lower()=='status': result = devs_in_server[device].get_status() 
                    else: result = devs_in_server[device].getAttr(aname)
                else:
                    self.debug('getXAttr creating a DeviceProxy to %s' % device)
                    dp = PyTango.DeviceProxy(device)
                    if (device+aname) not in self._external_attributes and \
                        aname.lower() not in [a.lower() for a in dp.get_attribute_list()]:
                        raise Exception,'%s_AttributeDoesNotExist'%aname
                    
                    self.debug('%s.read_attribute(%s)'%(device or self.get_name(),aname))
                    attrval = dp.read_attribute(aname)
                    self._external_attributes.add(device+aname) ## @todo a TauDevice.get_attribute method should be used to check attribute availability
                    """ #TODO: One day the time/quality of the read attributes should be passed to the client
                    if self.lastAttributeValue is None: self.lastAttributeValue = PyTango._PyTango.AttributeValue()
                    if self.lastAttributeValue.time > attrval.time:
                        self.lastAttributeValue.time = attrval.time
                    if self.lastAttributeValue.quality < attrval.quality:
                        self.lastAttributeValue.quality = attrval.quality
                    """
                    result = attrval.value
        except:
            self.last_attr_exception = time.ctime()+': '+ 'Unable to read_attribute %s from device %s: %s' % (aname,device or self.get_name(),traceback.format_exc())
            self.error(self.last_attr_exception)
            #Exceptions are not re_thrown to allow other commands to be evaluated if this fails.
        finally:
            if hasattr(self,'myClass') and self.myClass:
                self.myClass.DynDev=self #NOT REDUNDANT: If a call to another device in the same server occurs this pointer could have been modified.
        return result


    def get_quality_for_attribute(self,aname,value):
        print 'In get_quality_for_attribute(%s,%s)' % (aname,value)
        try:
            if hasattr(self,'DynamicQualities') and self.DynamicQualities:
                ## DynamicQualities: (*)_VAL = ALARM if $_ALRM else VALID
                print 'Testing Dynamic Qualities ........'
                import re
                exprs = {}
                [exprs.__setitem__(line.split('=')[0].strip(),line.split('=')[1].strip()) for line in self.DynamicQualities if '=' in line and not line.startswith('#')]
                for exp,value in exprs.items():
                    if '*' in exp and '.*' not in exp: exp.replace('*','.*')
                    if not exp.endswith('$'): exp+='$'
                    match = re.match(exp,aname)
                    if match: 
                        print 'There is a Quality for this attribute!: '+str((aname,exp,value))
                        for group in (match.groups()):
                            value=value.replace('$',group,1)
                        quality = eval(value,{},self._locals.copy()) or PyTango.AttrQuality.ATTR_VALID
                        print 'And the quality is: '+str(quality)
                        return quality
            if type(value) is DynamicAttribute or DynamicAttribute in value.__class__.__bases__:
                return value.quality
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
        self.debug('In DynamicDS.State()='+self.TangoStates[state]+', overriding attribute-based State.')
        return state

    def set_full_status(self,status):
        if self.last_state_exception:
            status += '\nLast DynamicStateException was:\n\t'+self.last_state_exception
        if self.last_attr_exception:
            status += '\nLast DynamicAttributeException was:\n\t'+self.last_attr_exception
        self.set_status(status)

    def set_state(self,state):
        #print 'STATE ADDED TO LOCALS!!!'
        self._locals['State']=state
        PyTango.Device_4Impl.set_state(self,state)
        #print 'STATE ADDED TO LOCALS!!!'

    def check_state(self):
        '''    The thread automatically close if there's no activity for 5 minutes,
            an always_executed_hook call or a new event will restart the thread.
        '''
        dyn_states = self.dyn_states
        if not dyn_states:
            self.debug('Dynamic States is Empty!!!')
            return

        self.debug('In DynamicDS.check_state')
        ## @remarks: the device state is not changed if none of the DynamicStates evaluates to True
        #self.set_state(PyTango.DevState.UNKNOWN)
        self.last_state_exception = ''
        for state,value in dyn_states.items():
            nstate,formula,code=state,value['formula'],value['compiled']
            if nstate not in self.TangoStates: continue
            result=None
            try:
                result=self.evalState(code) #Use of self.evalState allows to overload it
            except Exception,e:
                self.error('DynamicDS(%s).check_state(): Exception in evalState(%s): %s'%(self.get_name(),formula,str(traceback.format_exc())))
                self.last_state_exception += '\n'+time.ctime()+': '+str(traceback.format_exc())
            if result:
                self.set_state(PyTango.DevState(self.TangoStates.index(nstate)))
                self.info('DynamicDS(%s.check_state(): State changed to %s=%s'%(self.get_name(),nstate,formula))
                break
        self.debug('DynamicDS.check_state: finished')
        return

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
        
        #self.dyn_types[aname]=dyntype
        #if aname not in self.dyn_values:
            #create = True
        #elif formula != self.dyn_values[aname].formula or dyntype != self.dyn_values[aname].type:
            ### If the attribute already exists but has changed it must be removed from the device:
            #self.remove_attribute(aname)
            #create = True
        #else: create = False        
        
        ##All attributes managed with dyn_attr() that does not appear in DynamicAttributes or StaticAttributes list will be removed!
        attrs_list = [name.split('=',1)[0].strip() for name in (self.DynamicAttributes + (hasattr(self,'StaticAttributes') and self.StaticAttributes or []))]
        for a in self.dyn_attrs:
            if a not in attrs_list:
                self.warning('DynamicDS.updateDynamicAttributes(): Removing Attribute!: %sn not in [%s]' % (a,attrs_list))
                try:
                    self.remove_attribute(a)
                except Exception,e:
                    self.error('Unable to remove attribute %s: %s' % (a,str(e)))
        self.dyn_attr()

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
        argout=str(self.evalAttr(str(argin)))
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
        }

    #    Command definitions
    cmd_list = {
        'updateDynamicAttributes':
            [[PyTango.DevVoid, ""],
            [PyTango.DevVoid, ""],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],
        "evaluateFormula":
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
        for dev in dev_list:
            dev.dyn_attr()
            
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
            
def loadDynamicCommands(server,ds,ds_class):
    """
    By convention all dynamic commands have argin=DevVarStringArray, argout=DevVarStringArray
    @todo an special declaration should allow to redefine that! DevComm(typein,typeout,code)
    
    The code to add a new command will be something like:
    #srubio: it has been added for backward compatibility
    PyPLC.WriteBit,PyPLCClass.cmd_list['WriteBit']=PyPLC.WriteFlag,[[PyTango.DevVarShortArray, "DEPRECATED, Use WriteFlag instead"], [PyTango.DevVoid, "DEPRECATED, Use WriteFlag instead"]]
    """
    db = PyTango.Database()
    classes = db.get_device_class_list(server)
    devs = [classes[i] for i in range(len(classes)-1) if classes[i+1]==ds_class.__name__]
    for dev in devs:
        dyn_comms = db.get_device_property(dev,['DynamicCommands'])['DynamicCommands']
        ##@todo implementation will be:
        # @li parse type of argin/argout from command declaration
        # @li create a dictionary containing {command:code}
        # @li assign a lambda to each command: lambda self,argin=None,cmd_name=COMMAND: evalAttr(dyn_comms[cmd_name])
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


