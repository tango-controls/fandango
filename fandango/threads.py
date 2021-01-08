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
import time,threading,multiprocessing,traceback
import imp,__builtin__,pickle,re
from threading import Event,Lock,RLock,Thread

from log import except2str,shortstr,tracer
from functional import *
from excepts import trial,Catched,CatchedArgs
from operator import isCallable
from objects import Queue, Singleton, Object, SingletonMap


###############################################################################

_EVENT = threading.Event()

def wait(seconds,event=True,hook=None):
    """
    :param seconds: seconds to wait for
    :param event: if True (default) it uses a dummy Event, 
        if False it uses time.sleep,
        if Event is passed then it calls event.wait(seconds)
    :param hook: a callable to be executed before the wait
    """
    r = 0
    try:
      if hook and isCallable(hook):
          Catched(hook)()
      r+=1
      if not event:
          time.sleep(seconds)
      elif hasattr(event,'wait'):
        try:
          event.wait(seconds)
        except Exception,e:
          raise e
      else:
          _EVENT and _EVENT.wait(seconds)
      r+=2
    except Exception,e:
      ## This method triggers unexpected exceptions on ipython exit
      print('wait.hook failed!: %s,%s,%s,%s'%(event,event.wait,r,e))
      if time: time.sleep(seconds)
        
def timed_range(seconds,period,event=None):
    """
    Method used to execute the content of a for loop at periodic intervals.
    For X seconds, this method will return each period fragment.
    event can be used to pass a threading.Event to abort the loop if needed.

    Usage:
    
      for t in trange(15,0.1): 
        method_executed_at_10Hz_for_15s()
    """
    t0 = time.time()
    diff = 0
    e = event or threading.Event()
    while diff<seconds and not e.is_set():
      e.wait(period)
      diff = time.time()-t0
      if not e.is_set:
        yield diff
    
class FakeLock(object):
    """ Just for debugging, can replace a Lock when debugging a deadLock issue. """
    def acquire(self):pass
    def release(self):pass

###############################################################################

class ThreadedObject(Object):
  """
  An Object with a thread pool that provides safe stop on exit.
  
  It has a permanent thread running, that it's just paused 
  
  Created to allow safe thread usage in Tango Device Servers
  
  WARNING DO NOT CALL start()/stop() methods inside target or any hook,
  it may provoke unexpected behaviors.
  
  Some arguments:
  
  :target: function to be called
  :period=1: iteration frequency
  :nthreads=1: size of thread pool
  :min_wait=1e-5:  max frequency allowed
  :first=0: first iteration to start execution
  :start=False: start processing at object creation
  
  Statistics and execution hooks are provided:
  
  :start_hook: launched after an start() command, 
   may return args,kwargs for the target() method
  :loop_hook: like start_hook, but called at each iteration
  :stop_hook: called after an stop() call
  :wait_hook: called before each wait()
  """
  
  INSTANCES = []
  
  def __init__(self,target=None,period=1.,nthreads=1,start=False,min_wait=1e-5,first=0):

    self._event = threading.Event()
    self._stop = threading.Event()
    self._done = threading.Event()
    self._kill = threading.Event()
    self._started = 0
    self._min_wait = 1e-5
    self._first = first
    self._count = -1
    self._errors = 0
    self._delay = 0
    self._acc_delay = 0
    self._usage = 1.
    self._next = time.time()+period
    self._last = 0
    self._queue = []
    self._start_hook = self.start_hook
    self._loop_hook = self.loop_hook
    self._stop_hook = self.stop_hook
    self._wait_hook = None
    self._last_exc = ''
    
    self._threads = []
    if nthreads>1:
      print('Warning: ThreadedObject.nthreads>1 Not Implemented Yet!')
    for i in range(nthreads):
      self._threads.append(threading.Thread(target=self.loop))
      self._threads[i].daemon = True

    self.set_period(period)
    self.set_target(target)
    self.stop(wait=False)
    if start:
      #Not starting threads, just reset flags
      self.start()
    
    for t in self._threads: 
      t.start()
      
    ThreadedObject.INSTANCES.append(self)
      
  def __del__(self):
    self.kill()
    
  @classmethod
  def __test__(klass):
      """ returns True if performs 2 successful cycles """
      to = klass(period=.1)
      to.set_target(
        lambda o=to:setattr(o,'SUCCESS',
          not getattr(o,'SUCCESS',True)))
      to.start()
      wait(2*to.get_period())
      try: v = to.SUCCESS
      except: v = False
      to.stop()
      return v  
  ## HELPERS
    
  def get_count(self): return self._count
  def get_errors(self): return self._errors
  def get_delay(self): return self._delay
  def get_acc_delay(self): return self._acc_delay
  def get_avg_delay(self): return self._acc_delay/(self._count or 1)
  def get_usage(self): return self._usage
  def get_next(self): return self._next
  def get_last(self): return self._last
  def get_started(self): return self._started
      
  def get_thread(self,i=0): return self._threads[i]
  def get_nthreads(self): return len(self._threads)
  def is_alive(self,i=0): return self.get_thread(i).is_alive()
    
  def set_period(self,period): self._timewait = period
  def get_period(self): return self._timewait  
  def set_target(self,target): self._target = target
  def get_target(self): return self._target

  def set_start_hook(self,target): self._start_hook = target
  def set_loop_hook(self,target): self._loop_hook = target
  def set_stop_hook(self,target): self._stop_hook = target
  def set_wait_hook(self,target): self._wait_hook = target
  
  def print_exc(self,e='',msg=''):
    if not e and traceback: 
      e = traceback.format_exc()
    self._last_exc = str(e)
    print(msg+':'+self._last_exc)
  
  def set_queue(self,queue): 
    """
    A list of timestamps can be passed to the main loop to force
    a faster or slower processing.
    This list will override the current periodic execution,
    target() will be executed at each queued time instead.
    """
    self._queue = queue
  
  ## MAIN METHODS
    
  def start(self):
    # If already started, it forces the next cycle
    if self._started: 
      self.stop()
    else: #abort stop wait
      self._event.clear()
    self._done.clear()
    self._stop.clear()
    
  def stop(self,wait=3.):
    self._event.set()
    self._stop.set()
    if not wait: wait = .1e-5
    self._done.wait(wait)
    self._done.clear()
    self._event.clear()
    
  @staticmethod
  def stop_all():
    for i in ThreadedObject.INSTANCES:
        try: i.stop()
        except: pass
      
  def kill(self,wait=3.):
    self._kill.set()
    self.stop(wait)
    
  @staticmethod
  def kill_all():
    for i in ThreadedObject.INSTANCES:
        try: i.kill()
        except: pass    
      
  def start_hook(self,*args,**kwargs):
    """ redefine at convenience, it will return the arguments for target method """
    return [],{}
    print('Starting push_loop(%s)'%self._timewait)
    print('Sending %d events in bunches of %d every %f seconds'%(
      self.MaxEvents,self.ConsecutiveEvents,self._timewait))
    
    t0,t1,ts,self.send_buffer = time.time(),0,0,[]
    tnext = t0 + self._timewait  
    
  def loop_hook(self,*args,**kwargs):
    """ redefine at convenience, it will return the arguments for target method """
    return [],{}
  
  def stop_hook(self,*args,**kwargs):
    """ redefine at convenience """
    pass  
  
  def clean_stats(self):
    self._count = 0
    self._errors = 0
    self._delay = 0
    self._acc_delay = 0
    self._last  = 0
    
  def loop(self):
    try:
        self._done.set() #Will not be cleared until stop/start() are called

        while not self._kill.isSet():

            while self._stop.isSet():
                wait(self._timewait,self._event,self._wait_hook)
                
            self._done.clear()
            self.clean_stats()

            ts = time.time()
            ## Evaluate target() arguments
            try:
                args,kwargs = self._start_hook(ts)
            except:
                if self._errors < 10:
                    self.print_exc()
                self._errors += 1
                args,kwargs = [],{}
            
            tracer('ThreadedObject(%s).Start() ...'%type(self))
            self._started = time.time()
            self._next = self._started + self._timewait
            while not self._stop.isSet():
              try:
                self._event.clear()
                
                ## Task Execution
                if count>=self._first:
                  try:
                      if self._target:
                          self._target(*args,**kwargs)
                  except:
                      if self._errors < 10:
                          self.print_exc()
                      self._errors += 1

                ## Obtain next scheduled execution
                t1,tn = time.time(),ts+self._timewait
                if self._queue:
                    while self._queue and self._queue[0]<self._next:
                        self._queue.pop(0)
                    if self._queue:
                        tn = self._queue[0]
                
                ## Wait and Calcullate statistics
                self._next = tn
                tw = self._next-t1
                self._usage = (t1-ts)/self._timewait
                #self.debug('waiting %s'%tw)
                wait(max((tw,self._min_wait)),self._event,self._wait_hook)
                ts = self._last = time.time()
                self._delay = ts>self._next and ts-self._next or 0
                self._acc_delay = self._acc_delay + self._delay
                
                ## Execute Loop Hook to reevaluate target Arguments
                if count>=self._first:
                    try:
                      args,kwargs = self._loop_hook(ts)
                    except:
                      if self._errors < 10:
                          self.print_exc()
                      self._errors += 1
                      args,kwargs = [],{}
                
                self._count += 1
                
              except Exception,e:
                self.print_exc(traceback and traceback.format_exc(),
                               'ThreadObject stop!')
                raise e
                
            print('ThreadedObject.Stop(...)')
            self._started = 0
            self._done.set() #Will not be cleared until stop/start() are called
            Catched(self._stop_hook)()
    
        print('ThreadedObject.Kill() ...')
        return #<< Should never get to this point
    except Exception,e:
        self.print_exc(time and e,'ThreadObject exit!')

###############################################################################

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
    Allows to schedule tasks in a background thread or process
    
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
       
    def locals(self,key=None):
        return self._locals if key is None else self._locals.get(key)
        
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
        return evalX(target,
            _locals=self._locals,modules=self.modules,instances=self.instances,
            _trace=self._trace,_exception=WorkerException)
        
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
        self._queued.append(target) #<< saving a timestamp would be useful here
        WorkerThread.put(self,target)
    def get(self,target):
        """
        It flushes the value stored for {target} task.
        The target argument is needed to avoid mixing up commands from different requestors.
        """
        if not hasattr(self,'_values'): self._values = {}
        self._values.update(self.flush())
        ## @OJO: If update values fails, all received values will be lost!?!
        ## it seems that this should be done here instead of using flush(): self._queued.pop(target)
        return self._values.pop(target)
    def flush(self):
        #It just flushes all received values
        l = []
        l.extend(getattr(self,'_values',{}).items())
        l.extend(WorkerThread.flush(self))
        # Removing already finished commands from entry queue
        [self._queued.remove(v[0]) for v in l if v[0] in self._queued]
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
    
    See full description and usage in doc/recipes/Threading.rst
    """
    
    ALIVE_PERIOD = 15
    __ALIVE,__ADDKEY,__REMOVEKEY,__BIND,__NULL,__PAUSE = '__ALIVE','__ADDKEY','__REMOVEKEY','__BIND','__NULL','__PAUSE'
    
    def __init__(self,target=None,start=True,timeout=0,timewait=0):
        """ 
        :param target: If not None, target will be an object which methods could be targetted by queries. 
        """
        import multiprocessing
        import threading
        from collections import defaultdict
        self.trace('__init__(%s)'%(target))
        self.timeout = timeout or self.ALIVE_PERIOD #Maximum time between requests, process will die if exceeded
        self.paused = 0
        self.timewait = max((timewait,0.02)) #Time to wait between operations
        self.data = {} #It will contain a {key:ProcessedData} dictionary
        self.last_alive = 0
        
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
        #Launches the process and threads
        self._receiver.start(),self._process.start()
    def stop(self):
        #This method stops all threads
        self.trace('stop()')
        self._process_event.set(),self._threading_event.set()
        self._pipe1.close(),self._pipe2.close() 
        
    def isAlive(self):
        return self._process.is_alive() and self._receiver.is_alive()
    
    def keys(self): 
        return self.data.keys()
    def add(self,key,target=None,args=None,period=0,expire=0,callback=None):
        # Adds a command to be periodically executed
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
    
    def pause(self,timeout):
        # Stops for a while the execution of scheduled keys
        self.paused = time.time()+timeout
        self.send(self.__PAUSE,target=self.paused)
        
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
        This is the main loop of the background Process.
        
        Queries sent to Process can be executed in different ways:
         - Having a process(query) method given as argument.
         - Having an object with a key(query) method: returns (key,result)
         - If none of this, passing query to an evalX call.
         
        Executor will be a callable or an object with 'target' methods
        """
        last_alive,idle = time.time(),0 #Using NCycles count instead of raw time to avoid CPU influence
        key,paused = None,0
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
                elif scheduled and time.time()>paused:
                    data = first(sorted((v.date+v.period,v) for n,v in scheduled.items()))[-1]
                    if key not in scheduled and key is not None:
                        self.trace('Nothing in queue, checking scheduled tasks ...')
                    if (data.date+data.period)<=now: 
                        data.date = now
                        key,target,args = data.name,data.target,data.args
                    else: #print '%s > %s - %s' % (time2str(now),time2str(next))
                        key = None
                        
                if key == self.__PAUSE:
                    # should delay scheduled commands but not freeze those synchronous (like ADDKEY or COMMAND)
                    paused = target
                    self.trace('.Process: Scheduled keys will be paused %s seconds.'%(paused-time.time()))
                elif key == self.__ADDKEY: #(__ADDKEY,(args for ProcessedData(*)))
                    #Done here to evaluate not-periodic keys in the same turn that they are received
                    data = ProcessedData(*target)
                    if data.period>0: 
                        scheduled[data.name]=data
                        self.trace('.Process: Added key: %s'%str(data))
                    else: 
                        if data.name in scheduled: 
                            self.trace('.Process: Removing %s key'%data.name)
                            scheduled.pop(data.name)
                    if time.time()>paused:
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
                                    self.trace(shortstr('.Process:  [%s] = %s(%s)(*%s)'%(key,exec_,target,args)))
                                if args is None: value = exec_()
                                elif isDictionary(args): value = exec_(**args)
                                elif isSequence(args): value = exec_(*args)
                                else: value = exec_(args)
                            else: 
                                #target can be a an object member or eval(target) result
                                if key not in scheduled: 
                                    self.trace(shortstr('.Process: [%s] = %s(*%s)'%(key,target,args)))
                                value = exec_ 

                            pipe.send((key,getPickable(value)))
                    except Exception,e:
                        self.trace('.Process:\tError in %s process!\n%s\n%s\n%s'%(key,target,args,except2str(e)))
                        #print traceback.format_exc()
                        #print e
                        pipe.send((key,getPickable(e)))
            
            except Exception,e:
                self.trace('.Process:\tUnknown Error in process!\n%s'%traceback.format_exc())
            key = None
            event.wait(self.timewait)
        
        print '!'*80
        self.trace('.Process: exit_process: event=%s, thread not alive for %d s' % (event.is_set(),time.time()-last_alive))
                        
    def _receive_data(self):
        """
        Main loop of the thread receiving data from the background Process (and launching callbacks when needed)
        """
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
        print '!'*80
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
            try:
                import Queue
            except:
                import queue as Queue
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

"""
SubprocessMethod and AsynchronousFunction provide an API to execute tasks
in background processes
"""

def SubprocessMethod(obj,*args,**kwargs):
    """
    arguments (this will be extracted from kwargs): 
        object : object to extract method or callable
        method :  string or callable to get from object
        timeout : seconds 
        callback : optional method to be called
    
    Method for executing reader.get_attribute_values in background 
    with a timeout (30 s by default)

    In fact, it allows to call any object method passed by name; 
    or just pass a callable as object.

    This method could be embedded in a thread with very high timeout 
    to trigger a callback when data is received.

    This advanced behavior can be implemented using AsynchronousFunction
    
    example:
    reader,att = PyTangoArchiving.Reader(),'just/some/nice/attribute'
    dates = '2014-06-23 00:00','2014-06-30 00:00'
    values = fandango.threads.SubprocessMethod(reader,'get_attribute_values',
        att,*dates,timeout=10.)
    
    or 
    
    def callback(v): 
        print('>> received %d values'%len(v))
        
    fandango.threads.SubprocessMethod(reader,
        'get_attribute_values',att,*dates,
        timeout=10.,callback=callback)
    
    >> received 414131 values
    """
    method = kwargs.pop('method',None)
    timeout = kwargs.pop('timeout',30.)
    callback = kwargs.pop('callback',None)
    
    #Using pipe because it's faster than queue and more efficient
    local,remote = multiprocessing.Pipe(False)
    
    def do_it(o,m,conn,*a,**k):
        try:
            if None in (o,m): 
                m = (o or m)
            elif isString(m): 
                m = getattr(o,m)
            #print m,a,k
            conn.send(m(*a,**k))
            #conn.close()
        except Exception as e:
            traceback.print_exc()
            conn.send(e)
        
    args = (obj,method,remote)+args
    proc = multiprocessing.Process(target=do_it,args=args,kwargs=kwargs)
    #print('New Process(%s)' % str(do_it))
    proc.daemon = True
    proc.start()
    t0 = time.time()
    result = None
    
    while time.time()<t0+timeout:
        if local.poll():
            result = local.recv()
            break
        wait(.1)
        
    local.close(),remote.close() #close pipes
    print('Join Process(%s)' % str(do_it))
    proc.terminate(),proc.join() #close process

    if time.time()>t0+timeout:
        result = Exception('TimeOut(%s,%s)!'%(str(obj),timeout))
    if callback:
        callback(result)
    elif isinstance(result,Exception):
        raise result

    return result
    
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
    def __init__(self, function, args = None, kwargs = None, 
                callback=None, pause=0.0, start=False,
                ):
        """
        It just creates the function object.
        If pause!=0 or start=True, the function will be called
        """
        self.function  = function
        self.result = None
        self.exception = None
        self.finished = threading.Event()
        self.finished.clear()
        threading.Thread.__init__(self)
        self.callback = callback
        self.pause = pause
        self.wait = self.finished.wait
        self.daemon = False
        self.args = args or []
        self.kwargs = kwargs or {}
        if self.pause or start:
            self.start()
        
    def run(self):
        try:
            if self.pause:
                self.wait(self.pause)
            self.result = self.function(*self.args, **self.kwargs)
        except Exception,e:
            self.result = None            
            self.exception = e
        # Not really needed, simply call AsynchronousFunction.isAlive() 
        # to know if it has finished
        self.finished.set() 
        if self.callback:
            try:
                self._bg = AsynchronousFunction(self.callback, start=True,
                    args = [self.result] if self.result is not None else [])
            except:
                traceback.print_exc()

from . import doc
__doc__ = doc.get_fn_autodoc(__name__,vars())

