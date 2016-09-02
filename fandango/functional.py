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
fandango.functional::
    contains functional programming methods for python, it should use only python main library methods and not be dependent of any other module
"""

import re
import random
import math
import time,datetime

from operator import isCallable
from functools import partial
from itertools import count,cycle,repeat,chain,groupby,islice,imap,starmap
from itertools import dropwhile,takewhile,ifilter,ifilterfalse,izip
try: from itertools import combinations,permutations,product
except: pass

__test__ = {}

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
  
def first(seq,default=Exception):
    """Returns first element of sequence"""
    try: 
        return seq[0]
    except Exception,e:
        try: 
            return seq.next()
        except Exception,d:
            if default is not Exception:
                return default
            else:
                raise d
            #raise e #if .next() also doesn't work throw unsubscriptable exception
    return

def last(seq,MAX=1000,default=Exception):
    """Returns last element of sequence"""
    try:
        return seq[-1]
    except Exception,e:
        try: 
            n = seq.next()
        except: 
            if default is not Exception:
                return default
            else:
                raise e #if .next() also doesn't work throw unsubscriptable exception
        try:
            for i in range(1,MAX):
                n = seq.next()
            if i>(MAX-1):
                raise IndexError('len(seq)>%d'%MAX)
        except StopIteration,e: #It catches generators end
            return n
    return
        
max = max
min = min
        
def avg(seq):
    seq = [float(s) for s in seq if s is not None]
    if not bool(seq) or not len(seq): return 0
    return sum(seq)/len(seq)

def rms(seq):
    seq = [float(s)**2 for s in seq if s is not None]
    if not bool(seq) or not len(seq): return 0
    return math.sqrt(sum(seq)/float(len(seq)))
    
def randomize(seq):
    done,result = list(range(len(seq))),[]
    while done: result.append(seq[done.pop(random.randrange(len(done)))])
    return result
    
def randpop(seq): 
    return seq.pop(random.randrange(len(seq)))
    
def floor(x,unit=1):
    """ Returns greatest multiple of 'unit' below 'x' """
    return unit*int(x/unit)
    
def xor(A,B):
    """Returns (A and not B) or (not A and B);
    the difference with A^B is that it works also with different types and returns one of the two objects..
    """
    return (A and not B) or (not A and B)

def reldiff(x,y,floor=None): 
    """
    Checks relative (%) difference <floor between x and y
    floor would be a decimal value, e.g. 0.05
    """
    d = x-y
    if not d: return 0
    ref = x or y
    d = float(d)/ref
    return d if not floor else (0,d)[abs(d)>=floor]
    #return 0 if x*(1-r)<y<x*(1+r) else -1

def absdiff(x,y,floor=0.01):
    """
    Checks absolute difference <floor between x and y
    floor would be a decimal value, e.g. 0.05
    """
    d = x-y
    if not d: return 0
    return d if not floor else (0,d)[abs(d)>=floor]
    #return 0 if x-r<y<x+r else -1

def seqdiff(x,y,method=reldiff,floor=None):
    """
    Being x and y two arrays it checks (method) difference <floor between the elements of them.
    floor would be a decimal value, e.g. 0.05
    """
    if not floor:
        d = any(method(v,w) for v,w in zip(x,y))
    else:
        d = any(method(v,w,floor) for v,w in zip(x,y))
    return d

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
        
def djoin(a,b):
    """ This method merges dictionaries and/or lists """
    if not any(map(isDictionary,(a,b))): return join(a,b)
    other,dct = sorted((a,b),key=isDictionary) 
    if not isDictionary(other): 
        other = dict.fromkeys(other if isSequence(other) else [other,])
    for k,v in other.items():
        dct[k] = v if not k in dct else djoin(dct[k],v)
    return dct
  
def kmap(method,keys,values=None,sort=True):
    g = ((k,method((values or keys)[i])) for i,k in enumerate(keys))
    return sorted(g) if sort else list(g)
__test__['kmap'] = [
  {'args':[str.lower,'BCA','YZX',False],'result':[('A', 'x'), ('B', 'y'), ('C', 'z')]}
]
        
def splitList(seq,split):
    """splits a list in lists of 'split' size"""
    #return [seq[split*i:split*(i+1)] for i in range(1+len(seq)/split)]
    return [seq[i:i+split] for i in range(len(seq))[::split]]
    
def contains(a,b,regexp=True):
    """ Returns a in b; using a as regular expression if wanted """
    return inCl(a,b,regexp)

def anyone(seq,method=bool):
    """Returns first that is true or last that is false"""
    if not seq: return False
    s = None
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
  
def setlocal(key,value):
    setitem(locals(),key,value)

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
        return [s for s in seq if anyone(matchCl(e,s) for e in exprs)]
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
    
def matchMap(mapping,key,regexp=True,default=Exception):
    """ from a mapping type (dict or tuples list) with strings as keys it returns the value from the matched key or raises KeyError exception """
    if not mapping: 
      if default is not Exception:
        return default
      raise ValueError('mapping')    
    if hasattr(mapping,'items'): mapping = mapping.items()
    if not isSequence(mapping) or not isSequence(mapping[0]): raise TypeError('dict or tuplelist required')
    if not isString(key): key = str(key)
    
    for tag,value in mapping:
        if (matchCl(tag,key) if regexp else (key in tag)):
            return value
    if default is not Exception:
      return default
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
        if regexp:
            return any(matchCl(exp,s) for s in seq)
        else:
            return any(exp.lower()==s.lower() for s in seq)
    else:
        return exp in seq
    
def matchCl(exp,seq,terminate=False,extend=False):
    """ Returns a caseless match between expression and given string """
    if extend:
        if '&' in exp:
            return all(matchCl(e.strip(),seq,terminate=False,extend=True) for e in exp.split('&'))
        if exp.startswith('!'):
            return not matchCl(exp[1:],seq,terminate,extend=True) 
    return re.match(toRegexp(exp.lower(),terminate=terminate),seq.lower())
clmatch = matchCl #For backward compatibility

def searchCl(exp,seq,terminate=False,extend=False):
    """ Returns a caseless regular expression search between expression and given string """
    if extend:
        if '&' in exp:
            return all(searchCl(e.strip(),seq,terminate=False,extend=True) for e in exp.split('&'))
        if exp.startswith('!'):
            return not searchCl(exp[1:],seq,terminate,extend=True)
    return re.search(toRegexp(exp.lower(),terminate=terminate),seq.lower())
clsearch = searchCl #For backward compatibility

def replaceCl(exp,repl,seq,regexp=True,lower=False):
    """ 
    Replaces caseless expression exp by repl in string seq 
    repl can be string or callable(matchobj) ; to reuse matchobj.group(x) if needed in the replacement string
    lower argument controls whether replaced string should be always lower case or not
    """
    if lower and hasattr(repl,'lower'):
      repl = repl.lower()
    if regexp:
      r,s = '',1
      while s:
        s = searchCl(exp,seq)
        if s:
          r+=seq[:s.start()]+repl
          seq=seq[s.end():]
      return r+seq
    else:
      return seq.lower().replace(exp.lower(),repl)
    
clsub = replaceCl

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

def toCl(exp,terminate=False,wildcards=('*',' '),lower=True):
    """ Replaces * by .* and ? by . in the given expression. 
    """
    ## @PROTECTED: DO NOT MODIFY THIS METHOD, MANY, MANY APPS DEPEND ON IT
    exp = str(exp).strip()
    if lower: exp = exp.lower()
    if not any(s in exp for s in ('.*','\*',']*')):
        for w in wildcards:
            exp = exp.replace(w,'.*')
    if terminate and not exp.strip().endswith('$'): exp += '$'
    exp = exp.replace('(?p<','(?P<') #Preventing missing P<name> clausses
    return exp
    
def toRegexp(exp,terminate=False):
    """ Case sensitive version of the previous one, for backwards compatibility """
    return toCl(exp,terminate,wildcards=('*',),lower=False)
    
def filtersmart(seq,filters):
    """
    filtersmart(sequence,filters=['any_filter','+all_filter','!neg_filter'])
    
    appies a list of filters to a sequence of strings, 
    behavior of filters depends on first filter character:
        '[a-zA-Z0-9] : an individual filter matches all strings that contain it, one matching filter is enough
        '!' : negate, discards all matching values
        '+' : complementary, it must match all complementaries and at least a 'normal filter' to be valid
        '^' : matches string since the beginning (startswith instead of contains)
        '$' : matches the end of strings
    """
    seq = seq if isSequence(seq) else (seq,)
    filters = filters if isSequence(filters) else (filters,)
    raw,comp,neg = [],[],[]
    def parse(s):
        s = toRegexp(s)
        if '*' not in s:
            if not s.startswith('^'): s='.*'+s
            if not s.startswith('$'): s=s+'.*'
        return s
    for f in filters:
        if f.startswith('+'): comp.append(parse(f[1:]))
        elif f.startswith('!'): neg.append(parse(f[1:]))
        else: raw.append(parse(f))
    return [s for s in seq if (not any(matchCl(n,s) for n in neg)) and any(matchCl(r,s) for r in raw) and (not comp or all(matchCl(c,s) for c in comp))]

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

reint = '[0-9]+'
refloat = '[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?'
        
def isString(seq):
    if isinstance(seq,basestring): return True # It matches most python str-like classes
    if any(s in str(type(seq)).lower() for s in ('vector','array','list',)): return False
    if 'qstring' == str(type(seq)).lower(): return True # It matches QString
    return False

WILDCARDS = '^$*+?{[]\|()' #r'
def isRegexp(seq,wildcards=WILDCARDS):
    """ This function is just a hint, use it with care. """
    return anyone(c in wildcards for c in seq)
    
def isNumber(seq):
    #return operator.isNumberType(seq)
    if isinstance(seq,bool): return False
    try: 
        float(seq)
        return True
    except: return False
    
NaN = float('nan')
    
def isNaN(seq):
    return isinstance(seq,(int,float)) and math.isnan(seq) or (isString(seq) and seq.lower().strip() == 'nan')
    
def isNone(seq):
    return seq is None or (isString(seq) and seq.lower().strip() in ('none','null','nan',''))

def isFalse(seq):
    return not seq or str(seq).lower().strip() in ('false','0','no')

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
    try:
        if seq and isSequence(seq) and isSequence(seq[0]):
            if seq[0] and not isSequence(seq[0][0]): return True #First element of tuple must be hashable
    except: pass
    return False
isMapping = isDictionary

def isIterable(seq):
    """ It includes dicts and listlikes but not strings """
    return hasattr(seq,'__iter__') and not isString(seq)

def isNested(seq,strict=False):
    if not isIterable(seq) or not len(seq): return False
    child = seq[0] if isSequence(seq) else seq.values()[0]
    if not strict and isIterable(child): return True
    if any(all(map(f,(seq,child))) for f in (isSequence,isDictionary)): return True
    return False
    
def isBool(seq,is_zero=True):
    codes = ['true','yes','false','no']
    if is_zero: codes+=['0','1']
    if seq in (True,False):
        return True
    elif isString(seq):
        return seq.lower() in codes #none/nan will not be considered boolean
    else:
        return False
    
def isDate(seq):
    try:
        return str2time(seq)
    except:
        return False

###############################################################################

def str2int(seq):
    """ It returns the first integer encountered in the string """
    return int(re.search(reint,seq).group())

def str2float(seq):
    """ It returns the first float (x.ye-z) encountered in the string """
    return float(re.search(refloat,seq).group())

def str2bool(seq):
    """ It parses true/yes/no/false/1/0 as booleans """
    return seq.lower().strip() not in ('false','0','none','no')

def str2type(seq,use_eval=True,sep_exp='(,;\ ]+'):
    """ 
    Tries to convert string to an standard python type.
    If use_eval is True, then it tries to evaluate as code.
    Lines separated by sep_exp will be automatically split
    """
    seq = str(seq).strip()
    m = sep_exp and (seq[0] not in '{[(') and re.search(sep_exp,seq)
    if m:
        return [str2type(s,use_eval) for s in str2list(seq,m.group())]
    elif isBool(seq,is_zero=False):
        return str2bool(seq)
    elif use_eval:
        try:
            return eval(seq)
        except:
            return seq
    elif isNumber(seq):
        return str2float(seq)
    else:
        return seq
    
def doc2str(obj):
    return obj.__name__+'\n\n'+obj.__doc__
   
def rtf2plain(t,e='[<][^>]*[>]'):
    t = re.sub(e,'',t)
    if re.search(e,t):
        return rtf2plain(t,e)
    else:
        return t
       
def html2text(txt):
    return rtf2plain(txt)
  
def dict2json(dct,filename=None,throw=False,recursive=True,encoding='latin-1'):
    """
    It will check that all objects in dict are serializable.
    If throw is False, a corrected dictionary will be returned.
    If filename is given, dict will be saved as a .json file.
    """
    import json
    result = {}
    for k,v in dct.items():
        try:
            json.dumps(v,encoding=encoding)
            result[k] = v
        except Exception,e:
            if throw: raise e
            if isString(v): result[k] = ''
            elif isSequence(v):
                try:
                    result[k] = toList(v)
                    json.dumps(result[k])
                except:
                    result[k] = []
            elif isMapping(v) and recursive:
                result[k] = dict2json(v,None,False,True,encoding=encoding)
    if filename:
        json.dump(result,open(filename,'w'),encoding=encoding)
    return result if not filename else filename
    
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

def toString(val):
    if hasattr(val,'text'):
        try: return val.text()
        except: return val.text(0)
    else:
        return str(val)

def toStringList(seq):
    return map(toString,seq)

def str2list(s,separator='',regexp=False,sep_offset=0): 
    """ Arguments allow to split by regexp and to keep or not the separator character 
    sep_offset = 0 : do not keep
    sep_offset = -1 : keep with posterior
    sep_offset = 1 : keep with precedent
    """
    if not regexp:
      return map(str.strip,s.split(separator) if separator else s.split())
    elif not sep_offset:
      return map(str.strip,re.split(separator,s) if separator else re.split('[\ \\n]',s))
    else:
      r,seps,m = [],[],1
      while m:
        m = clsearch(separator,s)
        if m:
          r.append(s[:m.start()])
          seps.append(s[m.start():m.end()])
          s = s[m.end():]
      r.append(s)
      for i,p in enumerate(seps):
        if sep_offset<0: r[i]+=p
        else: r[i+1] = p+r[i+1]
      return r
    
def code2atoms(code):
    begin = '[\[\(\{]'
    end = '[\]\)\}]'
    #ops = '[,]'
    l0 = str2list(code,begin,1,1)
    l0 = filter(bool,map(str.strip,l0))
    l1 = [a for l in l0 for a in str2list(l,end,1,-1)]
    l1 = filter(bool,map(str.strip,l1))
    #l2 = [a for l in l1 for a in str2list(l,ops,1,-1)]
    return l1
    

def text2list(s,separator='\n'):
    return filter(bool,str2list(s,separator))

def str2lines(s,length=80,separator='\n'):
    return separator.join(s[i:i+length] for i in range(0,len(s),length))

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

def char2int(c): 
    """ord(c)"""
    return ord(c)
def int2char(n): 
    """unichr(n)"""
    return unichr(n)
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
    """Converts an integer to a binary represented as a boolean array"""
    result,dec = [],int(dec)
    for i in range(N):
        result.append(bool(dec % 2))
        dec = dec >> 1
    return result

def bool2int(seq):
    """ Converts a boolean array to an unsigned integer """
    return fandango.bin2unsigned(''.join(map(str,map(int,reversed(seq)))))

########################################################################
## Time conversion
########################################################################

END_OF_TIME = 1024*1024*1024*2-1 #Jan 19 04:14:07 2038
TIME_UNITS = {'ns':1e-9,'us':1e-6,'ms':1e-3,'':1,'s':1,'m':60, 'h':3600,'d':86.4e3,'w':604.8e3,'y':31.536e6}
RAW_TIME = '^([+-]?[0-9]+[.]?(?:[0-9]+)?)(?: )?(%s)$'%'|'.join(TIME_UNITS) # e.g. 3600.5 s

def now():
    return time.time()

def time2tuple(epoch=None):
    if epoch is None: epoch = now()
    elif epoch<0: epoch = now()-epoch
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
    elif epoch<0: epoch = now()-epoch
    return datetime.datetime.fromtimestamp(epoch)

def time2str(epoch=None,cad='%Y-%m-%d %H:%M:%S'):
    if epoch is None: epoch = now() 
    elif epoch<0: epoch = now()-epoch
    return time.strftime(cad,time2tuple(epoch))
epoch2str = time2str
    
def str2time(seq='',cad=''):
    """ 
    :param seq: Date must be in ((Y-m-d|d/m/Y) (H:M[:S]?)) format or -N [d/m/y/s/h]
    
    See RAW_TIME and TIME_UNITS to see the units used for pattern matching.
    
    The conversion itself is done by time.strptime method.
    
    :param cad: You can pass a custom time format
    """
    if seq in (None,''): return time.time()
    seq = str(seq).strip()
    m = re.match(RAW_TIME,seq) 
    if m:
        #Converting from a time(unit) format
        value,unit = m.groups()
        try: return float(value)*TIME_UNITS[unit]
        except: raise Exception('PARAMS_ERROR','time format cannot be parsed!: %s'%seq)
    else:
        #Converting from a date format
        t,ms = None,re.match('.*(\.[0-9]+)$',seq) #Splitting the decimal part
        if ms: ms,seq = float(ms.groups()[0]),seq.replace(ms.groups()[0],'')
        else: ms = 0
        time_fmts = ([cad] if cad else [None]+
            [('%s%s%s'%(date.replace('-',dash),separator if hour else '',hour)) 
            for date in ('%Y-%m-%d','%y-%m-%d','%d-%m-%Y','%d-%m-%y','%m-%d-%Y','%m-%d-%y')
            for dash in ('-','/')
            for separator in (' ','T')
            for hour in ('%H:%M','%H:%M:%S','')
            ])
        for tf in time_fmts:
            try:
                tf = (tf,) if tf else () #tf=None will try default system format
                t = time.strptime(seq,*tf)
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

def ifThen(condition,callback,falsables=tuple()):
    """
    This function allows to execute a callable on an object only if it has a valid value.
    ifThen(value,callable) will return callable(value) only if value is not in falsables.
    
    It is a List-like method, it can be combined with fandango.excepts.trial
    """
    if condition not in falsables:
        if not isSequence(callback):
          return callback(condition)
        else:
          return ifThen(callback[0](condition),callback[1:],falsables)
    else:
        return condition

def retry(callable,retries=3,pause=0,args=[],kwargs={}):
    r = None
    for i in range(retries):
        try:
            r = callable(*args,**kwargs)
            break
        except Exception,e:
            if i==(retries-1): raise e
            elif pause: time.sleep(pause)
    return r
  
def retried(retries=3,pause=0):
  """
  
  """
  def retrier(f):
    def retried_f(*args,**kwargs):
      return retry(f,retries=retries,pause=pause,args=args,kwargs=kwargs)
    return retried_f
  return retrier
    
def evalF(formula):
    """
    Returns a function that executes the formula passes as argument.
    The formula should use x,y,z as predefined arguments, or use args[..] array instead
    
    e.g.:
    map(evalF("x>2"),range(5)) : [False, False, False, True, True]
    
    It is optimized to be efficient (but still 50% slower than a pure lambda)
    """
    #return (lambda *args: eval(formula,locals={'args':args,'x':args[0],'y':args[1],'z':args[2]}))
    c = compile(formula,formula,'eval') #returning a lambda that evals a compiled code makes the method 500% faster
    return (lambda *args: eval(c,{'args':args,'x':args and args[0],'y':len(args)>1 and args[1],'z':len(args)>2 and args[2]}))

def testF(f,args=[],t=1.):
    args = toSequence(args)
    ct,t0 = 0,time.time()
    while time.time()<t0+5:
        f(*args)
        ct+=1
    return ct

def evalX(target,_locals=None,modules=None,instances=None,_trace=False,_exception=Exception):
    """
    evalX is an enhanced eval function capable of evaluating multiple types and import modules if needed.
    The _locals/modules/instances dictionaries WILL BE UPDATED with the result of the code! (if '=' or import are used)
    It is used by some fandango classes to send python code to remote threads; that will evaluate and return the values as pickle objects.
    
    target may be:
         - dictionary of built-in types (pickable): {'__target__':callable or method_name,'__args__':[],'__class_':'','__module':'','__class_args__':[]}
         - string to eval: eval('import $MODULE' or '$VAR=code()' or 'code()')
         - list if list[0] is callable: value = list[0](*list[1:]) 
         - callable: value = callable()
    """
    import imp,__builtin__
    
    # Only if immutable types are passed as arguments these dictionaries will be preserved.
    _locals = notNone(_locals,{})
    modules = notNone(modules,{})
    instances = notNone(instances,{})
    
    def import_module(module,reload=False):
        alias = module.split(' as ',1)[-1] if ' as ' in module else module
        module = module.split('import ',1)[-1].strip().split()[0]
        if reload or alias not in modules:
            if '.' not in module:
                modules[module] = imp.load_module(module,*imp.find_module(module))
            else:
                parent,child = module.rsplit('.',1)
                print parent
                mparent = import_module(parent)
                setattr(mparent,child,imp.load_module(module,*imp.find_module(child,mparent.__path__)))
                modules[module] = getattr(mparent,child)
            if alias: 
                modules[alias] = modules[module] 
                _locals[alias] = modules[alias]
        print '%s(%s) : %s' % (alias,module,modules[alias])
        return modules[alias]
        
    def get_instance(_module,_klass,_klass_args):
        if (_module,_klass,_klass_args) not in instances:
            instances[(_module,_klass,_klass_args)] = getattr(import_module(_module),klass)(*klass_args)
        return instances[(_module,_klass,_klass_args)]
    
    if 'import_module' not in _locals: _locals['import_module'] = lambda m: import_module(m,reload=True)
        
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
                    target = getattr(import_module(module),target)
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
            if target.startswith('import ') or ' import ' in target: 
                import_module(target) #Modules dictionary is updated here
                value = target
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
        if _trace: print('Out of evalX(%s): %s'%(target,value))
    return value
  
