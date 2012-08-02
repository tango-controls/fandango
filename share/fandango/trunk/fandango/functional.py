#!/usr/bin/env python2.5
"""
#############################################################################
##
## file :       logic.py
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
"""

import re
import time,datetime

from operator import isCallable
from functools import partial
from itertools import count,cycle,repeat,chain,groupby,islice,imap,starmap
from itertools import dropwhile,takewhile,ifilter,ifilterfalse,izip
try: from itertools import combinations,permutations,product
except: pass

#Load all by default
#__all__ = [
    #'partial','first','last','anyone','everyone',
    #'notNone','isTrue','join','splitList','contains',
    #'matchAll','matchAny','matchMap','matchTuples','inCl','matchCl','searchCl',
    #'toRegexp','isString','isRegexp','isNumber','isSequence','isDictionary','isIterable','isMapping',
    #'list2str','char2int','int2char','int2hex','int2bin','hex2int',
    #'bin2unsigned','signedint2bin',
    #]

########################################################################
## Some miscellaneous logic methods
########################################################################
  
def first(seq):
    """Returns first element of sequence"""
    try: 
        return seq[0]
    except Exception,e:
        try: 
            return seq.next()
        except Exception,d:
            raise d
            #raise e #if .next() also doesn't work throw unsubscriptable exception
    return

def last(seq,MAX=1000):
    """Returns last element of sequence"""
    try:
        return seq[-1]
    except Exception,e:
        try: 
            n = seq.next()
        except: 
            raise e #if .next() also doesn't work throw unsubscriptable exception
        try:
            for i in range(1,MAX):
                n = seq.next()
            if i>(MAX-1):
                raise IndexError('len(seq)>%d'%MAX)
        except StopIteration,e: #It catches generators end
            return n
    return
        
def avg(seq):
    seq = [s for s in seq if seq is not None]
    return sum(seq)/len(seq)
        
def xor(A,B):
    """Returns (A and not B) or (not A and B);
    the difference with A^B is that it works also with different types and returns one of the two objects..
    """
    return (A and not B) or (not A and B)

def notNone(arg,default=None):
    """ Returns arg if not None, else returns default. """
    return [arg,default][arg is None]

def isTrue(arg):
    """ Returns True if arg is not None, not False and not an empty iterable. """
    if hasattr(arg,'__len__'): return len(arg)
    else: return arg
    
def join(*seqs):
    """ It returns a list containing the objects of all given sequences. """
    if len(seqs)==1 and isSequence(seqs[0]):
        seqs = seqs[0]
    result = []
    for seq in seqs: 
        if isSequence(seq): result.extend(seq)
        else: result.append(seq)
    #    result += list(seq)
    return result
        
def splitList(seq,split):
    """splits a list in lists of 'split' size"""
    return [seq[split*i:split*(i+1)] for i in range(1+len(seq)/split)]
    
def contains(a,b,regexp=True):
    """ Returns a in b; using a as regular expression if wanted """
    return inCl(a,b,regexp)

def anyone(seq,method=bool):
    """Returns first that is true or last that is false"""
    if not seq: return False
    for s in seq:
        if method(s): return s
    return s if not s else None

def everyone(seq,method=bool):
    """Returns last that is true or first that is false"""
    if not seq: return False
    for s in seq:
        if not method(s): return s if not s else None
    return seq[-1]

#Dictionary methods

def setitem(mapping,key,value):
    mapping[key]=value

def getitem(mapping,key):
    return mapping[key]

########################################################################
## Regular expressions 
########################################################################
        
def matchAll(exprs,seq):
    """ Returns a list of matched strings from sequence.
    If sequence is list it returns exp as a list.
    """
    exprs,seq = toSequence(exprs),toSequence(seq)
    if anyone(isRegexp(e) for e in exprs):
        exprs = [(e.endswith('$') and e or (e+'$')) for e in exprs]
        return [s for s in seq if anyone(re.match(e,s) for e in exprs)]
    else:
        return [s for s in seq if s in exprs]
    
def matchAny(exprs,seq):
    """ Returns seq if any of the expressions in exp is matched, if not it returns None """
    exprs = toSequence(exprs)
    for exp in exprs:
        if matchCl(exp,seq): 
            #print '===============>   matchAny(): %s matched by %s' % (seq,exp)
            return seq
    return None
    
def matchMap(mapping,key,regexp=True):
    """ from a mapping type (dict or tuples list) with strings as keys it returns the value from the matched key or raises KeyError exception """
    if not mapping: raise ValueError('mapping')    
    if hasattr(mapping,'items'): mapping = mapping.items()
    if not isSequence(mapping) or not isSequence(mapping[0]): raise TypeError('dict or tuplelist required')
    if not isString(key): key = str(key)
    
    for tag,value in mapping:
        if (matchCl(tag,key) if regexp else (key in tag)):
            return value
    raise KeyError(key)
    
def matchTuples(mapping,key,value):
    """ mapping is a (regexp,[regexp]) tuple list where it is verified that value matches any from the matched key """
    for k,regexps in mapping:
        if re.match(k,key):
            if any(re.match(e,value) for e in regexps):
                return True
            else:
                return False
    return True
        
def inCl(exp,seq,regexp=True):
    """ Returns a caseless "in" boolean function, using regex if wanted """
    if not seq: 
        return False
    if isString(seq):
        return searchCl(exp,seq) if (regexp and isRegexp(exp)) else exp.lower() in seq.lower()
    elif isSequence(seq) and isString(seq[0]):
        return any(exp.lower()==s.lower() for s in seq)
    else:
        return exp in seq
    
def matchCl(exp,seq,terminate=False):
    """ Returns a caseless match between expression and given string """
    return re.match(toRegexp(exp.lower(),terminate=terminate),seq.lower())
clmatch = matchCl #For backward compatibility

def searchCl(exp,seq,terminate=False):
    """ Returns a caseless regular expression search between expression and given string """
    return re.search(toRegexp(exp.lower(),terminate=terminate),seq.lower())
clsearch = searchCl #For backward compatibility

def sortedRe(iterator,order):
    """ Returns a list sorted using regular expressions. 
        order = list of regular expressions to match ('[a-z]','[0-9].*','.*')
    """
    if '.*' not in order: order=list(order)+['.*']
    rorder = [re.compile(c) for c in order]
    def sorter(k,ks=rorder):
        k = str(k[0] if isinstance(k,tuple) else k).lower()
        return str((i for i,r in enumerate(ks) if r.match(k)).next())+k
    for i in sorted(iterator,key=sorter):
        print '%s:%s' % (i,sorter(i))
    return sorted(iterator,key=sorter)

def toRegexp(exp,terminate=False):
    """ Replaces * by .* and ? by . in the given expression. """
    exp = str(exp)
    exp = exp.replace('*','.*') if '*' in exp and not any(s in exp for s in ('.*','\*')) else exp
    #exp = exp.replace('?','.') if '?' in exp and not any(s in exp for s in (')?',']?','}?')) else exp
    if terminate and not exp.strip().endswith('$'): exp += '$'
    exp = exp.replace('(?p<','(?P<') #Preventing missing P<name> clausses
    return exp

########################################################################
## Methods for piped iterators
## Inspired by Maxim Krikun [ http://code.activestate.com/recipes/276960-shell-like-data-processing/?in=user-1085177]
########################################################################
        
class Piped:
    """This class gives a "Pipeable" interface to a python method:
        cat | Piped(method,args) | Piped(list)
        list(method(args,cat))
    e.g.: 
    class grep:
        #keep only lines that match the regexp
        def __init__(self,pat,flags=0):
            self.fun = re.compile(pat,flags).match
        def __ror__(self,input):
            return ifilter(self.fun,input) #imap,izip,count,ifilter could ub useful
    cat('filename') | grep('myname') | printlines
    """
    import itertools
    def __init__(self,method,*args,**kwargs):
        self.process=partial(method,*args,**kwargs)
    def __ror__(self,input):
        return imap(self.process,input)
        
class iPiped:
    """ Used to pipe methods that already return iterators 
    e.g.: hdb.keys() | iPiped(filter,partial(fandango.inCl,'elotech')) | plist
    """
    def __init__(self,method,*args,**kwargs): self.process = partial(method,*args,**kwargs)
    def __ror__(self,input): return self.process(input)
    
class zPiped:
    """ 
    Returns a callable that applies elements of a list of tuples to a set of functions 
    e.g. [(1,2),(3,0)] | zPiped(str,bool) | plist => [('1',True),('3',False)]
    """
    def __init__(self,*args): self.processes = args
    def __ror__(self,input): return (tuple(p(i[j]) for j,p in enumerate(self.processes))+tuple(i[len(self.processes):]) for i in input)
    
pgrep = lambda exp: iPiped(lambda input: (x for x in input if inCl(exp,x)))
pmatch = lambda exp: iPiped(lambda input: (x for x in input if matchCl(exp,str(x))))
pfilter = lambda meth=bool,*args: iPiped(filter,partial(meth,*args))
ppass = Piped(lambda x:x)
plist = iPiped(list)
psorted = iPiped(sorted)
pdict = iPiped(dict)
ptuple = iPiped(tuple)
pindex = lambda i: Piped(lambda x:x[i])
pslice = lambda i,j: Piped(lambda x:x[i,j])
penum = iPiped(lambda input: izip(count(),input) )
pzip = iPiped(lambda i:izip(*i))
ptext = iPiped(lambda input: '\n'.join(imap(str,input)))

########################################################################
## Methods for identifying types        
########################################################################
""" Note of the author:
 This methods are not intended to be universal, are just practical for general Tango application purposes.
"""
        
def isString(seq):
    if isinstance(seq,basestring): return True # It matches most python str-like classes
    if any(s in str(type(seq)).lower() for s in ('vector','array','list',)): return False
    if 'qstring' == str(type(seq)).lower(): return True # It matches QString
    return False
    
def isRegexp(seq):
    """ This function is just a hint, use it with care. """
    RE = r'.^$*+?{[]\|()'
    return anyone(c in RE for c in seq)
    
def isNumber(seq):
    #return operator.isNumberType(seq)
    if isinstance(seq,bool): return False
    try: 
        float(seq)
        return True
    except: return False
    
def isNone(seq):
    return seq is None

def isGenerator(seq):
    from types import GeneratorType
    # A generator check must be added to the rest of methods in this module!
    return isinstance(seq,GeneratorType)
    
def isSequence(seq,INCLUDE_GENERATORS = True):
    """ It excludes Strings, dictionaries but includes generators"""
    if any(isinstance(seq,t) for t in (list,set,tuple)): 
        return True
    if isString(seq): 
        return False
    if hasattr(seq,'items'): 
        return False
    if INCLUDE_GENERATORS:
        if hasattr(seq,'__iter__'): 
            return True
    elif hasattr(seq,'__len__'): 
        return True
    return False
    
def isDictionary(seq):
    """ It includes dicts and also nested lists """
    if isinstance(seq,dict): return True
    if hasattr(seq,'items') or hasattr(seq,'iteritems'): return True
    if seq and isSequence(seq) and isSequence(seq[0]):
        if seq[0] and not isSequence(seq[0][0]): return True #First element of tuple must be hashable
    return False
isMapping = isDictionary

def isIterable(seq):
    """ It includes dicts and listlikes but not strings """
    return hasattr(seq,'__iter__') and not isString(seq)

###############################################################################

def str2int(seq):
    """ It returns the first integer encountered in the string """
    return int(re.search('[0-9]+',seq).group())

def str2float(seq):
    """ It returns the first float (x.ye-z) encountered in the string """
    return float(re.search('[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?',seq).group())

def toList(val,default=[],check=isSequence):
    if val is None: 
        return default
    elif hasattr(val,'__len__') and len(val)==0: #To prevent exceptions due to non evaluable numpy arrays
        return [] 
    elif not check(val): #You can use (lambda s:isinstance(s,list)) if you want
        return [val]
    elif not hasattr(val,'__len__'): #It forces the return type to have a fixed length
        return list(val)
    else:
        return val
toSequence = toList

def str2list(s,separator=''): 
    return map(str.strip,s.split(separator) if separator else s.split())

def text2list(s,separator='\n'):
    return filter(bool,str2list(s,separator))

def list2str(s,separator='\t',MAX_LENGTH=255):
    s = str(separator).join(str(t) for t in s)
    if MAX_LENGTH>0 and separator not in ('\n','\r') and len(s)>MAX_LENGTH: 
        s = s[:MAX_LENGTH-4]+'... '
    return s

def text2tuples(s,separator='\t'):
    return [str2list(t,separator) for t in text2list(s)]

def tuples2text(s,separator='\t'):
    return list2str([list2str(t,separator) for t in s],'\n')

########################################################################
## Number conversion
########################################################################

def negbin(old):
    """ Given a binary number as an string, it returns all bits negated """
    return ''.join(('0','1')[x=='0'] for x in old)

def char2int(c): return ord(c)
def int2char(n): return unichr(n)
def int2hex(n): return hex(n)
def int2bin(n): return bin(n)
def hex2int(c): return int(c,16)
def bin2unsigned(c): return int(c,2)

def signedint2bin(x,N=16):
    """ It converts an integer to an string with its binary representation """ 
    if x>=0: bStr = bin(int(x))
    else: bStr = bin(int(x)%2**16)
    bStr = bStr.replace('0b','')
    if len(bStr)<N: bStr='0'*(N-len(bStr))+bStr
    return bStr[-N:]

def bin2signedint(x,N=16):
    """ Converts an string with a binary number into a signed integer """
    i = int(x,2)
    if i>=2**(N-1): i=i-2**N
    return i
    
def int2bool(dec,N=16):
    """Decimal to binary converter"""
    result,dec = [],int(dec)
    for i in range(N):
        result.append(bool(dec % 2))
        dec = dec >> 1
    return result        

########################################################################
## Time conversion
########################################################################

END_OF_TIME = 1024*1024*1024*2 #Jan 19 04:14:08 2038

def now():
    return time.time()

def time2tuple(epoch=None):
    if epoch is None: epoch = now()
    return time.localtime(epoch)
    
def tuple2time(tup):
    return time.mktime(tup)

def date2time(date):
    return tuple2time(date.timetuple())

def date2str(date):
    #return time.ctime(date2time(date))
    return time.strftime('%Y-%m-%d %H:%M:%S',time2tuple(date2time(date)))

def time2date(epoch=None):
    if epoch is None: epoch = now()
    return datetime.datetime.fromtimestamp(epoch)

def time2str(epoch=None,cad='%Y-%m-%d %H:%M:%S'):
    if epoch is None: epoch = now() 
    return time.strftime(cad,time2tuple(epoch))
epoch2str = time2str
    
def str2time(seq,cad=''):
    """ Date must be in ((Y-m-d|d/m/Y) (H:M[:S]?)) format"""
    t,ms = None,re.match('.*(\.[0-9]+)$',seq)
    if ms: ms,seq = float(ms.groups()[0]),seq.replace(ms.groups()[0],'')
    else: ms = 0
    time_fmts = ([cad] if cad else
        [('%s%s%s'%(date.replace('-',dash),separator if hour else '',hour)) 
        for date in ('%Y-%m-%d','%y-%m-%d','%d-%m-%Y','%d-%m-%y','%m-%d-%Y','%m-%d-%y')
        for dash in ('-','/')
        for separator in (' ','T')
        for hour in ('%H:%M','%H:%M:%S','')
        ])
    for tf in time_fmts:
        try:
            t = time.strptime(seq,tf)
            break
        except: pass
    if t is not None: return time.mktime(t)+ms
    else: raise Exception('PARAMS_ERROR','date format cannot be parsed!: %s'%str(seq))    
str2epoch = str2time

def time2gmt(epoch=None):
    if epoch is None: epoch = now()
    return tuple2time(time.gmtime(epoch))
    
def timezone():
    t = now()
    return int(t-time2gmt(t))/3600

#Auxiliary methods:
def ctime2time(time_struct):
    return (float(time_struct.tv_sec)+1e-6*float(time_struct.tv_usec))
    
def mysql2time(mysql_time):
    return time.mktime(mysql_time.timetuple())
    

########################################################################
## Extended eval
########################################################################

def evalX(target,_locals=None,modules=None,instances=None,_trace=False,_exception=Exception):
    """
    target may be:
            - dictionary of built-in types: {'__target__':callable or method_name,'__args__':[],'__class_':'','__module':'','__class_args__':[]}
         - string to eval: eval('import $MODULE' or '$VAR=code()' or 'code()')
         - list if list[0] is callable: value = list[0](*list[1:]) 
         - callable: value = callable()
    """
    import imp,__builtin__
    
    # Only if immutable types are passed as arguments these dictionaries will be preserved.
    _locals = notNone(_locals,{})
    modules = notNone(modules,{})
    instances = notNone(instances,{})
    
    def get_module(_module):
        if module not in modules: 
            modules[module] = imp.load_module(*([module]+list(imp.find_module(module))))
        return modules[module]
    def get_instance(_module,_klass,_klass_args):
        if (_module,_klass,_klass_args) not in instances:
            instances[(_module,_klass,_klass_args)] = getattr(get_module(module),klass)(*klass_args)
        return instances[(_module,_klass,_klass_args)]
        
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
                    if _trace: print('evalX: %s.%s(%s).%s(%s)'%(module,klass,klass_args,target,args))
                    target = getattr(get_instance(module,klass,klass_args),target)
                else:
                    if _trace: print('evalX: %s.%s(%s)'%(module,target,args))
                    target = getattr(get_module(module),target)
            elif klass and klass in dir(__builtin__):
                if _trace: print('evalX: %s(%s).%s(%s)'%(klass,klass_args,target,args))
                instance = getattr(__builtin__,klass)(*klass_args)
                target = getattr(instance,target)
            elif target in dir(__builtin__): 
                if _trace: print('evalX: %s(%s)'%(target,args))
                target = getattr(__builtin__,target)
            else:
                raise _exception('%s()_MethodNotFound'%target)
        else:
            raise _exception('%s()_NotCallable'%target)
        value = target(**args) if isDictionary(args) else target(*args)
        if _trace: print('%s: %s'%(model,value))
        return value
    else:
        #Parse: method[0](*method[1:])
        if isIterable(target) and isCallable(target[0]):
            value = target[0](*target[1:])
        #Parse: method()
        elif isCallable(target):
            value = target()
        elif isString(target):
            if _trace: print('evalX("%s")'%target)
            #Parse: import $MODULE
            if target.startswith('import '): 
                module = target.replace('import ','')
                get_module(module)
                value = module
            #Parse: $VAR = #code
            elif (  '=' in target and 
                    '='!=target.split('=',1)[1][0] and 
                    re.match('[A-Za-z\._]+[A-Za-z0-9\._]*$',target.split('=',1)[0].strip())
                ):
                var = target.split('=',1)[0].strip()
                _locals[var]=eval(target.split('=',1)[1].strip(),modules,_locals)
                value = var
            #Parse: #code
            else:
                value = eval(target,modules,_locals)
        else:
            raise _exception('targetMustBeCallable, not %s(%s)'%(type(target),target))
        if _trace: print('%s: %s'%(target,value))
    return value