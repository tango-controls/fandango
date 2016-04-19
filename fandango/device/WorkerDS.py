#!/usr/bin/env python

#############################################################################
##
## file :    WorkerDS.py
##
## description : Device Server that processes attributes.
##               Python source for the WorkerDS and its commands. 
##               The class is derived from Device. It represents the
##               CORBA servant object which will be accessed from the
##               network. All commands which can be executed on the
##               WorkerDS are implemented in this file.
##               Based on the code of PySignalSimulator by srubio
##
## project :    Tango-ds
##
## developers history: srubio@cells.es
##
## $Revision:  $
##
## $Log:  $
##
## copyleft :    Cells / Alba Synchrotron
##               Bellaterra
##               Spain
##
#############################################################################
##
## This file is part of Tango-ds.
##
## This is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## This software is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
###########################################################################


import sys,traceback,math,random,time,imp
from re import match,search,findall

import PyTango,fandango
from fandango import functional
from fandango import tango
from fandango import CaselessDict,SortedDict,CaselessDefaultDict
from fandango.dynamic import DynamicDS,DynamicDSClass,DynamicAttribute
from fandango.interface import FullTangoInheritance
from fandango.threads import wait

def get_module_dict(module,ks=None):
    return dict((k,v) for k,v in module.__dict__.items() if (not ks or k in ks) and not k.startswith('__'))


#==================================================================
#   WorkerDS Class Description:
#   
#   Device Server that processes attributes. Based on the code of PySignalSimulator by srubio
#
#==================================================================
    
class WorkerDS(PyTango.Device_4Impl):

    #--------- Add you global variables here --------------------------
    LIBS = [fandango.functional] #math,random,scipy,scipy.signal] #IMPORTED AS "from module import *
    NAMES = [] #Objects from locals() to be passed to the eval worker
    OTHERS = {'fun':fandango.functional} #Use this dictionary to declare aliases
    
    def update_tasks(self):
      while not self.event.isSet():
        self.last_check = time.time()
        self.info('-'*70)
        self.info( 'In WorkerDS::updateTasks ...')
        self._state = (PyTango.DevState.RUNNING)
        for task,commands in self.tasks.items():
          if task not in self.conditions:
            self.warning('\t%s not scheduled!'%task)
            continue
          if not commands[-1].startswith(task) and ' = ' not in commands[-1]:
            commands[-1] = commands[-1].replace('return ','')
            commands[-1] = task+'_result = '+commands[-1]
          try:
            self.worker.get(commands[-1])
            self.dones[task] = time.time()
          except:
            pass
          try:
            self.update_locals(task=task)
            self.info( 'In WorkerDS::updateTasks(%s): %s'%(task,commands))
            if functional.evalX(self.conditions[task],_locals=self.locals()):
              if not self.dones[task]>=self.sends[task]:
                self.warning('In WorkerDS::updateTasks(%s): still running since %s!!!'%(task,fandango.time2str(self.sends[task])))
              else:
                self.info( 'In WorkerDS::updateTasks(%s)'%task)
                map(self.worker.put,commands)
                self.sends[task] = time.time()
          except:
            self.error(traceback.format_exc())
          wait(.1,self.event)
      
        self.info(' ---- Waiting %s seconds ---- '%self.PollingSeconds)
        self._state = PyTango.DevState.ON
        while not self.waiter.isSet() and time.time()<(self.last_check+int(self.PollingSeconds)):
          status = ['Worker DS waiting %s s for next cycle ..'%self.PollingSeconds]
          status.append('Last check was at %s'%fandango.time2str(self.last_check))
          status.append('')
          for task,commands in sorted(self.tasks.items()):
            if not commands[-1].startswith(task) and ' = ' not in commands[-1]:
              commands[-1] = commands[-1].replace('return ','')
              commands[-1] = task+'_result = '+commands[-1]            
            try:
              self.worker.get(commands[-1])
              self.dones[task] = time.time()
            except:
              pass
            if self.dones[task]>self.sends[task]:
              status.append('%s: Finished at %s'%(task,fandango.time2str(self.dones[task])))
            elif self.sends[task]>self.dones[task]:
              status.append('%s: Launched at %s'%(task,fandango.time2str(self.sends[task])))
          self._status = ('\n'.join(status))
          wait(1.,self.waiter)
        self.waiter.clear()
          
      print '#'*80
      print '#'*80
          
        
    def get_task_conditions(self,prop=None):
       prop = prop or self.TaskConditions
       prop = [p.split('#')[0].strip() for p in prop]
       prop = filter(bool,prop)
       return CaselessDict(p.split(':',1) for p in prop)
      
    def update_locals(self,_locals=None,update=False,task=None):
        if _locals is None: _locals = {}
        try:
            date = fandango.time2date()
            _locals['t'] = time.time() #TIME MUST BE ABSOLUTE!!!
            _locals['minute'] = date.minute
            _locals['hour']=date.hour
            _locals['day']=date.day
            _locals['weekday']=date.weekday()
            _locals['CURRENT'] = task
            _locals['LAST'] = self.dones[task]
            _locals.update(dict(zip('DOMAIN FAMILY MEMBER'.split(),self.get_name().split('/'))))
            _locals.update({'DEVICE':self.get_name(),'SELF':self}) #,'ALARMS':self.Alarms.keys(),'PANIC':self.Panic,'SELF':self})
            self._locals.update(_locals)
            self.worker._locals.update([(k,v) for k,v in self._locals.items()
              if (k in _locals or k in self.extra_modules) 
                and k not in self.tasks])
            #if check:
                #for k,v in self.Alarms.items():
                    #val = v.active if not self.CheckDisabled(k) else False
                    #if _locals.get(k,None)!=val: update = True
                    #_locals[k] = val
            #if update:
                #self.debug('In PyAlarm.update_locals(...)')
                #if self.worker:
                    #try:
                        #self.worker.send('update_locals',
                            #target='update_locals',
                            #args={'dct':dict((k,v) for k,v in _locals.items() if k in self.Panic)},
                            #callback=None)
                    #except: 
                        #self.error('worker.send(update_locals) failed!: %s'%traceback.format_exc())
                        #self.info(str(_locals))
                #else: 
                    #self.Eval.update_locals(_locals)
                    #if self.get_name()+'/'+self.Alarms.keys()[0] not in self.Eval.attributes:
                        #self.Eval.attributes.update(dict((str(n).lower(),fandango.tango.CachedAttributeProxy(n,fake=True))
                            #for n in (self.get_name()+'/'+k for k in self.Alarms) ))
                    #[self.Eval.attributes[self.get_name()+'/'+k].set_cache(_locals[k]) for k in self.Alarms]
        except:
            self.warning(traceback.format_exc())
        return self.locals()
    
    #------------------------------------------------------------------
    #    Device constructor
    #------------------------------------------------------------------
    def __init__(self,cl, name):
        #PyTango.Device_4Impl.__init__(self,cl,name)
        print 'IN WorkerDS.__INIT__'
        _locals = {}
        [_locals.update(get_module_dict(m)) for m in self.LIBS]
        _locals.update((k.__name__,k) for k in self.NAMES)
        _locals.update(self.OTHERS)
        _locals['TASK'] = lambda t,s=self:s.worker.locals(t+'_result') if t in s.tasks else None
        #print '_locals are:\n%s' % _locals
        DynamicDS.__init__(self,cl,name,_locals=_locals,useDynStates=True)
        WorkerDS.init_device(self)

    #------------------------------------------------------------------
    #    Device destructor
    #------------------------------------------------------------------
    def delete_device(self):
        print "[Device delete_device method] for device",self.get_name()
        try:
          self.event.set()
          self.waiter.set()
          self.thread.join()
          self.worker.stop()
        except:
          traceback.print_exc()
        self.worker = None
        print 'done ...'

    #------------------------------------------------------------------
    #    Device initialization
    #------------------------------------------------------------------
    def init_device(self):
        print "In ", self.get_name(), "::init_device{}(%s)"%self.get_init_count()
        try: 
            DynamicDS.init_device(self) #New in Fandango 11.1
        except:
            self.get_DynDS_properties() #LogLevel is already set here
        try:[sys.path.insert(0,p) for p in self.PYTHONPATH if p not in sys.path]
        except: traceback.print_exc()
        self.setLogLevel('INFO')
        default_props = dict((k,v[-1]) for k,v in WorkerDSClass.device_property_list.items())
        all_props = (tango.get_matching_device_properties(self.get_name(),'*'))

        missing = [k for k,v in default_props.items() if v and k.lower() not in map(str.lower,all_props)]
        if missing:
          print('Updating default property values')
          print default_props.keys()
          print all_props.keys()
          print missing
          self.get_db().put_device_property(self.get_name(),dict((k,default_props[k]) for k in missing))
        
        #TASKS IS NOT CASELESS TO KEEP THE ORIGINAL NAME OF THE TASK
        self.tasks = dict((k,v) for k,v in all_props.items() if k.lower() not in map(str.lower,default_props))
        self.sends = CaselessDefaultDict(int)
        self.dones = CaselessDefaultDict(int)
        self.conditions = self.get_task_conditions()
        self.TStarted = time.time()
        self.StaticAttributes = ['%s = str(TASK("%s") or "")'%(t,t) for t in self.tasks]
        self.StaticAttributes += ['LastCheck = self.last_check']
        self.parseStaticAttributes()
        self.info('Loaded %d tasks: %s'%(len(self.tasks),self.tasks.keys()))

        for m in self.ExtraModules:
            self.extra_modules = {}
            try: 
              self.info('Loading ExtraModules(%s)'%m)
              m,k = m.split(' as ') if (' as ' in m) else (m,'')
              m = m.strip().split('.')
              if not m: continue
              k = k or m[-1]
              if k not in self._locals: 
                if m[0] in ('sys','os'): 
                  raise Exception('%s not allowed'%str(m))
                print '%s.init_device(): loading %s as %s' % (self.get_name(),m,k)
                l = imp.load_module(m[0],*imp.find_module(m[0]))
                if len(m)==1:
                  self._locals[k or m[0]] = l
                elif m[1]=='*':
                  self._locals.update(get_module_dict(l))
                else:
                  self._locals[k or m[1]] = l.__dict__[m[1]]
              self.extra_modules[k] = self._locals[k]
            except: traceback.print_exc()
            
        self.set_state(PyTango.DevState.INIT)
        self.Start()
        print "Out of ", self.get_name(), "::init_device()"

    #------------------------------------------------------------------
    #    Always excuted hook method
    #------------------------------------------------------------------
    def always_executed_hook(self):
        #print "In ", self.get_name(), "::always_excuted_hook()"
        try:
          self.update_locals()
          DynamicDS.always_executed_hook(self)
          if self.last_check < (time.time()-1.5*self.PollingSeconds):
            self.set_state(PyTango.DevState.FAULT)
          else:
            self.set_state(self._state)
          self.set_status(self._status)
        except:
          self.warning(traceback.format_exc())

#==================================================================
#
#    WorkerDS read/write attribute methods
#
#==================================================================
#------------------------------------------------------------------
#    Read Attribute Hardware
#------------------------------------------------------------------
    def read_attr_hardware(self,data):
        #print "In ", self.get_name(), "::read_attr_hardware()"
        pass
      
    def read_TasksSent(self,attr):
        pass
      
    def read_TasksDone(self,attr):
        pass
      
    def read_LastCheck(self,attr):
        pass

#==================================================================
#
#    WorkerDS command methods
#
#==================================================================

    def Go(self):
        return self.waiter.set()
      
    def Start(self):
        if not getattr(self,'worker',None):
          self.worker = fandango.SingletonWorker()
          self.worker._locals = self.locals()
          self.worker.start()
          import threading
          self.event = threading.Event()
          self.waiter = threading.Event()
          self.thread = threading.Thread(target=self.update_tasks)
          self.thread.start()
          self.info('THREADS STARTED!!')
    
#==================================================================
#
#    WorkerDSClass class definition
#
#==================================================================
class WorkerDSClass(PyTango.DeviceClass):

    #    Class Properties
    class_property_list = {
        }


    #    Device Properties
    device_property_list = {
        'ExtraModules':
            [PyTango.DevVarStringArray,
            "Extra modules to be available for attribute evaluation.",
            [ "fandango.functional as fun","re","traceback","time",] ],
        'PYTHONPATH':
            [PyTango.DevVarStringArray,
            "Extra folders to add in pythonpath.",
            [ ] ],
        'TaskConditions':
            [PyTango.DevVarStringArray,
            "Tasks will be automatically executed whenever condition is met. t,minute,hour,day,weekday can be used for cron-like conditions.",
            [ "FirstTask:'FirstTask' not in locals()","HourlyTask:minutes==0", "WeeklyTask:weekday==0", "OtherTask:minutes%20" ] ],
        'PollingSeconds':
            [PyTango.DevLong,
             "TaskConditions polling period, in seconds",
             [ 60. ] ],
        'DynamicAttributes':
            [PyTango.DevVarStringArray,
            "Attributes and formulas to create for this device.\n<br/>\nThis Tango Attributes will be generated dynamically using this syntax:\n<br/>\nT3=int(SomeCommand(7007)/10.)\n\n<br/>\nSee the class description to know how to make any method available in attributes declaration.",
            [ ] ],
        'DynamicStates':
            [PyTango.DevVarStringArray,
            "This property will allow to declare new States dinamically based on\n<br/>\ndynamic attributes changes. The function Attr will allow to use the\n<br/>\nvalue of attributes in formulas.<br/>\n\n\n<br/>\nALARM=Attr(T1)>70<br/>\nOK=1",
            [ ] ],
        }


    #    Command definitions
    cmd_list = {
        'Go':
            [[PyTango.DevVoid, "Jumps directly to next iteration"],
            [PyTango.DevVoid, "Jumps directly to next iteration"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],      
        'Start':
            [[PyTango.DevVoid, "Start Tasks execution"],
            [PyTango.DevVoid, "Start Tasks execution"],
            {
                'Display level':PyTango.DispLevel.EXPERT,
             } ],                  
        }


    #    Attribute definitions
    attr_list = {
        }


#------------------------------------------------------------------
#    WorkerDSClass Constructor
#------------------------------------------------------------------
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name);
        print "In WorkerDSClass  constructor"
        
#==================================================================
#
#    WorkerDS class main method
#
#==================================================================
        
WorkerDS,WorkerDSClass = FullTangoInheritance('WorkerDS',WorkerDS,WorkerDSClass,DynamicDS,DynamicDSClass,ForceDevImpl=True)
        
def main(args=None):
    args = args or sys.argv
    try:
        py = PyTango.Util(args)
        # Adding all commands/properties from fandango.DynamicDS
        from fandango.device.WorkerDS import WorkerDS,WorkerDSClass
        WorkerDS,WorkerDSClass = FullTangoInheritance('WorkerDS',WorkerDS,WorkerDSClass,DynamicDS,DynamicDSClass,ForceDevImpl=True)
        py.add_TgClass(WorkerDSClass,WorkerDS,'WorkerDS')
        U = PyTango.Util.instance()
        U.server_init()
        U.server_run()

    except PyTango.DevFailed,e:
        print '-------> Received a DevFailed exception:',e
    except Exception,e:
        print '-------> An unforeseen exception occured....',e  

if __name__ == '__main__':
    main()
