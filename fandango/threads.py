#!/usr/bin/env python2.5
"""
#############################################################################
##
## file :       threads.py
##
## description : see below
##
## project :     Tango Control System
##
## $Author: Sergi Rubio Manrique, srubio@cells.es $
##
## $Revision: 2011 $
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

by Sergi Rubio, 
srubio@cells.es, 
2010
"""
import time,Queue,threading,multiprocessing,traceback
import imp,__builtin__,pickle,re

from log import except2str,shortstr
from functional import *
from excepts import trial
from operator import isCallable
from objects import Singleton,Object,SingletonMap

try: from collections import namedtuple #Only available since python 2.6
except: pass

###############################################################################

_EVENT = threading.Event()

def wait(seconds):
    _EVENT.wait(seconds)
    
class FakeLock(object):
    """ Just for debugging, can replace a Lock when debugging a deadLock issue. """
    def acquire(self):pass
    def release(self):pass

class CronTab(object):
    """
    Line Syntax:
    #Minutes Hour DayOfMonth(1-31) Month(1-12) DayOfWeek(0=Sunday-6) Task
    00 */6 * * * /homelocal/sicilia/archiving/bin/cleanTdbFiles /tmp/archiving/tdb --no-prompt

    ct = fandango.threads.CronTab('* 11 24 08 3 ./command &') #command can be replaced by a callable task argument
    ct.match() #It will return True if actual time matches crontab condition, self.last_match stores last time check
        True
    ct.start()
        In CronTab(* 11 24 08 3 date).start()
        CronTab thread started

        In CronTab(* 11 24 08 3 date).do_task(<function <lambda> at 0x8cc4224>)
        CronTab(* 11 24 08 3 date).do_task() => 3
        
    ct.stop()

    """
    def __init__(self,line='',task=None,start=False,process=False,keep=10,trace=False):
        if line: self.load(line)
        if task is not None: self.task = task
        self.last_match = 0
        self.trace = trace
        self.keep = keep
        
        self.THREAD_CLASS = threading.Thread if not process else multiprocessing.Process
        self.QUEUE_CLASS = Queue.Queue if not process else multiprocessing.Queue
        self.EVENT_CLASS = threading.Event if not process else multiprocessing.Event
        self.LOCK_CLASS = threading.RLock if not process else multiprocessing.RLock

        self._thread = None
        self.event = None
        self._queue = self.QUEUE_CLASS(maxsize=int(self.keep or 10))
        if start: self.start()
        
    def load(self,line):
        """
        Crontab line parsing
        """
        print 'In CronTab().load(%s)'%line
        vals = line.split()
        if len(vals)<5: raise Exception('NotEnoughArguments')
        self.minute,self.hour,self.day,self.month,self.weekday = vals[:5]
        if vals[5:] or not getattr(self,'task',None): self.task = ' '.join(vals[5:])
        self.line = line
        
    def _check(self,cond,value):
        if '*'==cond: return True
        elif '*/' in cond: return not int(value)%int(cond.replace('*/',''))
        else: return int(cond)==int(value)
        
    def match(self,now=None):
        """
        Returns True if actual timestamp matches cron configuration
        """
        if now is None: now=time.time()
        self.last_match = now-(now%60)
        tt = time2tuple(now)
        if all(self._check(c,v) for c,v in 
            zip([self.minute,self.hour,self.day,self.month,self.weekday],
                [tt.tm_min,tt.tm_hour,tt.tm_mday,tt.tm_mon,tt.tm_wday+1])
            ):
                return True
        else:
            return False
        
    def changed(self,now=None):
        """
        Checks if actual timestamp differs from last cron check
        """
        if now is None: now=time.time()
        return (now-(now%60))!=self.last_match
        
    def do_task(self,task=None,trace=False):
        """
        Executes an string or callable
        """
        trace = trace or self.trace
        task = task or self.task
        if trace: print 'In CronTab(%s).do_task(%s)'%(self.line,task)
        if isCallable(task):
            ret = task()
        elif isString(task):
            from fandango.linos import shell_command
            ret = shell_command(self.task)
        else:
            raise Exception('NotCallable/String')
        if self.keep:
            if self._queue.full(): self.get()
            self._queue.put(ret,False)
        if trace: 
            print 'CronTab(%s).do_task() => %s'%(self.line,ret)
            
    def get(self):
        return self._queue.get(False)
        
    def _run(self):
        print 'CronTab thread started' 
        from fandango.linos import shell_command
        while not self.event.is_set():
            now = time.time()
            if self.changed(now) and self.match(now):
                try:
                    self.do_task()
                except:
                    print 'CronTab thread exception' 
                    print traceback.format_exc()
            self.event.wait(15)
        print 'CronTab thread finished' 
        return 
        
    def start(self):
        print 'In CronTab(%s).start()'%self.line
        if self._thread and self._thread.is_alive:
            self.stop()
        import threading
        self._thread = self.THREAD_CLASS(target=self._run)
        self.event = self.EVENT_CLASS()
        self._thread.daemon = True
        self._thread.start()
        
    def stop(self):
        print 'In CronTab(%s).stop()'%self.line
        if self._thread and self._thread.is_alive:
            self.event.set()
            self._thread.join()
            
    def is_alive(self):
        if not self._thread: return False
        else: return self._thread.is_alive()
    
###############################################################################

WorkerException = type('WorkerException',(Exception,),{})

class WorkerThread(object):
    """
    This class allows to schedule tasks in a background thread or process
    
    If no process() method is overriden, the tasks introduced in the internal queue using put(Task) method may be:
         
         - dictionary of built-in types: {'__target__':callable or method_name,'__args__':[],'__class_':'','__module':'','__class_args__':[]}
         - string to eval: eval('import $MODULE' or '$VAR=code()' or 'code()')
         - list if list[0] is callable: value = list[0](*list[1:]) 
         - callable: value = callable()
            
    It also allows to pass a hook method to be called for every main method execution.
    
    Usage::
        wt = fandango.threads.WorkerThread(process=True)
        wt.start()
        wt.put('import fandango')
        wt.put("tc = fandango.device.TangoCommand('lab/15/vgct-01/sendcommand')")
        command = "tc.execute(feedback='status',args=['ver\r\\n'])"
        wt.put("tc.execute(feedback='status',args=['ver\r\\n'])")
        while not wt.getDone():
            wt.stopEvent.wait(1.)
            pile = dict(wt.flush())
        result = pile[command]
    """
    
    SINGLETON = None
    
    def __init__(self,name='',process=False,wait=.01,target=None,hook=None,trace=False):
        self._name = name
        self.wait = wait
        self._process = process
        self._trace = trace
        self.hook=hook
        self.THREAD_CLASS = threading.Thread if not process else multiprocessing.Process
        self.QUEUE_CLASS = Queue.Queue if not process else multiprocessing.Queue
        self.EVENT_CLASS = threading.Event if not process else multiprocessing.Event
        self.LOCK_CLASS = threading.RLock if not process else multiprocessing.RLock

        self.inQueue = self.QUEUE_CLASS()
        self.outQueue = self.QUEUE_CLASS()
        self.errorQueue = self.QUEUE_CLASS()
        self.stopEvent = self.EVENT_CLASS()
        if target is not None: 
            self.put(target)
        
        self._thread = self.THREAD_CLASS(name='Worker',target=self.run)
        self._thread.daemon = True
        pass
    def __del__(self):
        try: 
            self.stop()
            object.__del__(self)
        except: pass
        
    def put(self,target):
        """Inserting a new object in the Queue."""
        self.inQueue.put(target,False)
    def get(self):
        """Getting the oldest element in the output queue in (command,result) format"""
        try:
            self.getDone()
            try:
                while True: print self.errorQueue.get(False)
            except Queue.Empty: 
                pass
            return self.outQueue.get(False)
        except Queue.Empty: 
            #if self.outQueue.qsize():
                #print('FATAL PickleError, output queue has been lost')
                #self.outQueue = self.QUEUE_CLASS()
            return None
    def flush(self):
        """
        Getting all elements stored in the output queue in [(command,result)] format
        """
        result = []
        try:
            while True: result.append(self.outQueue.get(False))
        except Queue.Empty:
            pass
        return result
        
    def start(self):
        self._thread.start()
    def stop(self):
        self.stopEvent.set()
        self._thread.join()
    def isAlive(self):
        return self._thread.is_alive()
        
    def getQueue(self):
        return self.outQueue
    def getSize(self):
        return self.inQueue.qsize()
    def getDone(self):
        return not self.inQueue.qsize() and not self.outQueue.qsize()
    
    def process(self,target):
        """
        This method can be overriden in child classes to perform actions distinct from evalX
        """
        self.modules = getattr(self,'modules',{})
        self.instances = getattr(self,'instances',{})
        self._locals = getattr(self,'_locals',{})
        evalX(target,
            _locals=self._locals,modules=self.modules,instances=self.instances,
            _trace=self._trace,_exception=WorkerException)
        return evalX(*args,**kwargs)
        
    def run(self):
        print 'WorkerThread(%s) started!'%self._name
        logger = getattr(__builtin__,'print') if not self._process else (lambda s:(getattr(__builtin__,'print')(s),self.errorQueue.put(s)))
        while not self.stopEvent.is_set():
            try:
                target,value = self.inQueue.get(True,timeout=self.wait),None
                if self.stopEvent.is_set(): break
                if target is not None:
                    try:
                        model = target #To avoid original target to be overriden in process()
                        value = self.process(target)
                        try: pickle.dumps(value)
                        except pickle.PickleError: 
                            print traceback.format_exc()
                            raise WorkerException('UnpickableValue')
                        self.outQueue.put((model,value))
                    except Exception,e:
                        msg = 'Exception in WorkerThread(%s).run()\n%s'%(self._name,except2str())
                        print( msg)
                        self.outQueue.put((target,e))
                    finally:
                        if not self._process: self.inQueue.task_done()
                if self.hook is not None: 
                    try: 
                        self.hook()
                    except: 
                        print('Exception in WorkerThread(%s).hook()\n%s'%(self._name,except2str()))
            except Queue.Empty:
                pass
            except:
                print 'FATAL Exception in WorkerThread(%s).run()'%self._name
                print except2str()
        print 'WorkerThread(%s) finished!'%self._name
        
import objects

class SingletonWorker(WorkerThread,objects.Singleton):
    """
    Usage::
        # ... same like WorkerThread, but command is required to get the result value
        command = "tc.execute(feedback='status',args=['ver\r\\n'])"
        sw.put(command)
        sw.get(command)
    """
    def put(self,target):
        if not hasattr(self,'_queued'): self._queued = []
        self._queued.append(target)
        WorkerThread.put(self,target)
    def get(self,target):
        """
        It flushes the value stored for {target} task.
        The target argument is needed to avoid mixing up commands from different requestors.
        """
        if not hasattr(self,'_values'): self._values = {}
        self._values.update(self.flush())
        return self._values.pop(target)
    def flush(self):
        #It just flushes received values
        l = []
        l.extend(getattr(self,'_values',{}).items())
        l.extend(WorkerThread.flush(self))
        [self._queued.remove(v) for v in l if v in self._queued]
        return l
    def values(self):
        return self._values
    def done(self):
        return not bool(self._queued)

###############################################################################

class DataExpired(Exception): 
    def __str__(self):
        return 'DataExpired(%s)'%Exception.__str__(self)
    __repr__ = __str__

def getPickable(value):
    try: 
        pickle.dumps(value)
    except:# pickle.PickleError: 
        if isinstance(value,Exception):
            return Exception(str(value))
        else:
            value = str(value)
    return value

    
class ProcessedData(object):
    """ This struct stores named data with value,date associated and period,expire time constraints """
    def __init__(self,name,target=None,args=None,period=None,expire=None,callback=None):
        self.name = name
        self.target = target or name
        self.args = args
        self.period = period or 0
        self.expire = expire or 0
        self.callback = callback
        self.date = -1
        self.value = None
    def get_args(self):
        return (self.name,self.target,self.args,self.period,self.expire,None)
    def __repr__(self):
        return 'ProcessedData(%s)=(%s) at %s'%(str(self.get_args()),self.value,time2str(self.date))
    def __str__(self):
        return str(self.get_args())
    def set(self,value):
        self.date = time.time()
        self.value = value
    def get(self):
        result = self.value
        if self.date<=0: 
            raise DataExpired('%s s'%self.expire)
        else:
            now = time.time()
            expired = self.date+max((self.expire,self.period)) < now
            if self.expire>=0 and expired: #(self.expire==0 or self.date>0 and expired)):
                self.date = -1
                self.value = None
        return result
        
class WorkerProcess(Object,SingletonMap): #,Object,SingletonMap):
    """
    Class that provides a multiprocessing interface to process tasks in a background process and throw callbacks when finished.
    
    The queries are sent between sender/receiver thread and worker process using tuples.
    Queries may be: (key,) ; (key,target) ; (key,target,args)
     - key is just an identifier to internally store data results and callbacks
     - if target is a callable it will be thrown with args as argument (use [] if target is a void function)
     - if it isn't, then executor(target) will be called
     - executor can be fandango.evalX or other object/method assigned using WorkerProcess.bind(class,args)
    
    By default fandango.evalX is used to perform tasks, a different executor can be defined as WorkerProcess argument or calling:
      CP = WorkerProcess(targetClass(initArgs))
      CP.bind(targetClass,initArgs)
    
    Sending tasks to the process:
      CP.send(key='A1',target) 
      # Returns immediately and executes target() or executor(*target) in a background process
      CP.send('A1',target,args,callback=callback) 
      # Returns immediately, executes x=target(args) in background and launches callback(x) when ready
      
    When a (key,target,args) tuple is received the procedure is:
     * obtain the exec_ method (executor if args is None, 
     * obtain arguments (target if args is None, if args is map/sequence it is pre-parsed):
     * if args is None and there's a valid executor: return executor(target)
     
    How the executable method is obtained:
     - if args is None it tries to get a valid executor and target will be args.
     - if target is string first it tries to get executor.target
     - if failed, then it evals target (that may return an executable)
     - if args is not none and target is not string, target is used as executable if callable
    Return value:
     - if a valid executable method is found it returns exec_([*/**]args)
     - if not, it returns what has been found instead (evalX(target), executor.target or target)
    
    To use it like a threadDict, allowing a fixed list of keys to be permanently updated:
      CP.add(key,target,args,period,expire,callback)
      #This call will add a key to dictionary, which target(args) method will be executed every period, value obtained will expire after X seconds.
      #Optional Callback will be executed every time value is updated.
    
    Throwing commands in a sequential way (it will return when everything already in the queue is done):
      CP.command('comm') # Execute comm() and returns result
      CP.command('comm',args=(,)) # Execute comm(*args) and returns result
    
    Two different dictionaries will keep track of process results:
     - data : will store named data with and update period associated
     - callbacks : will store associated callbacks to throw-1 calls
    """
    
    ALIVE_PERIOD = 15
    __ALIVE,__ADDKEY,__REMOVEKEY,__BIND,__NULL = '__ALIVE','__ADDKEY','__REMOVEKEY','__BIND','__NULL'
    
    def __init__(self,target=None,start=True,timeout=0,timewait=0):
        """ 
        :param target: If not None, target will be an object which methods could be targetted by queries. 
        """
        import multiprocessing
        import threading
        from collections import defaultdict
        self.trace('__init__(%s)'%(target))
        self.timeout = timeout or self.ALIVE_PERIOD #Maximum time between requests, process will die if exceeded
        self.timewait = max((timewait,0.02)) #Time to wait between operations
        self.data = {} #It will contain a {key:ProcessedData} dictionary
        
        #Process Part
        self._pipe1,self._pipe2 = multiprocessing.Pipe()
        self._process_event,self._threading_event,self._command_event = multiprocessing.Event(),threading.Event(),threading.Event()
        self._process = multiprocessing.Process(
            target=self._run_process, #Callable for the process.main()
            args=[self._pipe2,self._process_event,target] #List of target method arguments
            )
        #Thread part
        self._receiver = threading.Thread(target=self._receive_data)
        self._process.daemon,self._receiver.daemon = True,True
        self.callbacks = defaultdict(list)
        if start: self.start()
        
    def __del__(self):
        self.stop()
        type(self).__base__.__del__(self)
    def trace(self,msg,level=0):
        print '%s, %s: %s'%(time2str(),type(self).__name__,str(msg))
        
    def bind(self,target,args=None):
        self.send(self.__BIND,target=target,args=args)
        
    #Thread Management
    def start(self):
        self._receiver.start(),self._process.start()
    def stop(self):
        self.trace('stop()')
        self._process_event.set(),self._threading_event.set()
        self._pipe1.close(),self._pipe2.close() 
    def isAlive(self):
        return self._process.is_alive() and self._receiver.is_alive()
    
    def keys(self): 
        return self.data.keys()
    def add(self,key,target=None,args=None,period=0,expire=0,callback=None):
        data = self.data[key] = ProcessedData(key,target=target,args=args,period=period,expire=expire,callback=callback)
        self.send(self.__ADDKEY,target=data.get_args())
    def get(self,key,default=__NULL,_raise=False):
        # Returns a key value (or default if defined)
        if key not in self.data and default!=self.__NULL: return default
        result = self.data[key].get()
        if _raise and isinstance(result,Exception): raise result
        return result
    def pop(self,key):
        # Returns a key value and removes from dictionary
        d = self.data.pop(key)
        self.send(self.__REMOVEKEY,key)
        return d
        
    def send(self,key,target,args=None,callback=None):
        """ 
        This method throws a new key,query,callback tuple to the process Pipe 
        Queries may be: (key,) ; (key,args=None) ; (key,command,args=None)
        """
        keywords = (self.__BIND,self.__ADDKEY,self.__ALIVE,self.__REMOVEKEY,None)
        if (key in keywords or key not in self.callbacks):
            #self.trace('send(%s,%s,%s,%s)'%(key,target,args,callback))
            if key not in keywords: self.callbacks[key] = [callback]
            if args is not None: self._pipe1.send((key,target,args))
            else: self._pipe1.send((key,target))
        elif callback not in self.callbacks[key]: 
            #self.trace('send(%s,%s,%s,%s) => %s'%(key,target,args,callback,self.callbacks[key]))
            self.callbacks[key].append(callback)
        return
    def command(self,command,args=None):
        """ This method performs a synchronous command (no callback, no persistence),
        it doesn't return until it is resolved """
        self._return = None
        self.send(key=str(command),target=command,args=args,callback=lambda q,e=self._command_event,s=self:(setattr(s,'_return',q),e.set()))
        while not self._command_event.is_set(): self._command_event.wait(self.timewait)
        self._command_event.clear()
        return self._return
    
    # Protected methods
    @staticmethod
    def get_hash(d):
        """This method just converts a dictionary into a hashable type""" 
        if isMapping(d): d = d.items()
        if isSequence(d): d = sorted(d)
        return str(d)
        
    @staticmethod
    def get_callable(key,executor=None):
        try:
            x = []
            if isinstance(key,basestring):
                trial(lambda:x.append(evalX(key)),lambda:x.append(None))
            return first(a for a in (
                key,
                x and x[0],
                isinstance(key,basestring) and getattr(executor,key,None), #key is a member of executor
                getattr(executor,'process',None), #executor is a process object
                executor, #executor is a callable
                #isinstance(key,basestring) and evalX(key), # key may be name of function
                ) if a and isCallable(a))
        except StopIteration,e:
            return None
        
    #@staticmethod
    def _run_process(self,pipe,event,executor=None):
        """ 
        Queries sent to Process can be executed in different ways:
         - Having a process(query) method given as argument.
         - Having an object with a key(query) method: returns (key,result)
         - If none of this, passing query to an evalX call.
         
        Executor will be a callable or an object with 'target' methods
        """
        last_alive,idle = time.time(),0 #Using NCycles count instead of raw time to avoid CPU influence
        scheduled = {} #It will be a {key:[data,period,last_read]} dictionary
        locals_,modules,instances = {'executor':executor},{},{}
        key = None
        self.trace('.Process(%s) started'%str(executor or ''))
        while not event.is_set() and (pipe.poll() or idle<(self.timeout/self.timewait)): #time.time()<(last_alive+self.timeout)):
            try:
                idle+=1
                now = time.time()
                if pipe.poll():
                    t = pipe.recv() #May be (key,) ; (key,args=None) ; (key,command,args)
                    key,target,args = [(None,None,None),(t[0],None,None),(t[0],t[1],None),t][len(t)]
                    if key!=self.__ALIVE: self.trace(shortstr('.Process: Received: %s => (%s,%s,%s)'%(str(t),key,target,args)))
                    last_alive,idle = time.time(),0 #Keep Alive Thread
                elif scheduled:
                    data = first(sorted((v.expire,v) for n,v in scheduled.items()))[-1]
                    if data.expire<=now: 
                        data.expire = now+data.period
                        key,target,args = data.name,data.target,data.args
                    else: #print '%s > %s - %s' % (time2str(now),time2str(next))
                        key = None
                if key == self.__ADDKEY: #(__ADDKEY,(args for ProcessedData(*)))
                    #Done here to evaluate not-periodic keys in the same turn that they are received
                    data = ProcessedData(*target)
                    if data.period>0: 
                        data.expire = now+data.period
                        scheduled[data.name]=data
                        self.trace('.Process: Added key: %s'%str(data))
                    else: 
                        if data.name in scheduled: 
                            self.trace('.Process: Removing %s key'%data.name)
                            scheduled.pop(data.name)
                    key,target,args = data.name,data.target,data.args #Added data will be immediately read
                if key is not None:
                    try:
                        if key == self.__REMOVEKEY: #(__REMOVEKEY,key)
                            if target in scheduled: scheduled.pop(target)
                            self.trace(scheduled)
                        elif key == self.__BIND:
                            # Setting a new executor object
                            if isCallable(target): executor = target
                            elif isinstance(target,basestring): executor = evalX(target,locals_,modules,instances)
                            else: executor = target
                            if isCallable(executor) and args is not None:
                                if isMapping(args): executor = executor(**args)
                                elif isSequence(args): executor = executor(*args)
                                else: executor = executor(args)
                            locals_['executor'] = executor
                            self.trace('.Process: Bound executor object to %s'%(executor))
                        elif key!=self.__ALIVE:
                            if args is None and executor is not None and (isCallable(executor) or getattr(executor,'process',None)):
                                # Target is a set of arguments to Executor object
                                exec_ = getattr(executor,'process',executor)
                                args = target
                            elif isinstance(target,basestring):
                                # Target is a member of executor or an string to be evaluated
                                # e.g. getattr(Reader,'get_attribute_values')(*(attr,start,stop))
                                if hasattr(executor,target): exec_ = getattr(executor,target)
                                else: exec_ = evalX(target,locals_,modules,instances) #Executor bypassed if both target and args are sent
                            else:
                                #Target is a value or callable
                                exec_ = target
                            
                            if isCallable(exec_): 
                                # Executing 
                                if key not in scheduled: 
                                    self.trace('.Process:  [%s] = %s(%s)(*%s)'%(key,exec_,target,args))
                                if args is None: value = exec_()
                                elif isDictionary(args): value = exec_(**args)
                                elif isSequence(args): value = exec_(*args)
                                else: value = exec_(args)
                            else: 
                                #target can be a an object member or eval(target) result
                                if key not in scheduled: 
                                    self.trace('.Process: [%s] = %s(*%s)'%(key,target,args))
                                value = exec_ 

                            pipe.send((key,getPickable(value)))
                    except Exception,e:
                        self.trace('.Process:\tError in %s process!\n%s'%(key,except2str(e)))
                        #print traceback.format_exc()
                        #print e
                        pipe.send((key,getPickable(e)))
            except Exception,e:
                self.trace('.Process:\tUnknown Error in process!\n%s'%traceback.format_exc())
            key = None
            event.wait(self.timewait)
        self.trace('.Process: exit_process: event=%s, thread not alive for %d s' % (event.is_set(),time.time()-last_alive))
                        
    def _receive_data(self):
        self.last_alive = 0
        while not self._threading_event.is_set():
            try:
                if self._pipe1.poll():
                    key,query = self._pipe1.recv()
                    if key not in self.data: 
                        self.trace('.Thread: received %s data; pending: %s'%(key,self.callbacks.keys()))
                        pass
                    if key in self.keys():
                        self.data[key].set(query)
                        if self.data[key].callback: 
                            try:
                                self.trace('.Thread:\tlaunching %s callback %s'%(key,callback))
                                self.data[key].callback(query)
                            except:
                                self.trace('.Thread:\tError in %s callback %s!'%(key,callback))
                                self.trace(except2str())
                    if key in self.callbacks:
                        for callback in self.callbacks[key]:
                            if callback is None: continue
                            try:
                                self.trace('.Thread:\tlaunching callback %s'%callback)
                                callback(query)
                            except:
                                self.trace('.Thread:\tError in %s callback %s!'%(key,callback))
                                self.trace(except2str())
                        self.callbacks.pop(key)
            except: self.trace('.Thread,Exception:%s'%traceback.format_exc())
            try:
                if time.time() > self.last_alive+3: 
                    self._pipe1.send((self.__ALIVE,None))
                    self.last_alive = time.time()
            except: self.trace('.Thread.is_alive(),Exception:%s'%traceback.format_exc())
            self._threading_event.wait(self.timewait)
        self.trace('.Thread: exit_data_thread')
        self.trace('<'*80)
        self.trace('<'*80)


###############################################################################

class Pool(object):
    """ 
    It creates a queue of tasks managed by a pool of threads.
    Each task can be a Callable or a Tuple containing args for the "action" class argument.
    If "action" is not defined the first element of the tuple can be a callable, and the rest will be arguments
    
    Usage:
        p = Pool()
        for item in source(): p.add_task(item)
        p.start()
        while len(self.pending()):
            time.sleep(1.)
        print 'finished!'
    """
    
    def __init__(self,action=None,max_threads=5,start=False,mp=False):   
        import threading
        if mp==True:
            import multiprocessing
            self._myThread = multiprocessing.Process
            self._myQueue = multiprocessing.Queue
        else:
            import Queue
            self._myThread = threading.Thread
            self._myQueue = Queue.Queue
        self._action = action
        self._max_threads = max_threads
        self._threads = []
        self._pending = []
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._locked = partial(locked,_lock=self._lock)
        self._started = start
        self._queue = self._myQueue()
        
    def start(self):
        """ 
        Start all threads.
        """
        [t.start() for t in self._threads]
        self._started = True
        
    def stop(self):
        self._stop.set()
        [t.join(3.) for t in self._threads]
        #while not self._queue.empty(): self._queue.get()
        self._retire()
        self._started = False
        
    def add_task(self,item):#,block=False,timeout=None):
        """
        Adds a new task to the queue
        :param task: a callable or a tuple with callable and arguments
        """
        self._locked(self._pending.append,str(item))
        if self._started: self._retire()
        if len(self._pending)>len(self._threads) and len(self._threads)<self._max_threads:
            self._new_worker()        
        self._queue.put(item)#,block,timeout)

    def pending(self):
        """ returns a list of strings with the actions not finished yet"""
        self._retire()
        return self._pending
        
    ####################################################################################
    #Protected methods
            
    def _new_worker(self):
        #Creates a new thread
        t = self._myThread(target=self._worker)
        self._locked(self._threads.append,t)
        t.daemon = True
        if self._started: t.start()      
        
    def _retire(self):
        #Cleans dead threads
        dead = [t for t in self._threads if not t.is_alive()]
        for t in dead:
            self._locked(self._threads.remove,t) 
    
    def _worker(self):
        #Processing queue items
        while not self._stop.is_set() and not self._queue.empty():
            item = self._queue.get()
            try:
                if item is not None and isCallable(item): 
                    item()
                elif isSequence(item): 
                    if self._action: self._action(*item)
                    elif isCallable(item[0]): item[0](*item[1:])
                elif self._action: 
                    self._action(item)
            except:
                import traceback
                print('objects.Pool.worker(%s) failed: %s'%(str(item),traceback.format_exc()))
            self._remove_task(item)
        return
                
        
    def _remove_task(self,item=None):
        #Remove a finished task from the list
        if str(item) in self._pending: 
            self._locked(self._pending.remove,str(item))
        return getattr(self._queue,'task_done',lambda:None)()
            
    pass
    
###############################################################################
    
class AsynchronousFunction(threading.Thread):
    '''This class executes a given function in a separate thread
    When finished it sets True to self.finished, a threading.Event object 
    Whether the function is thread-safe or not is something that must be managed in the caller side.
    If you want to autoexecute the method with arguments just call: 
    t = AsynchronousFunction(lambda:your_function(args),start=True)
    while True:
        if not t.isAlive(): 
            if t.exception: raise t.exception
            result = t.result
            break
        print 'waiting ...'
        threading.Event().wait(0.1)
    print 'result = ',result
    '''
    def __init__(self,function):
        """It just creates the function object, you must call function.start() afterwards"""
        self.function  = function
        self.result = None
        self.exception = None
        self.finished = threading.Event()
        self.finished.clear()
        threading.Thread.__init__(self)
        self.wait = self.finished.wait
        self.daemon = False
    def run(self):
        try:
            self.wait(0.01)
            self.result = self.function()
        except Exception,e:
            self.result = None            
            self.exception = e
        self.finished.set() #Not really needed, simply call AsynchronousFunction.isAlive() to know if it has finished
