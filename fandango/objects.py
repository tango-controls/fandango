#!/usr/bin/env python2.5
""" @if gnuheader
#############################################################################
##
## file :       objects.py
##
## description : see below
##
## project :     Tango Control System
##
## $Author: tcoutinho@cells.es, homs@esrf.fr $
##
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
@package object
@description It includes 2 wonderful classes: Object (by ahoms) and Singleton (by MarcSantiago)
@attention THIS MODULE IS DEPRECATED, Use @b tau.core.utils.Singleton and @b tau.core.utils.Object instead!
"""

from __builtin__ import object
from functional import *
from operator import isCallable
try: from collections import namedtuple #Only available since python 2.6
except: pass

## Useful class objects

class Struct(object):
    def __init__(self,dct = None):
        if dct is None: dct = {}
        elif isSequence(dct) and not isDictionary(dct): dct = dict.fromkeys(dct) #isDictionary also matches items lists
        [setattr(self,k,v) for k,v in (dct.items() if hasattr(dct,'items') else dct)]
    def __repr__(self):
        return 'fandango.Struct({\n'+'\n'.join("\t'%s': %s,"%(k,v) for k,v in self.__dict__.items())+'\n\t})'
    def __str__(self):
        return self.__repr__().replace('\n','').replace('\t','')
    pass
        
def Property(fget=None,fset=None,fdel=None,doc=None):
    """ It makes easier to declare name independent property's (descriptors) by using template methods like:
    
    def fget(self,var): # var is the identifier of the variable
        return getattr(self,var)    
    def fset(self,value,var): # var is the identifier of the variable
        setattr(self,var,value)
    def fdel(self,var): # var is the identifier of the variable
        delattr(self,var)    
        
    MyObject.X = Property(fget,fset,fdel,'X')        
    """
    return property(partial(fget,var=doc) if fget else None,partial(fset,var=doc) if fset else None,partial(fdel,var=doc) if fdel else None,doc=doc)
    
import threading
__lock__ = threading.RLock()
def locked(f,*args,**kwargs):
    """ 
    decorator for secure-locked functions 
    A key-argument _lock can be used to use a custom Lock object
    """
    _lock = kwargs.pop('_lock',__lock__)
    try:
        _lock.acquire()
        return f(*args,**kwargs)
    except Exception,e:
        print 'Exception in%s(*%s,**%s): %s' % (f.__name__,args,kwargs,e)
    finally:
        _lock.release()
            
def self_locked(func,reentrant=True):
    ''' Decorator to make thread-safe class members
    @deprecated
    @note see in tau.core.utils.containers
    Decorator to create thread-safe objects.
    reentrant: CRITICAL:
        With Lock() this decorator should not be used to decorate nested functions; it will cause Deadlock!
        With RLock this problem is avoided ... but you should rely more on python threading.
    '''
    def lock_fun(self,*args,**kwargs):
        if not hasattr(self,'lock'):
            setattr(self,'lock',threading.RLock() if reentrant else threading.Lock())
        if not hasattr(self,'trace'):
            setattr(self,'trace',False)
        self.lock.acquire()
        try: 
            #if self.trace: print "locked: %s"%self.lock
            result = func(self,*args,**kwargs)
        finally: 
            self.lock.release()
            #if self.trace: print "released: %s"%self.lock
        return result       
    return lock_fun

import Queue
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
        while not self._stop.isSet() and not self._queue.empty():
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
    

class Singleton(object):
    """This class allows Singleton objects overriding __new__ and renaming __init__ to init_single
    The __new__ method is overriden to force Singleton behaviour, the Singleton is created for the lowest subClass.
    @warning although __new__ is overriden __init__ is still being called for each instance=Singleton()
    """   
    ## Singleton object
    __instance = None     # the one, true Singleton, private members cannot be read directly
    __dumb_init = (lambda self,*p,**k:None)
    
    def __new__(cls, *p, **k):
        if cls != type(cls.__instance):
            __instance = object.__new__(cls)
            #srubio: added init_single check to prevent redundant __init__ calls
            if hasattr(cls,'__init__') and cls.__init__ != cls.__dumb_init:
                setattr(cls,'init_single',cls.__init__)
                setattr(cls,'__init__',cls.__dumb_init)  #Needed to avoid parent __init__ methods to be called
            if hasattr(cls,'init_single'): 
                cls.init_single(__instance,*p,**k) #If no __init__ or init_single has been defined it may trigger an object.__init__ warning!
            cls.__instance = __instance #Done at the end to prevent failed __init__ to create singletons
        return cls.__instance
    
    @classmethod
    def get_singleton(cls,*p,**k):
        return cls.__instance or cls(*p,**k)

class SingletonMap(object):
    """This class allows distinct Singleton objects for each args combination.
    The __new__ method is overriden to force Singleton behaviour, the Singleton is created for the lowest subClass.
    @warning although __new__ is overriden __init__ is still being called for each instance=Singleton()
    """
    
    ## Singleton object
    __instances = {} # the one, true Singleton, private members cannot be read directly
    __dumb_init = (lambda self,*p,**k:None)    
    
    def __new__(cls, *p, **k):
        key = cls.parse_instance_key(*p,**k)
        if cls != type(cls.__instances.get(key)):
            __instance = object.__new__(cls)
            __instance.__instance_key = key
            #srubio: added init_single check to prevent redundant __init__ calls
            if hasattr(cls,'__init__') and cls.__init__ != cls.__dumb_init:
                setattr(cls,'init_single',cls.__init__)
                setattr(cls,'__init__',cls.__dumb_init) #Needed to avoid parent __init__ methods to be called
            if hasattr(cls,'init_single'): 
                cls.init_single(__instance,*p,**k) #If no __init__ or init_single has been defined it may trigger an object.__init__ warning!
            cls.__instances[key] = __instance
        return cls.__instances[key]
            
    @classmethod
    def get_singleton(cls,*p,**k):
        key = cls.parse_instance_key(*p,**k)
        return cls.__instances.get(key,cls(*p,**k))
    
    @classmethod
    def get_singletons(cls):
        return cls.__instances       
      
    @classmethod
    def parse_instance_key(cls,*p,**k):
        return '%s(*%s,**%s)' % (cls.__name__,list(p),list(sorted(k.items())))
    
    def get_instance_key(self):
        return self.__instance_key
   

class Object(object):
    """
    This class solves some problems when an object inherits from multiple classes
    and some of them inherit from the same 'grandparent' class
    """ 

    def __init__(self):
        """ default initializer 
        @todo be more clever!
        """

        self.name = None
        
        pass
        ## @var name
        # Var does nothing    
        # @todo be more clever!
        
        pass
        
    def call__init__(self, klass, *args, **kw):
        if 'inited_class_list' not in self.__dict__:
            self.inited_class_list = []

        if klass not in self.inited_class_list:
            self.inited_class_list.append(klass)
            #print '%s.call__init__(%s,%s)' % (klass.__name__,args,kw)
            klass.__init__(self, *args, **kw)
            
    def call_all__init__(self, klass, *_args, **_kw):
        ''' Call __init__ recursively, for multiple dynamic inheritance.
        @author srubio@cells.es
        
        This method should be called only if all arguments are keywords!!!
        Multiple __init__ calls with unnamed arguments is hard to manage: 
            All the _args values will be assigned to non-keyword args
        e.g:
            from objects import Object
            
            class A(Object):
                def __init__(self,a=2):
                    print 'A.__init__',a
            class B(A):
                def __init__(self,b):
                    print 'B.__init__',b
            class C(B,A):
                def __init__(self,c):
                    print 'C.__init__',c
            class D(C,B):
                def __init__(self,d=1,*args,**kwargs):
                    self.call_all__init__(D,*args,**kwargs)
                    print 'D.__init__',d
            D(a=1,b=2,c=3,d=4)
        '''
        #if _args: raise Exception,'__init_all_Object_withUnnamedArgumentsException'
        from inspect import getargspec
        #print '%s.call_all__init__(%s,%s)' % (klass.__name__,_args,_kw)
        for base in klass.__bases__:
            if 'call__init__' in dir(base) and ('inited_class_list' not in self.__dict__ or base not in self.inited_class_list):
                #print '\t%s.base is %s' % (klass.__name__,base.__name__)
                nkw,i = {},0
                try:
                    args,largs,kargs,vals = getargspec(base.__init__)
                    if kargs: nkw = dict(_kw)
                    for arg in args:
                        if arg == 'self': continue
                        if arg in _kw: 
                            nkw[arg] = _kw[arg]
                        elif i<len(_args): 
                            nkw[arg], i = _args[i], i+1
                    self.call_all__init__(base,*_args,**_kw)
                    self.call__init__(base,**nkw)
                except Exception,e:
                    print 'Unable to execute %s.__init__!: %s' % (base.__name__,str(e))
        return
            
    def getAttrDict(self):
        attr = dict(self.__dict__)
        if 'inited_class_list' in attr:
            del attr['inited_class_list']
        return attr
        
    def updateAttrDict(self, other):
        attr = other.getAttrDict()
        self.__dict__.update(attr)
        

