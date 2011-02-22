#!/usr/bin/env python2.5
""" @if gnuheader
#############################################################################
##
## file :       object.py
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

class Singleton(object):
    """by MarcSantiago from http://code.activestate.com/recipes/52558/
    This class allows Singleton objects
    The __new__ method is overriden to force Singleton behaviour.
    The Singleton is created for the lowest subClass.
    @warning although __new__ is overriden __init__ is still being called for each instance=Singleton()
    
    Working Example of Usage:
    class Prova(objects.Singleton):
        __instantiated__ = 0
        def __init__(self,my_id):
            if self.__class__.__instantiated__:
                print 'already instantiated!'
            else:
                self.__class__.__instantiated__+=1
                print 'first initialization'
                self.name = '%s' % my_id
            return
    """
    
    ## Singleton object
    _the_instance = None     
    #__single = None # the one, true Singleton, private members cannot be read directly
    
    def __new__(cls, *p, **k):
        """
        Check to see if a __single exists already for this class
        Compare class types instead of just looking for None so
        that subclasses will create their own __single objects
        @note __single must be private or protected (_the_instance) ?!?!
        """
        if cls != type(cls._the_instance):
            #cls.__single = object.__new__(cls, *args, **kwargs)
            cls._the_instance = object.__new__(cls, *p, **k)
            #srubio: added init_single check
            if 'init_single' in cls.__dict__: 
                cls._the_instance.init_single(*p,**k)       
                #cls.__single.init_single(*p,**k)            
            else: 
                cls._the_instance.init(*p,**k)
                #cls.__single.init(*p,**k)
        return cls._the_instance #cls.__single
    
    def init(self, *p,**k):
        pass 
        
    #def __init__(self,name=None):
        #self.name = name
    #def _display(self):
        #print self.name,id(self),type(self)
    
   
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
            from object import Object
            
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
        

