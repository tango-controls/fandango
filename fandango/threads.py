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
import Queue,threading,multiprocessing,traceback
import imp,__builtin__,pickle

from . import functional
from functional import *
from operator import isCallable
from objects import Singleton

try: from collections import namedtuple #Only available since python 2.6
except: pass

###############################################################################
WorkerException = type('WorkerException',(Exception,),{})

class WorkerThread(object):
    """
    This class allows to schedule tasks in a background thread or process
    """
    
    def __init__(self,name='',process=False,wait=.01,target=None,trace=False):
        self._name = name
        self.wait = wait
        self._process = process
        self._done = 0
        self._trace = trace
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
        self.inQueue.put(target,False)
    def get(self):
        try:
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
        if not self._done: return 0.
        qs = self.inQueue.qsize()
        return self._done/(self._done+qs) if qs else 1.
        
    def run(self):
        print 'WorkerThread(%s) started!'%self._name
        modules = {}
        instances = {}
        _locals = {}
        logger = getattr(__builtin__,'print') if not self._process else (lambda s:(getattr(__builtin__,'print')(s),self.errorQueue.put(s)))
        def get_module(_module):
            if module not in modules: 
                modules[module] = imp.load_module(*([module]+list(imp.find_module(module))))
            return modules[module]
        def get_instance(_module,_klass,_klass_args):
            if (_module,_klass,_klass_args) not in instances:
                instances[(_module,_klass,_klass_args)] = getattr(get_module(module),klass)(*klass_args)
            return instances[(_module,_klass,_klass_args)]
                
        while not self.stopEvent.is_set():
            try:
                target = self.inQueue.get(True,timeout=self.wait)
                if self.stopEvent.is_set(): break
                if target is None: continue
                try:
                    result = None
                    #f,args = objects.parseMappedFunction(target)
                    #if not f: raise WorkerException('targetMustBeCallable')
                    #else: self.outQueue.put(f())
                    if isDictionary(target):
                        model = target
                        keywords = ['__args__','__target__','__class__','__module__','__class_args__']
                        args = model['__args__'] if '__args__' in model else dict((k,v) for k,v in model.items() if k not in keywords)
                        target = model.get('__target__',None)
                        module = model.get('__module__',None)
                        klass = model.get('__class__',None)
                        klass_args = model.get('__class_args__',tuple())
                        if isCallable(target): 
                            target = model['__target__']
                        elif isString(target):
                            if module:
                                #module,subs = module.split('.',1)
                                if klass: 
                                    if self._trace: print('WorkerThread(%s) executing %s.%s(%s).%s(%s)'%(self._name,module,klass,klass_args,target,args))
                                    target = getattr(get_instance(module,klass,klass_args),target)
                                else:
                                    if self._trace: print('WorkerThread(%s) executing %s.%s(%s)'%(self._name,module,target,args))
                                    target = getattr(get_module(module),target)
                            elif klass and klass in dir(__builtin__):
                                if self._trace: print('WorkerThread(%s) executing %s(%s).%s(%s)'%(self._name,klass,klass_args,target,args))
                                instance = getattr(__builtin__,klass)(*klass_args)
                                target = getattr(instance,target)
                            elif target in dir(__builtin__): 
                                if self._trace: print('WorkerThread(%s) executing %s(%s)'%(self._name,target,args))
                                target = getattr(__builtin__,target)
                            else:
                                raise WorkerException('%s()_MethodNotFound'%target)
                        else:
                            raise WorkerException('%s()_NotCallable'%target)
                        value = target(**args) if isDictionary(args) else target(*args)
                        if self._trace: print('%s: %s'%(model,value))
                        self.outQueue.put((model,value))
                    else:
                        if isIterable(target) and isCallable(target[0]):
                            value = target[0](*target[1:])
                        elif isCallable(target):
                            value = target()
                        if isString(target):
                            if self._trace: print('eval(%s)'%target)
                            if target.startswith('import '): 
                                module = target.replace('import ','')
                                get_module(module)
                                value = module
                            elif '=' in target and '='!=target.split('=',1)[1][0]:
                                var = target.split('=',1)[0].strip()
                                _locals[var]=eval(target.split('=',1)[1].strip(),modules,_locals)
                                value = var
                            else:
                                value = eval(target,modules,_locals)
                                #try: 
                                    #pickle.dumps(value)
                                #except: 
                                    #print traceback.format_exc()
                                    #raise WorkerException('unpickableValue')
                        else:
                            raise WorkerException('targetMustBeCallable')
                        if self._trace: print('%s: %s'%(target,value))
                        try: pickle.dumps(value)
                        except pickle.PickleError: 
                            print traceback.format_exc()
                            raise WorkerException('UnpickableValue')
                        self.outQueue.put((target,value))
                except:
                    msg = 'Exception in WorkerThread(%s).run()\n%s'%(self._name,traceback.format_exc())
                    print( msg)
                finally:
                    if not self._process: self.inQueue.task_done()
                    self._done+=1
            except Queue.Empty:
                pass
            except:
                print 'FATAL Exception in WorkerThread(%s).run()'%self._name
                print traceback.format_exc()
        print 'WorkerThread(%s) finished!'%self._name
        

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