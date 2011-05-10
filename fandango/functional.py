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

import operator
import re
import time,datetime

from operator import isCallable
from functools import partial
from itertools import count,cycle,repeat,chain,groupby,islice,imap,starmap
from itertools import dropwhile,takewhile,ifilter,ifilterfalse,izip
try: from itertools import combinations,permutations,product
except: pass

__all__ = ['partial','first','last','anyone','everyone','isString','isNumber','isSequence','isDictionary','isIterable']

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
    """ It returns the a list containing the objects of all given sequences. """
    if len(seqs)==1 and isSequence(seqs[0]):
        seqs = seqs
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
    for s in seq:
        if method(s): return s
    return s if not s else None        

def everyone(seq,method=bool):
    """Returns last that is true or first that is false"""
    for s in seq:
        if not method(s): return s if not s else None
    return s
        
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
        return [s for s in seq if fun.anyone(re.match(e,s) for e in exprs)]
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
    
def matchTuples(self,mapping,key,value):
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
    return operator.isNumberType(seq)

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

def list2str(seq,MAX_LENGTH=80):
    s = str(seq)
    return s if len(s)<MAX_LENGTH else '%s...%d]'%(s[:MAX_LENGTH-4],len(seq))


########################################################################
## Time conversion
########################################################################

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
    if not cad:
        date = '%Y-%m-%d' if '-' in seq else '%d/%m/%Y'
        hour =  ['',' %H:%M',' %H:%M:%S'][min((seq.count(':'),2))]
        cad = date+hour
    return time.mktime(time.strptime(seq,cad))
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
    

