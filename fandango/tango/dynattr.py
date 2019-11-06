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
Additional Classes for managing fandango.DynamicDS attribute types
"""

#==============================================================================
#
#   Additional Classes for Attribute types management ...
#
#==============================================================================

__all__ = ['DynamicDSType','DynamicDSTypes','isTypeSupported',
           'castDynamicType','DynamicAttribute']

import PyTango
from PyTango import AttrQuality
import fandango
import fandango.functional as fun
import re, time, inspect, traceback

class DynamicDSType(object):
    """ Allows to parse all the Tango types for Attributes """
    def __init__(self,tangotype,labels,pytype,dimx=1,dimy=1):
        self.tangotype=tangotype
        self.name=labels[0] if labels else ''
        self.labels=labels
        self.pytype=pytype
        self.dimx=dimx
        self.dimy=dimy
    def match(self,expr):
        expr = expr.strip()
        for l in self.labels:
            t = l.replace('(','\(').replace('[','\[')+'[\(,]'
            if re.match(t,expr) or expr.startswith(l):
                return True
        return False

#: Dictionary that contains the definition of all types 
#   available in DynamicDS attributes
#: Tango Type casting in formulas is done using int(value), 
#   SPECTRUM(int,value), IMAGE(int,value) for bool,int,float,str types
DynamicDSTypes={
    # Labels will be matched at the beginning of formulas using 
    # re.match(label+'[(,]',formula)
    'DevState':
        DynamicDSType(PyTango.ArgType.DevState,['DevState',],int),
    'DevLong':
        DynamicDSType(PyTango.ArgType.DevLong,
            ['DevLong','DevULong','int','SCALAR(int','DYN(int'],int),
    'DevLong64':
        DynamicDSType(PyTango.ArgType.DevLong,
            ['DevLong64','DevULong64','long','SCALAR(long'],long),
    'DevShort':
        DynamicDSType(PyTango.ArgType.DevShort,
            ['DevShort','DevUShort','short'],int),
    'DevString':
        DynamicDSType(PyTango.ArgType.DevString,
            ['DevString','str','SCALAR(str'],lambda x:str(x or '')),
    'DevBoolean':
        DynamicDSType(PyTango.ArgType.DevBoolean,
            ['DevBoolean','bit','bool','Bit','Flag','SCALAR(bool'],
            lambda x:False if str(x).strip().lower() 
            in ('','0','none','false','no') else bool(x)),
    'DevDouble':
        DynamicDSType(PyTango.ArgType.DevDouble,
            ['DevDouble','DevDouble64','double','float',
            'DevFloat','IeeeFloat','SCALAR(float'],float),
            
    'DevVarLongArray':
        DynamicDSType(PyTango.ArgType.DevLong,
            ['DevVarLongArray','DevVarULongArray',
            'SPECTRUM(int','list(int','[int'],
            lambda l:[int(i) for i in 
                ([],l)[hasattr(l,'__iter__')]],4096,1),
    'DevVarLong64Array':
        DynamicDSType(PyTango.ArgType.DevLong,
            ['DevVarLong64Array','DevVarULong64Array',
            'SPECTRUM(long','list(long','[long'],
            lambda l:[long(i) for i in 
                ([],l)[hasattr(l,'__iter__')]],4096,1),            
    'DevVarShortArray':
        DynamicDSType(PyTango.ArgType.DevShort,
            ['DevVarShortArray','DevVarUShortArray',
            'list(short','[short'],
            lambda l:[int(i) for i in 
                ([],l)[hasattr(l,'__iter__')]],4096,1),
    'DevVarStringArray':
        DynamicDSType(PyTango.ArgType.DevString,
            ['DevVarStringArray','SPECTRUM(str','list(str','[str'],
            lambda l:[str(i) for i in 
                ([],l)[hasattr(l,'__iter__')]],4096,1),
    'DevVarBooleanArray':
        DynamicDSType(PyTango.ArgType.DevShort,
            ['DevVarBooleanArray','SPECTRUM(bool','list(bool','[bool'],
            lambda l:[bool(i) for i in 
                ([],l)[hasattr(l,'__iter__')]],4096,1),
    'DevVarDoubleArray':
        DynamicDSType(PyTango.ArgType.DevDouble,
            ['DevVarDoubleArray','SPECTRUM(float',
            'list(double','[double','list(float','[float'],
            lambda l:[float(i) for i in 
                ([],l)[hasattr(l,'__iter__')]],4096,1),
            
    'DevVarLongImage':
        DynamicDSType(PyTango.ArgType.DevLong,
            ['DevVarLongImage','IMAGE(int,'],
            lambda l:[map(int,i) for i in 
                ([],l)[hasattr(l,'__iter__')]],4096,4096),
    'DevVarLong64Image':
        DynamicDSType(PyTango.ArgType.DevLong,
            ['DevVarLong64Image','IMAGE(long,'],
            lambda l:[map(long,i) for i in 
                ([],l)[hasattr(l,'__iter__')]],4096,4096),            
    'DevVarShortImage':
        DynamicDSType(PyTango.ArgType.DevShort,
            ['DevVarShortImage',],
            lambda l:[map(int,i) for i in 
                ([],l)[hasattr(l,'__iter__')]],4096,4096),
    'DevVarStringImage':DynamicDSType(PyTango.ArgType.DevString,
            ['DevVarStringImage','IMAGE(str,'],
            lambda l:[map(str,i) for i in 
                ([],l)[hasattr(l,'__iter__')]],4096,4096),
    'DevVarBooleanImage':
        DynamicDSType(PyTango.ArgType.DevShort,
            ['DevVarBooleanImage','IMAGE(bool,'],
            lambda l:[map(bool,i) for i in 
                ([],l)[hasattr(l,'__iter__')]],4096,4096),
    'DevVarDoubleImage':
        DynamicDSType(PyTango.ArgType.DevDouble,
            ['DevVarDoubleImage','IMAGE(float,',],
            lambda l:[map(float,i) for i in 
                ([],l)[hasattr(l,'__iter__')]],4096,4096),     
}

for a,b in [('Float','Double'),('ULong','Long'),('ULong64','Long64'),
            ('UShort','Short'),('Char','Short'),('UChar','Char'),
            ('Double64','Double'),]:
    ta,tb = 'Dev%s'%a,DynamicDSTypes['Dev%s'%b]
    pt = PyTango.ArgType.names.get(ta)
    DynamicDSTypes[ta] = DynamicDSType(
        pt,[ta],tb.pytype,tb.dimx,tb.dimy)
    ta, tb = 'DevVar%sArray'%a, DynamicDSTypes['DevVar%sArray'%b]
    DynamicDSTypes[ta] = DynamicDSType(
        pt,[ta],tb.pytype,tb.dimx,tb.dimy)
    ta, tb = 'DevVar%sImage'%a, DynamicDSTypes['DevVar%sImage'%b]
    DynamicDSTypes[ta] = DynamicDSType(
        pt,[ta],tb.pytype,tb.dimx,tb.dimy)
    
            
def isTypeSupported(ttype,n_dim=None):
    if n_dim is not None and n_dim not in (0,1): return False
    ttype = getattr(ttype,'name',str(ttype))
    return any(ttype in t.labels for t in DynamicDSTypes.values())

def castDynamicType(dims,klass,value):
    t = {(0,int):'DevLong',(0,float):'DevDouble',
         (0,bool):'DevBoolean',(0,str):'DevString',
         (1,int):'DevVarLongArray',(1,float):'DevVarDoubleArray',
         (1,bool):'DevVarBooleanArray',(1,str):'DevVarStringArray',
         (2,int):'DevVarLongImage',(2,float):'DevVarDoubleImage',
         (2,bool):'DevVarBooleanImage',(2,str):'DevVarStringImage',}
    return DynamicDSTypes[t[dims,klass]].pytype(value)
            
    
class DynamicAttribute(object):
    ''' 
    This class provides a background for dynamic attribute management and 
    interoperativity
    Future subclasses could override the operands of the class to manage 
    quality and date modifications
    '''
    qualityOrder = [AttrQuality.ATTR_VALID, AttrQuality.ATTR_CHANGING, 
        AttrQuality.ATTR_WARNING, AttrQuality.ATTR_ALARM, 
        AttrQuality.ATTR_INVALID]

    def __init__(self,value=None,date=0.,quality=AttrQuality.ATTR_VALID,name=''):
        self.name = name
        self.value=value
        self.max_peak=(value if not hasattr(value,'__len__') else None,0)
        self.min_peak=(value if not hasattr(value,'__len__') else None,0)
        self.forced=None
        self.date=date
        self.quality=quality
        self.updated = 0
        self.formula=None
        self.compiled = None
        self.states_queue=[]
        self.type=None
        self.keep = True
        self.dependencies = None #it will be initialized to set() in evalAttr
        self.primeOlder=False #
        #self.__add__ = lambda self,other: self.value.__add__(other)

    def getItem(self,index=None):
        if type(self.value) is list or list in self.value.__class__.__bases__:
            return self.value.__getitem__(index)
        elif not index:
            return value
        else:
            raise Exception,'InvalidIndex%sFor%s'%(str(index),str(value))

    def update(self,value,date,quality,t=None):
        self.value=value
        self.date=date
        self.quality=quality
        self.updated = t or fun.now()
        try: 
            if value is not None and not hasattr(value,'__len__') and not isinstance(value,Exception):
                if self.max_peak[0] is None or self.value>self.max_peak[0]:
                    self.max_peak = (value,date)
                if self.min_peak[0] is None or self.value<self.min_peak[0]:
                    self.min_peak = (value,date)
        except: pass

    def __add__(self,other):
        result = DynamicAttribute()
        #This method is wrong, qualities are not ordered by criticity!
        result.update(self.value.__add__(other),min([self.date,other.date]),max([self.quality,other.quality]))
        return result.value

    def __repr__(self,klass='DynamicAttribute'):
        r='%s({'%klass
        r+='"%s": %s; '%('value',repr(self.value))
        r+='"%s": "%s"; '%('date',time.ctime(self.date))
        r+='"%s": %s; '%('quality',str(self.quality))
        if self.type: r+='"%s": %s; '%('type',hasattr(self.type,'labels') and self.type.labels[0] or str(self.type))
        r+='})'
        if len(r)>80*2: r = r.replace(';',',\n\t')
        else: r = r.replace(';',',')
        return r

    def operator(self,op_name,other=None,unary=False,multipleargs=False):
        #print('operator() called for %s(%s).%s(%s)'%(self.__class__,str(type(self.value)),op_name,other and other.__class__ or ''))
        value = self.value

        if value is None:
            if op_name in ['__nonzero__','__int__','__float__','__long__','__complex__']: 
                value = 0
            elif op_name in ['__str__','__repr__']:
                return ''
            else:
                return None

        result = DynamicAttribute()
        result.quality,result.date,result.primeOlder=self.quality,self.date,self.primeOlder
        op_name = '__len__' if op_name == '__nonzero__' and type(value) is list else op_name
        
        if op_name in ['__eq__','__lt__','__gt__','__ne__','__le__','__ge__'] and '__cmp__' in dir(value):
            if op_name is '__eq__': method = lambda s,x: not bool(s.__cmp__(x))
            if op_name is '__ne__': method = lambda s,x: bool(s.__cmp__(x))
            if op_name is '__lt__': method = lambda s,x: (s.__cmp__(x)<0)
            if op_name is '__le__': method = lambda s,x: (s.__cmp__(x)<=0)
            if op_name is '__gt__': method = lambda s,x: (s.__cmp__(x)>0)
            if op_name is '__ge__': method = lambda s,x: (s.__cmp__(x)>=0)

        elif hasattr(type(value),op_name) and hasattr(value,op_name): 
            #Be Careful, method from the class and from the instance don't get the same args
            method = getattr(type(value),op_name)
            #print('Got %s from %s: %s'%(op_name,type(value),method))
        #elif op_name in value.__class__.__base__.__dict__:
        #    method = value.__class__.__base__.__dict__[op_name]

        else:
            raise Exception,'DynamicAttribute_WrongMethod%sFor%sType==(%s)'% (
                    op_name,str(type(value)),value)

        if unary:
            if value is None and op_name in ['__nonzero__','__int__','__float__','__long__','__complex__']: 
                result.value = method(0)
            else:
                result.value = method(value)
        elif multipleargs:
            args=[value]+list(other)
            result.value = method(*args)
        elif isinstance(other,DynamicAttribute):
            #print(str(self),'.',op_name,'(',str(other),')')
            result.quality = self.quality if self.qualityOrder.index(self.quality)>self.qualityOrder.index(other.quality) else other.quality
            result.date = min([self.date,other.date]) if self.primeOlder else max([self.date,other.date])
            result.value = method(value,other.value)
        else:
            #print('%s,%s(%s),%s(%s)' % (method,type(value),value,type(other),other))
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


 
