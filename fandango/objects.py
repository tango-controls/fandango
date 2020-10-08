#!/usr/bin/env python2.5

#############################################################################
##
## file :       objects.py
##
## description : see below
##
## project :     Tango Control System
##
## $Author: srubio@cells.es, tcoutinho@cells.es, homs@esrf.fr $
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

"""
fandango.objects contains method for loading python modules and objects 
"on the run", as well as several advanced types used within fandango library

Struct, Decorator and Cached are fundamental types for all fandango API's

It includes 2 wonderful classes: Object (by Alejandro Homs) 
and Singleton (by Marc Santiago)

Enum classes are borrowed from taurus.core.utils (by Tiago Coutinho)

"""
from __future__ import print_function
try:
  from future import standard_library
  standard_library.install_aliases()
  from builtins import map
  from builtins import str
  from past.builtins import basestring
  from builtins import object
  import builtins
  from builtins import object
except: 
  pass

import traceback
from fandango.functional import *
from operator import isCallable, isSequenceType
from collections import Hashable
from types import MethodType
import threading
import functools

#Python 2-3 conundrum
try:
    import Queue
    import Queue as queue
except:
    import queue
    import queue as Queue

try: 
    from collections import namedtuple #Only available since python 2.6
except: 
    namedtuple = None

## Inspection methods

def dirModule(module):
    return [a for a,v in list(module.__dict__.items()) 
        if getattr(v,'__module__','') == module.__name__]

def findModule(module):
    from imp import find_module
    if '.' not in module:
        return find_module(module)[1]
    else:
        parent,child = module.rsplit('.', 1)
        #mparent = loadModule(parent)
        pparent = findModule(parent)
        pchild = find_module(child, [pparent])[1]
        return pchild

def loadModule(module,modulename=None):
    #Loads a python module either from source file or from module
    import imp
    if modulename or '/' in module or '.py' in module:
        if not modulename:
            modulename = module.split('/')[-1].split('.py')[0]
            modulename = replaceCl('[-\.]', '_', modulename)
            
        return imp.load_source(modulename, module)
    
    elif '.' not in module:
        return imp.load_module(module, *imp.find_module(module))
   
    else:
        parent,child = module.rsplit('.', 1)
        mparent = loadModule(parent)
        args = imp.find_module(child, mparent.__path__)
        mchild = imp.load_module(module, *args)
        return mchild

def dirClasses(module,owned=False):
    v = [a for a,v in list(module.__dict__.items()) if isinstance(v,type)]
    if owned: return [a for a in dirModule(module) if a in v]
    else: return v
  
def copy(obj):
    """ 
    This method will return a copy for a python primitive object.
    It will not work for class objects unless they implement the 
    __init__(other) constructor
    """
    if hasattr(obj,'copy'):
      o = obj.copy()
    else:
      try:
        o = type(obj)(other=obj)
      except:
        o = type(obj)(obj)
    return o

##############################################################################
# Methods for pickling/dumping, passing objects to files/queues
    
def obj2dict(obj,type_check=True,class_check=False,fltr=None):
    """ 
    Converts a python object to a dictionary with all its members 
    as python primitives 
    
    This can be used in Queues or to convert to str using pickle.dumps
    
    :param fltr: a callable(name):bool method
    """
    dct = {}
    try:
        for name in dir(obj):
            if fltr and not fltr(name):
                continue
            try:
                attr = getattr(obj,name)
                if hasattr(attr,'__call__'): continue
                if name == 'inited_class_list': continue
                if name.startswith('__'): continue
                if type_check:
                    try: 
                        if type(attr).__name__ not in dir(__builtin__):
                            if isinstance(attr,dict):
                                attr = dict((k,v) for k,v in list(attr.items()))
                            else:
                                attr = str(attr)
                    except: 
                        continue
                dct[name] = attr
            except Exception as e:
                print(e)

        if class_check:
            klass = obj.__class__
            if '__class__' not in dct: 
                dct['__class__'] = klass.__name__
            if '__bases__' not in dct: 
                dct['__bases__'] = [b.__name__ for b in klass.__bases__]
            if '__base__' not in dct: 
                dct['__base__'] = klass.__base__.__name__
                
    except Exception as e:
        print(e)
    return(dct)

def pick(filename, keys = []):
    import pickle
    try:
        f = open(filename)
        v = pickle.load(f)
        if keys:
            try:
                for k in keys:
                    v = v[k]
            except:
                traceback.print_exc()
        return v
    except:
        traceback.print_exc()
    finally:
        f.close()

def dump(value, filename, as_dict = False):
    import pickle
    try:
        f = open(filename, 'w')
        if not as_dict:
            try:
                pickle.dump(value, f)
            except:
                as_dict = True
        if as_dict:
            pickle.dump(obj2dict(value), f)
    except:
        traceback.print_exc()
    finally:
        f.close()

## Useful class objects

class Struct(object):
    """
    Metamorphic type to pass/retrieve data objects as object or dictionary
    
    s = Struct(name='obj1',value=3.0)
    s.setCastMethod(lambda k,v: str2type)
    s.cast('3.0') : 3.0
    s.keys() : ['name', 'value']
    s.to_str() : "fandango.Struct({'name': obj1,'value': 3.0,})"
    s.dict() : {'name': 'obj1', 'value': 3.0}
    """
    def __init__(self,*args,**kwargs):
        self.load(*args,**kwargs)
        
    def load(self,*args,**kwargs):
        dct = args[0] if len(args)==1 else (args or kwargs)
        if isSequence(dct) and not isDictionary(dct): 
            dct = dict.fromkeys(dct) #isDictionary also matches items lists
        [setattr(self,k,v) for k,v in (list(dct.items()) 
                                       if hasattr(dct,'items') else dct)]
        
    #Overriding dictionary methods
    def update(self,*args,**kwargs): return self.load(*args,**kwargs)
    def keys(self): return list(self.__dict__.keys())
    def values(self): return list(self.__dict__.values())
    def items(self): return list(self.__dict__.items())
    def dict(self): return self.__dict__
  
    def get(self,k,default=None): 
      try: #Some keys may raise exception
        return getattr(self,k,default)
      except:
        return default
      
    def get_key(self,value):
      """ Reverse lookup """
      for k,v in list(self.items()):
        if v == value:
          return k
      raise Exception('%s_NotFound!'%value)
      
    def set(self,k,v): return setattr(self,k,v)
    def setdefault(self,v): self.dict().setdefault(v)
    def pop(self,k): return self.__dict__.pop(k)
    def has_key(self,k): return k in self.__dict__
    def __getitem__(self,k): return getattr(self,k)
    def __setitem__(self,k,v): return setattr(self,k,v)
    def __contains__(self,k): return hasattr(self,k)

    def __call__(self,*args,**kwargs):
        """getter with one string, setter if 2 are passed"""
        assert len(args) in (1,2)
        if len(args)==2: setattr(self,args[0],args[1])
        elif len(args)==1 and isString(args[0]): return getattr(self,args[0])
        else: self.load(*args,**kwargs)
    def __repr__(self):
        return 'fandango.Struct({\n'+'\n'.join("\t'%s': %s,"%(k,v) 
                                for k,v in list(self.__dict__.items()))+'\n\t})'
    def __str__(self):
        return self.__repr__().replace('\n','').replace('\t','')
    def to_str(self,order=None,sep=','):
        """ This method provides a formatable string for sorting""" 
        return self.__str__() if order is None else (
                                        sep.join('%s'%self[k] for k in order))
      
    def default_cast(self,key=None,value=None):
        """
        This method checks if key is already defined.
        If it is, it will return value as an evaluable string.
        If it is not, then it will do same action on the passed value.
        """
        if key not in list(self.keys()) and not value:
          key,value = None,key #defaults to single argument mode
        value = notNone(value,key and self.get(key))
        if not isString(value): 
          return value
        else:
          return str2type(value)
        
    def cast(self,key=None,value=None,method=None):
        """
        The cast() method is used to convert an struct to a pickable/json obj
        Use set_cast_method(f) to override this call.
        The cast method must accept both key and value keyword arguments.
        """      
        return (method or self.default_cast)(key,value)
        
    def cast_items(self,items=[],update=True):
        """
        The cast() method is used to convert an struct to a pickable/json obj
        """
        items = items or list(self.items())
        items = [(k,self.cast(value=v)) for k,v in list(self.items())]
        if update:
          [self.set(k,v) for k,v in items]
        return items
        
def _fget(self,var):
    return getattr(self,var)
def _fset(self,value,var):
    setattr(self,var,value)
def _fdel(self,var):
    delattr(self,var)
def make_property(var,fget=_fget,fset=_fset,fdel=_fdel):
    """ This Class is in Beta, not fully implemented yet"""
    return property(partial(fget,var=var),partial(fset,var=var),
                    partial(fdel,var=var),doc='%s property'%var)

class Variable(object):
    """
    This class helps to declare module variables that can share the
    state when updated from parent modules.
    
    e.g. fandango.DEFAULT_TIME_FORMAT <=> functional.DEFAULT_TIME_FORMAT
    """
    def __new__(cls, value):
        print((cls,value))
        __instance = object.__new__(cls, value)
        cls.__init__(__instance, value)
        return __instance.value
    
    def __init__(self, value = None):
        self._value = value
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def set_value(self, value):
        self._value = v
        

#class NamedProperty(property):
    #"""
    #"""
    #def __init__(self,name,fget=None,fset=None,fdel=None):
        #self.name = name
        #mname = '%s%s'%(name[0].upper(),name[1:])
        #lname = '%s%s'%(name[0].lower(),name[1:])
        #property.__init__(fget,fset,fdel,doc='NamedProperty(%s)'%self._name)
    #def get_attribute_name(self):
        #return '_%s'self.name
    
def NamedProperty(name,fget=None,fset=None,fdel=None):#,doc=None):
    """ 
    This Class is in Beta, not fully implemented yet
    
    It makes easier to declare name independent property's (descriptors) by 
    using template methods like:
    
    def fget(self,var): # var is the identifier of the variable
        return getattr(self,var)    
    def fset(self,value,var): # var is the identifier of the variable
        setattr(self,var,value)
    def fdel(self,var): # var is the identifier of the variable
        delattr(self,var)    
        
    MyObject.X = Property(fget,fset,fdel,'X')        
    """
    return property(partial(fget,var=name) if fget else None,
                    partial(fset,var=name) if fset else None,
                    partial(fdel,var=name) if fdel else None,doc=name)
    
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
    except Exception as e:
        print('Exception in%s(*%s,**%s): %s' % (f.__name__,args,kwargs,e))
    finally:
        _lock.release()
            
def self_locked(func,reentrant=True):
    ''' Decorator to make thread-safe class members
    @deprecated
    @note see in tau.core.utils.containers
    Decorator to create thread-safe objects.
    reentrant: CRITICAL:
        With Lock() this decorator should not be used to decorate nested 
            functions; it will cause Deadlock!
        With RLock this problem is avoided ... but you should rely more 
            on python threading.
    '''
    @functools.wraps(func)
    def lock_fun(self,*args,**kwargs):
        #self,args = args[0],args[1:]
        if not hasattr(self,'lock'):
            setattr(self,'lock',threading.RLock() if reentrant 
                                    else threading.Lock())
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
    #lock_fun.__name__ = func.__name__
    #lock_fun.__doc__ = func.__doc__
    return lock_fun
    

###############################################################################

def NewClass(classname,classparent=None,classdict=None):
    """ 
    Creates a new class on demand:
     ReleaseNumber = NewClass('ReleaseNumber',tuple,
            {'__repr__':(lambda self:'.'.join(('%02d'%i for i in self)))})
    """
    if classparent and not isSequence(classparent): 
        classparent = (classparent,)
        
    return type(classname,classparent or (object,),classdict or {})

class ReleaseNumber(object):
    """
    ReleaseNumber = type('ReleaseNumber',(tuple,),{
    '__repr__':(lambda self:'.'.join(('%02d'%i for i in self)))
    })
    """
    def __init__(self,*args):
        assert args
        if len(args)==1:
            if isinstance(args[0],basestring):
                args = args[0].split('.')
            elif isSequenceType(args[0]):
                args = args[0]
            else:
                args = [args]
        self._tuple = tuple(args)
        
    def __iter__(self): return self._tuple.__iter__()
    def __len__(self): return self._tuple.__len__()
    def __getitem__(self,i): return self._tuple.__getitem__(i)
    def __hash__(self): return self._tuple.__hash__()

    def __repr__(self):
        return '.'.join(map(str,self))
    
    def major(self):
        try:
            m = int(self[0])
            return m
        except:
            return '0'
    
    def minor(self):
        try:
            m = int(self[1])
            return m
        except:
            return '0'
    
    def patch(self):
        try:
            m = int(self[2])
            return m
        except:
            return self[2] if len(self)>2 else '0'
        
    def __cmp__(self,other):
        if not isinstance(other,ReleaseNumber):
            other = ReleaseNumber(other)
        if self._tuple == other._tuple:
            return 0
        if int(self.major()) < other.major():
            return -1
        if int(self.major()) > other.major():
            return 1
        if int(self.minor()) < other.minor():
            return -1
        if int(self.minor()) > other.minor():
            return 1
        if self.patch() < other.patch():
            return -1
        if self.patch() > other.patch():
            return 1
        return 0
        
    def __gt__(self,other): return self.__cmp__(other) > 0
    def __ge__(self,other): return self.__cmp__(other) >= 0
    def __lt__(self,other): return self.__cmp__(other) < 0
    def __le__(self,other): return self.__cmp__(other) <= 0
    def __eq__(self,other): return not self.__cmp__(other)
    def __ne__(self,other): return self.__cmp__(other)

    
###############################################################################

class Object(object):
    """
    This class solves some problems when an object inherits from multiple 
    classes and some of them inherit from the same 'grandparent' class
    """ 

    def __init__(self):
        """ default initializer 
        @todo be more clever!
        """
        pass
        #self.name = None    
        ## @var name
        # Var does nothing    
        # @todo be more clever!
        
        pass
        
    def call__init__(self, klass, *args, **kw):
        if 'inited_class_list' not in self.__dict__:
            self.inited_class_list = []

        if klass not in self.inited_class_list:
            self.inited_class_list.append(klass)
            #print('#'*80)
            #print('%s(%s).call__init__(%s,%s)' % (
              #type(self).__name__,klass.__name__,args,kw))
            #print('#'*80)
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
        #if _args: 
        #   raise Exception,'__init_all_Object_withUnnamedArgumentsException'
        from inspect import getargspec
        #print '%s.call_all__init__(%s,%s)' % (klass.__name__,_args,_kw)
        for base in klass.__bases__:
            if 'call__init__' in dir(base) and \
                ('inited_class_list' not in self.__dict__ 
                 or base not in self.inited_class_list):
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
                except Exception as e:
                    print('Unable to execute %s.__init__!: %s' 
                          % (base.__name__,str(e)))
        return
            
    def getAttrDict(self):
        return obj2dict(self)
        
    def updateAttrDict(self, other):
        attr = other.getAttrDict()
        self.__dict__.update(attr)
        

###############################################################################

class Singleton(object):
    """
    This class allows Singleton objects overriding __new__ and renaming 
    __init__ to init_single
    
    The __new__ method is overriden to force Singleton behaviour, 
    the Singleton is created for the lowest subClass.
    
    @warning although __new__ is overriden __init__ is still being called 
    for each instance=Singleton(), this is way we replace it by __dub_init
    """   
    ## Singleton object
    # the one, true Singleton, private members cannot be read directly
    __instance = None 
    __dumb_init = (lambda self,*p,**k:None)
    
    def __new__(cls, *p, **k):
        if cls != type(cls.__instance):
            __instance = object.__new__(cls)
            #srubio: added init_single check to prevent redundant __init__ calls
            if hasattr(cls,'__init__') and cls.__init__ != cls.__dumb_init:
                setattr(cls,'init_single',cls.__init__)
                #Needed to avoid parent __init__ methods to be called
                setattr(cls,'__init__',cls.__dumb_init)  
            if hasattr(cls,'init_single'): 
                #If no __init__ or init_single has been defined it may trigger 
                #an object.__init__ warning!
                cls.init_single(__instance,*p,**k) 
                
            #Done at the end to prevent failed __init__ to create singletons
            cls.__instance = __instance 
        return cls.__instance
    
    @classmethod
    def get_singleton(cls,*p,**k):
        return cls.__instance or cls(*p,**k)
    
    @classmethod
    def clear_singleton(cls):
        cls.__instance = None

class SingletonMap(object):
    """
    This class allows distinct Singleton objects for each args combination.
    The __new__ method is overriden to force Singleton behaviour, the Singleton
    is created for the lowest subClass.
    
    @warning although __new__ is overriden __init__ is still being called 
    for each instance=Singleton(), this is way we replace it by __dub_init
    """
    
    ## Singleton object
    # the one, true Singleton, private members cannot be read directly
    __instances = {} 
    __dumb_init = (lambda self,*p,**k:None)    
    
    def __new__(cls, *p, **k):
        key = cls.parse_instance_key(*p,**k)
        if cls != type(cls.__instances.get(key)):
            __instance = object.__new__(cls)
            __instance.__instance_key = key
            #srubio:added init_single check to prevent redundant __init__ calls

            if hasattr(cls,'__init__') and cls.__init__ != cls.__dumb_init:
                setattr(cls,'init_single',cls.__init__)
                #Needed to avoid parent __init__ methods to be called
                setattr(cls,'__init__',cls.__dumb_init) 

            if hasattr(cls,'init_single'): 
                #If no __init__ or init_single has been defined it may trigger 
                #an object.__init__ warning!
                cls.init_single(__instance,*p,**k) 

            cls.__instances[key] = __instance

            #print('#'*80+'\n'+'%s.__instances[%s] = %s'
            #   %(str(cls),key,str(__instance))

        return cls.__instances[key]
            
    @classmethod
    def get_singleton(cls,*p,**k):
        key = cls.parse_instance_key(*p,**k)
        return cls.__instances.get(key,cls(*p,**k))
    
    @classmethod
    def get_singletons(cls):
        return cls.__instances       
    
    @classmethod
    def clear_singleton(cls,*p,**k):
        cls.__instances.pop(cls.parse_instance_key(*p,**k))
        
    @classmethod
    def clear_singletons(cls):
        cls.__instances.clear()
      
    @classmethod
    def parse_instance_key(cls,*p,**k):
        return '%s(*%s,**%s)' % (cls.__name__,list(p),list(sorted(k.items())))
    
    def get_instance_key(self):
        return self.__instance_key


###############################################################################

class nullDecorator(object):
    """
    Empty decorator with null arguments, used to replace pyqtSignal,pyqtSlot
    """
    def __init__(self,*args): 
        pass
    def __call__(self,f): 
        return f

def decorator_with_args(decorator):
    '''
    Decorator with Arguments must be used with parenthesis: @decorated() 
    , even when arguments are not used!!!
    
    This method gets an d(f,args,kwargs) decorator and returns a new 
    single-argument decorator that embeds the new call inside.
    
    But, this decorator disturbed stdout!!!! 
    
    There are some issues when calling nested decorators; it is clearly 
    better to use Decorator classes instead.
    '''
    # decorator_with_args = lambda decorator: \
    #    lambda *args, **kwargs: lambda func: decorator(func, *args, **kwargs)

    return lambda *args, **kwargs: lambda func: decorator(func, *args, **kwargs)

class Decorated(object): 
    """
    @TODO: This class should provide an API to get all decorators
    applied to a python object and its methods
    """
    pass

class Decorator(object):
    """
    This generic class allows to differentiate decorators from common classes.
    """
    __example__ = """
    SEE THE Cached DECORATOR CLASS FOR A REAL EXAMPLE, THIS IS JUST AN
    ABSTRACT CLASS WITHOUT IMPLEMENTATION
    
    It uses the __get__ descriptor to allow decoration of Class methods
    
    Inherit from it and use issubclass(klass,Decorator) to know if a class
    is a decorator
    
    To add arguments to decorator reimplement __init__
    
    To modify your wrapper reimplement __call__
    
    A decorator __init__ with a single argument can be called like:
    
      @D
      def f(x): 
        pass
    
    If you need a Decorator with arguments then __init__ will manage the 
    arguments and __call__ will take the function and return a wrapper instead.
    
      @D(x,y)
      def f(z):
        pass
    """
    
    @classmethod
    def new_wrapped_instance(cls, *args, **kwargs):
        """ obtain a better wrapped instance, experimental, doesnt work well on py2 """
        func = args and args[0] or None
        i = object.__new__(type(cls.__name__+'_'+func.__name__,(cls,),
            {'__doc__': func.__doc__}))
        cls.__init__(i,*args,**kwargs)
        return i        
    
    def __init__(self,func):
        self.func = func
         #self.call = wraps(self.func)(self.__call__) #Not for methods!!
        functools.update_wrapper(self,self.func)
        
    def __call__(self,*args,**kwargs):
        return self.func(*args,**kwargs)
      
    def __get__(self,obj,objtype=None):
        """
        This bounding method will be called only when decorating an
        instance method
        """
        return MethodType(self,obj,objtype)
    
    def get_func(self):
        return self.func
      
class ClassDecorator(Decorator): 
    """ 
    This empty class is not trivial. It identifies the QObject decorators
    from fandango.qt module
    
    Although empty, it is critical for Vacca. Modify it with care
    """
    pass      
    
class Cached(Decorator):
    """
    This decorator will provide a function that caches up to N different
    executions of a method (for different combinations of arguments) for 
    a given period. It is very similar to functools.lru_cache in py3 
    """
    __example__ = """
    
    e.g.: check_device_cached = Cached(check_device,depth=10,keep=3)
    
    It will keep cached for 3 seconds up to 10 different device check results.
    
    If "func" is not declared, then it can be used as a decorator_with_args
    
    @Cached(depth=10,keep=3)
    def check_device(*a,**k): 
      ...
      return
      
    The catched argument will print and return exceptions instead of throwing
    """
  
    def __init__(self,func=None,depth=10,expire=3.,log=False,catched=False):

        self.log = log
        self._im = None
        self.cache = {}
        self.depth = depth
        self.expire = expire
        self.catched = catched
        self.decorate(func)
        #self.__code__ = getattr(func,'__code__',None)
        self.__doc__ = '@Cached:'+str(getattr(func,'__doc__','') or '')
        self.lock = threading.Lock()
          
    def __call__(self,*args,**kwargs):
        """
        This method will either decorate a method (with args) or execute it
        """
        if self.func is None:
            # Deferred decorator
            self.decorate(args[0])
            return self
        else:
            # Instantiated decorator
            return self.execute(*args,**kwargs)
          
    def _log(self,msg):
        if isCallable(self.log): 
          self.log(msg) 
        elif self.log: 
          print(msg)
      
    @staticmethod
    def getCachedObject(obj,methods=[],depth=10.,expire=3.,catched=False):
        """ @RISKY
        This method will try to apply Cached decorator to all methods 
        of an object. USE IT AT YOUR OWN RISK!!
        """
        klass = obj if isinstance(obj,type) else type(obj)
        if not methods:
            methods = [k for k,f in list(klass.__dict__.items()) if isCallable(f)]
        for k in methods:
            try:
                m = Cached(getattr(klass,k),depth,expire,catched=catched)
                setattr(obj,k,m)
            except:pass
        return obj
    
    def decorate(self,func):
        if isCallable(func):
            #self._log('decorate(%s)'%str(func))
            self.func = func
            #self.call = wraps(self.func)(self.__call__) #Not for methods!!
            functools.update_wrapper(self,self.func)
        else:
            self.func = None
            
    def prune(self,expire=None,depth=None):
        try:
            self.lock.acquire()
            depth = notNone(depth,self.depth)
            expire = time.time()-notNone(expire,self.expire)
            cache = sorted(k for k in list(self.cache.keys()) if k[0]>expire)
            if (len(cache)!=len(self.cache) or len(cache)>self.depth):
                #self._log('pruning: %s => %s'%(len(self.cache),len(cache)))
                pass
                
            self.cache = dict((k,self.cache[k]) for k in cache[-self.depth:])
            return sorted(self.cache.keys())
        finally:
            self.lock.release()
    
    def clear(self):
        self.cache.clear()
        
    def execute(self,*args,**kwargs):
        #self._log('__call__(%s,%s)'%(args,kwargs))
        v,match,expire = None,None,self.expire
        
        try:
            key = time.time(),tuple(args),tuple(kwargs.items())
            #assert all(isinstance(k,Hashable) for l in key[1:] for k in l)
            assert isHashable(key)
        except:
            self._log('unhashable arguments!')
            expire = 0
        
        if not self.depth or not expire:
            self._log('disabling cache ...')
            if not self.depth: self.cache = {}
            return self.func(*args,**kwargs)
        
        else:
            cache = self.prune(expire)
            match = first((k for k in cache if (k[1:]) == (key[1:])),None)
            
            if match:
                v = self.cache[match]
                #self._log('(%s,%s) was in cache: %s'%(args,kwargs,v))
            else:
                try:
                    v = self.func(*args,**kwargs)
                except Exception as e:
                    v = e
                #self._log('%s(%s,%s) = %s'%(self.func,args,kwargs,v))
                try:
                    self.cache[key] = v
                except:
                    print('%s(%s,%s) = %s'%(self.func,args,kwargs,v))
                    print('cache[%s] = %s'%(key,v))
                    raise
            
        if isinstance(v,Exception):
            if self.catched:
                if not match:
                    self._log(traceback.format_exc())
                return v
            else:
                self._log(str(self.func))
                self._log(traceback.format_exc())
                raise v
        else:
            return v
        
def Queued(my_queue):
    """
    This decorator will put the result of the function
    into a Queue-like object (using put() method)
    
    Intended to be used in processes and threads
    
    If use_id is True, then str(fun)+str(args) will be used
    as ID for the result.
    """
    def QueuedDecorator(method, use_id=False):
        def QueuedFunction(*args,**kwargs):
            r = method(*args,**kwargs)
            if use_id:
                r = (str(method)+str(args)+str(sorted(kwargs.items())),
                     r)
            my_queue.put(r)
        return QueuedFunction
    return QueuedDecorator        

###########################################################################
    
## @DEPRECATED!
class BoundDecorator(Decorator):
    """
    DEPRECATED , To be removed in Fandango 13; 
    replaced by the use of __get__ descriptor
    
    Inspired in 
    https://wiki.python.org/moin/PythonDecoratorLibrary
      #Class_method_decorator_using_instance
        Class method decorator specific to the instance.
        It uses a descriptor to delay the definition of the
        method wrapper.
    
    To use it, just inherit from it and rewrite the wrapper method
    
    Example:
    
    from fandango.objects import BoundDecorator
    BoundDecorator().tracer = 1
    
    class X(object):
        def __init__(self,name):
        self.name = name
        def f(self,*args):
        return (self.name,args)
    
    class D(BoundDecorator):
        @staticmethod
        def wrapper(instance,f,*args,**kwargs):
            print('guess what?')
            v = f(instance,*args,**kwargs)
            return v[0]
    
    x = X('a')
    X.f = D()(X.f)
    x.f()
    """
    
    def __init__(self,*args,**kwargs):
        print('BoundDecorator is DEPRECATED!!!, Use Decorator.__get__ instead')
        Decorator.__init__(self,*args,**kwargs)
    
    @staticmethod
    def wrapper(instance,f,*args,**kwargs):
        return f(instance, *args, **kwargs)
    
    class _Tracer(object):
        def __init__(self):
            self._trace = False
        def __get__(self,obj,type=None):return self
        def __set__(self,obj,value):self._trace = value
        def __bool__(self): return self._trace
        def __call__(self,msg):
            if self: print(msg)
            
    #NOTE: Giving a value to Tracer only works with instances; not from class            
    tracer = _Tracer() 
    
    def __call__(this,f=None):
        class _Descriptor(BoundDecorator):
            # Inherits to get the wrapper from the BoundDecorator class 
            # and be able to exist "onDemand"
            def __init__(self, f):
                self.func = f
            def __get__(self, instance, klass):
                BoundDecorator.tracer('__get__(%s,%s)'%(instance,klass))
                if instance is None:
                    # Class method was requested
                    return self.make_unbound(klass)
                return self.make_bound(instance)
            def make_unbound(self, klass):
                BoundDecorator.tracer('make_unbound(%s)'%klass)
                
                @functools.wraps(self.func)
                def wrapper(*args, **kwargs):
                    '''This documentation will disapear :)
                    This method may work well only without arguments
                    '''
                    BoundDecorator.tracer(
                        "Called the unbound method %s of %s"
                        %(self.func.__name__, klass.__name__))
                    return partial(this.wrapper,f=f)(*args,**kwargs)    
                return wrapper
            
            def make_bound(self, instance):
                BoundDecorator.tracer('make_bound(%s)'%instance)
                @functools.wraps(self.func)
                def wrapper(*args, **kwargs):
                    '''This documentation will disapear :)'''
                    BoundDecorator.tracer(
                        "Called the decorated method %s of %s"
                        %(self.func.__name__, instance))
                    #return self.func(instance, *args, **kwargs)
                    return this.wrapper(instance,f,*args,**kwargs)
                #wrapper = self.wrapper #wraps(self.func)(self.wrapper)
                # This instance does not need the descriptor anymore,
                # let it find the wrapper directly next time:
                setattr(instance, self.func.__name__, wrapper)
                return wrapper

        return _Descriptor(f)


from . import doc
__doc__ = doc.get_fn_autodoc(__name__,vars())
