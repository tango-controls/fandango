#!/usr/bin/env python2.5
"""
#############################################################################
##
## file :       dicts.py
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
@package dicts

Some extensions to python dictionary
ThreadDict: Thread safe dictionary with redefinable read/write methods and a backgroud thread for hardware update.
defaultdict_fromkey: Creates a dictionary with a default_factory function that creates new elements using key as argument.
CaselessDict: caseless dictionary
CaselessDefaultDict: a join venture between caseless and default dict

@deprecated
@note see in tau.core.utils.containers

by Sergi Rubio, 
srubio@cells.es, 
2008 
"""

import collections

def self_locked(func,reentrant=True):
    ''' Decorator to make thread-safe class members
    @deprecated
    @note see in tau.core.utils.containers
    Decorator to create thread-safe objects.
    reentrant: CRITICAL:
        With Lock() this decorator should not be used to decorate nested functions; it will cause Deadlock!
        With RLock this problem is avoided ... but you should rely more on python threading.
    '''
    import threading
    def lock_fun(self,*args,**kwargs):
        if not hasattr(self,'lock'):
            setattr(self,'lock',threading.RLock() if reentrant else threading.Lock())
        if not hasattr(self,'trace'):
            setattr(self,'trace',False)
        self.lock.acquire()
        try: 
            if self.trace: print "locked: %s"%self.lock
            result = func(self,*args,**kwargs)
        finally: 
            self.lock.release()
            if self.trace: print "released: %s"%self.lock
        return result       
    return lock_fun
            
try:
    import numpy
    class fuzzyDict(dict):
        ## @todo TODO
        def __getitem__(self,key):
            try:
                return dict.__getitem__(self,key)
            except:
                a=numpy.arange(6)*1.1    
                array([ 0. ,  1.1,  2.2,  3.3,  4.4,  5.5])  #The keys of the dictionary
                numpy.abs(a-key).argmin() #returns the index of the nearest key                
                pass
except:
    pass
            
class ThreadDict(dict):
    ''' Thread safe dictionary with redefinable read/write methods and a backgroud thread for hardware update.
    All methods are thread-safe using @self_lock decorator.
        NOTE: any method decorated in this way CANNOT call other decorated methods!
    All values of the dictionary will be automatically updated in a separate Thread using read_method provided.
    Any value overwritten in the dict should launch the write_method.
    
    Briefing:
        a[2] equals to a[2]=read_method(2)
        a[2]=1 equals to a[2]=write_method(2,1)
    
    threadkeys(): 
        returns the list of keys that are being automatically updated in a background thread
    append(key): 
        adds a new key to the dictionary and to the list of keys to be updated
    __setitem__(key,value):tdict[key]=value 
        will also add a new key to the dictionary, but this key value will not be automatically updated.
    
    timewait is a pause inserted between readings
    
    If read_method defined:
        If threaded: the Thread inserts data in the dictionary, __getitem__ retrieves this data
        else: __getitem__ directly executes read_method
    else: __getitem__ as a normal thread-safe dictionary
    If write_method defined:
        any __setitem__ call executes the write_method (dictionary is no affected)
    else: __setitem__ as a normal thread-safe dictionary
    
    @deprecated now in tau.core.utils.containers
    '''
    
    def __init__(self,other=None,read_method=None,write_method=None,timewait=0.1,threaded=True):
        self.read_method = read_method
        self.write_method = write_method
        self.timewait = timewait
        self.threaded = threaded
        self._threadkeys = []
        self.trace = False
        self.last_update = 0
        self.last_cycle_start = 0
        self.parent = type(self).mro()[1] #equals to self.__class__.__base__ or type(self).__bases__[0]
    
    def tracer(self,text): print text
        
    def start(self):
        import threading
        print 'Starting ThreadDict ...'
        if not self.threaded:
            print 'This Dict has no Thread!'
            return
        if hasattr(self,'_Thread') and self._Thread and self._Thread.isAlive():
            print 'ThreadDict.stop() must be executed first!'
            return
        self.event = threading.Event()
        self.event.clear()
        self._Thread = threading.Thread(target=self.run)
        self._Thread.setDaemon(True)
        self._Thread.start()
        self.tracer('ThreadDict started!')
    def stop(self):
        print 'Stopping ThreadDict ...'
        if self.threaded and hasattr(self,'event'): self.event.set()
        if hasattr(self,'_Thread'): self._Thread.join()
        print 'ThreadDict Stopped'

    def alive(self):
        if not hasattr(self,'_Thread') or not self._Thread: return False
        else: return self._Thread.isAlive()
    def __del__(self):
        self.stop()
        #dict.__del__(self)
        
    def run(self):
        self.tracer('In ThreadDict.run()')
        while not self.event.isSet():
            keys = self.threadkeys()
            if self.trace: print 'ThreadDict keys are %s'%keys
            for k in keys:
                if self.trace: self.tracer('ThreadDict::run(): updating %s'%str(k))
                try:
                    #@todo It must be checked wich method for reading is better for thread_safe
                    if True:
                        self.__getitem__(k,hw=True)
                    else: #try this alternative in case of deadlock (it could need extra locks inside read_method)
                        if self.read_method:
                            value = self.read_method(k)
                            self.__setitem__(k,value,hw=False)
                finally:
                    self.event.wait(self.timewait)
                if self.event.isSet(): break
            timewait = self.get_timewait()
            self.event.wait(timewait)
        self.tracer('End of ThreadDict')
        
    @self_locked
    def get_last_update(self): return self.last_update
    @self_locked
    def set_last_update(self,value): self.last_update=value
    
    @self_locked
    def get_last_cycle_start(self): return self.last_cycle_start
    @self_locked
    def set_last_cycle_start(self,value): self.last_cycle_start=value
    
    @self_locked
    def get_timewait(self): return self.timewait
    @self_locked
    def set_timewait(self,value): self.timewait=value    
    
    @self_locked
    def append(self,key,value=None): 
        if not dict.has_key(self,key): self.parent.__setitem__(self,key,value)
        if key not in self._threadkeys: self._threadkeys.append(key)
    
    @self_locked
    def threadkeys(self):
        return self._threadkeys[:]
    
    @self_locked
    def __getitem__(self,key,hw=False):
        ''' This method launches a read_method execution if there's no thread on charge of doing that or if the hw flag is set to True. '''
        import time
        if (hw or not self.threaded) and self.read_method: 
            dict.__setitem__(self,key,self.read_method(key))
            self.last_update = time.time()
        return dict.__getitem__(self,key)    

    @self_locked
    def __setitem__(self,key,value,hw=True):
        ''' This method launches a write_method execution if the hw flag is not explicitly set to False. '''
        import time
        if hw and self.write_method: 
            #It implies that a key will not be added here to read thread!
            dict.__setitem__(self,key,self.write_method(*[key,value]))
        else: dict.__setitem__(self,key,value)
        self.last_update = time.time()
    
    @self_locked
    def get(self,key,default=None):
        import time
        if not self.threaded and self.read_method: 
            dict.__setitem__(self,key,self.read_method(key))
            self.last_update = time.time()
        if default is False: return dict.get(self,key)
        else: return dict.get(self,key,default)
    
    #__getitem__ = self_locked(dict.__getitem__)
    #__setitem__ = self_locked(dict.__setitem__)
    __delitem__ = self_locked(dict.__delitem__)
    __contains__ = self_locked(dict.__contains__)
    __iter__ = self_locked(dict.__iter__)
    
    pop = self_locked(dict.pop)
    #@self_locked
    #def pop(self,k,d=None):
        #if k in self.keys():
            #self.stop()
            #d = dict.pop(self,k)
            #self.start()
        #return d
    
    @self_locked
    def __str__(self):
        return "{" +",".join(["'"+str(k)+"'"+":"+"'"+str(v)+"'" for k,v in zip(dict.keys(self),dict.values(self))])+ "}"
    @self_locked
    def __repr__(self):
        return "{\n" +"\n,".join(["'"+str(k)+"'"+":"+"'"+str(v)+"'" for k,v in zip(dict.keys(self),dict.values(self))])+ "\n}"      
    #__str__ = self_locked(dict.__str__)
    #__repr__ = self_locked(dict.__repr__)
    
    #get = self_locked(dict.get)
    has_key = self_locked(dict.has_key)
    update = self_locked(dict.update)
    copy = self_locked(dict.copy)
    
    keys = self_locked(dict.keys)
    values = self_locked(dict.values)
    items = self_locked(dict.items)
    iterkeys = self_locked(dict.iterkeys)
    itervalues = self_locked(dict.itervalues)   
    iteritems = self_locked(dict.iteritems) 

class defaultdict_fromkey(collections.defaultdict):
    """ Creates a dictionary with a default_factory function that creates new elements using key as argument.
    Usage : new_dict = defaultdict_fromkey(method); where method like (lambda key: return new_obj(key))
    Each time that new_dict[key] is called with a key that doesn't exist, method(key) is used to create the value
    Copied from PyAlarm device server
    @deprecated now in tau.core.utils.containers
    """
    def __missing__(self, key):
        if self.default_factory is None: raise KeyError(key)
        self[key] = value = self.default_factory(key)
        return value
        
class CaselessDict(dict):
    """     Dictionary with caseless key resolution 
    Copied from tau.core.utils.CaselessDict
    @deprecated now in tau.core.utils.containers            
    """
    def __init__(self, other=None):
        if other:
            # Doesn't do keyword args
            if isinstance(other, dict):
                for k,v in other.items():
                    dict.__setitem__(self, k.lower() if hasattr(k,'lower') else k, v)
            else:
                for k,v in other:
                    dict.__setitem__(self, k.lower() if hasattr(k,'lower') else k, v)

    def __getitem__(self, key):
        if dict.has_key(self,key):
            return dict.__getitem__(self,key)
        return dict.__getitem__(self, key.lower() if hasattr(key,'lower') else key)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key.lower() if hasattr(key,'lower') else key, value)

    def __contains__(self, key):
        return dict.__contains__(self, key.lower() if hasattr(key,'lower') else key)

    def has_key(self, key):
        return dict.has_key(self, key.lower() if hasattr(key,'lower') else key)

    def get(self, key, def_val=None):
        return dict.get(self, key.lower() if hasattr(key,'lower') else key, def_val)

    def setdefault(self, key, def_val=None):
        return dict.setdefault(self, key.lower() if hasattr(key,'lower') else key, def_val)

    def update(self, other):
        for k,v in other.items():
            dict.__setitem__(self, k.lower() if hasattr(k,'lower') else k, v)

    def fromkeys(self, iterable, value=None):
        d = CaselessDict()
        for k in iterable:
            dict.__setitem__(d, k.lower() if hasattr(k,'lower') else k, value)
        return d

    def pop(self, key, def_val=None):
        return dict.pop(self, key.lower() if hasattr(key,'lower') else key, def_val)

    def __delitem__(self, k):
        dict.__delitem__(self, k.lower() if hasattr(k,'lower') else k)
        
class CaselessDefaultDict(defaultdict_fromkey,CaselessDict):
    """ a join venture between caseless and default dict
    This class merges the two previous ones.
    This declaration equals to:
        CaselessDefaultDict = type('CaselessDefaultType',(CaselessDict,defaultdict_fromkey),{})
    """
    def __getitem__(self, key):
        return defaultdict_fromkey.__getitem__(self, key.lower())
    pass

class DefaultThreadDict(defaultdict_fromkey,ThreadDict):
    """ a join venture between thread and default dict
        This class merges the two previous ones.
    @deprecated now in tau.core.utils.containers              
    @todo This two classes are not yet well integrated ... the way a new key is added to the dict must be rewritten explicitly.
    """
    def __init__(self,other=None,default_factory=None,read_method=None,write_method=None,timewait=0.1,threaded=True):
        defaultdict_fromkey.__init__(self,default_factory)
        ThreadDict.__init__(self,other,read_method,write_method,timewait,threaded)
    pass