#!/usr/bin/env python2.5
#############################################################################
##
## file :       arrays.py
##
## description : Module developed to manage CSV-like files and generic 2D arrays, using headers for columns
##
## project :     Tango Control System
##
## $Author: Sergi Rubio Manrique, srubio@cells.es $
##              Grid Class thanks to Kent Johnson kent37 at tds.net
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

import csv,sys,re,operator,traceback
import functional as fun
from fandango.dicts import SortedDict
try: import numpy as np
except: np = None

__all__ = ['Grid','CSVArray','tree2table']

#from excepts import *
#from ExceptionWrapper import *

__doc__ = """
h1. fandango.arrays module

h2. Array Decimation

It contains many decimation methods, the one used by taurustrend is filter_array; which averages data at some given time intervals

"""

###############################################################################

from fandango.functional import reldiff,absdiff,seqdiff
MAX_DATA_SIZE = 2*1024

def decimator(data,min_inc=.05,min_rel=None,max_size=MAX_DATA_SIZE,max_iter=1000):
    """
    @NOTE, this is intensive when focusing on size, filter_array is better if you want to keep the shape over time++89+77
    This size-focused decimator sequentially iterates until reducing the size of the array 
    """
    start,count = len(data),0
    while len(data)>max_size and count<max_iter:
        d = []
        for i,t in enumerate(data[:-1]):
            if not d or i>=(len(data)-2): d.append((t[0],t[1]))
            elif abs(t[1])<min_inc and xor(abs(d[-1][1])>min_inc,abs(data[i+1][1])>min_inc):
                d.append((t[0],0)) #zeroing
            elif abs(d[-1][1]-t[1])>min_inc or abs(t[1]-data[i+1][1])>min_inc:
                # if min_inc is not None else min_rel*max((d[-1][1],t[1],min_inc or min_rel))):
                d.append((t[0],t[1]))
        data = d
        min_inc = min_inc*1.5
        count += 1
    if count>=max_iter: print('Unable to decimate data!')
    print('\t[%d] -> [%d] in %d iterations, inc = %s'%(start,len(data),count,min_inc))
    return data
    
def decimate_custom(seq,cmp=None,pops=None,keeptime=3600*1.1):
    """ 
    @NOTE: Although faster, filter_array provides a better decimation for trends
    It will remove all values from a list that doesn't provide information.
    In a set of X consecutive identical values it will remove all except the first and the last.
    A custom compare method can be passed as argument
    :param seq: a list of (timestamp,value) values
    """
    if len(seq)<3: return seq
    if len(seq[0])<2: return seq
    import __builtin__
    cmp = cmp or __builtin__.cmp
    pops = pops if pops is not None else []
    while pops: pops.pop() 
    x0,x1,x2 = seq[0],seq[1],seq[2]
    
    for i in range(len(seq)-2):
        #if (seq[i+2][0]-seq[i][0])<keeptime and not cmp(seq[i][1],seq[i+1][1]) and not cmp(seq[i+1][1],seq[i+2][1]):
        if not cmp(x0[1],seq[i+1][1]) and not cmp(seq[i+1][1],seq[i+2][1]):
            pops.append(i+1)
        else: x0 = seq[i+1]
    for i in reversed(pops):
        seq.pop(i)
    return seq

def decimate_array(data,fixed_size=0,keep_nones=True,fixed_inc=0,fixed_rate=0,fixed_time=0,logger=None):
    """ 
    @NOTE: filter_array provides a better decimation for trends
    Decimates a [(time,numeric value)] buffer by size/rate/increment/time
    Repeated values are always decimated.
    keep_nones forces value-to-None steps to be kept
    fixed_size: smaller increments of data will be pruned until fitting in a fixed_size array
    fixed_inc: keeps all values with an absolute increment above fixed_inc; overrides fixed_size
    fixed_step keeps some random values by order, overrides fixed_inc and fixed_size
    fixed_time keeps some time-fixed values; it takes preference over the rest
    """
    
    t0 = time.time()
    if hasattr(data[0],'value'):
        get_value = lambda v: v.value
        get_time = lambda t: hasattr(t.time,'tv_sec') and (t.time.tv_sec+1e-6*t.time.tv_usec) or t.time
    else:
        get_value = lambda t: t[1]
        get_time = lambda t: t[0]

    last,last_slope,buff,nones,fixed = data[0],0,[],[],[0,len(data)-1]
    for i in range(1,len(data)-1):
        #v is the data to check, using previous and later values
        u,v,w = get_value(data[i-1]),get_value(data[i]),get_value(data[i+1])
        if u == v == w: continue
        if fixed_time and max((get_time(data[i])-get_time(data[i-1]),get_time(data[i])-get_time(last)))>=fixed_time:
            fixed.append(i)
            last = data[i]
        elif None not in (u,v,w): 
            if fixed_rate and not i%fixed_rate: 
                fixed.append(i) #It would help to keep shape around slowly changing curves (e.g. parabollic)
                last = data[i]
            elif fixed_inc or fixed_size:
                slope = (u-v)>0
                if slope!=last_slope:
                    last_slope,last = slope,data[i]
                diff = max((abs(u-v),abs(w-v),abs(get_value(last)-v)))
                if fixed_inc and diff>fixed_inc: 
                    fixed.append(i)
                    last = data[i]
                else: 
                    buff.append((diff,i))
                    last = data[i]
            else:
                fixed.append(i)
                last = data[i]
        elif keep_nones:
            if v is None:
                #Double "if" is not trivial!
                if (u is not None or w is not None): 
                    nones.append(i)
                    last = data[i]
            #value-to-None-to-value steps
            elif u is None or w is None: 
                fixed.append(i)
                last = data[i]
    if fixed_size: 
        bsize = int(fixed_size-len(nones)-len(fixed))
        buff = [t[1] for t in sorted(buff)[-bsize:]]
    else:
        buff = [] #[t[1] for t in buff]
    new_data = [data[i] for i in sorted(buff+nones+fixed)]
    if logger: logger.debug('data[%d] -> buff[%d],nones[%d],fixed[%d]; %f seconds'%(
            len(data),len(buff),len(nones),len(fixed),(time.time()-t0)))
    return new_data
    
###############################################################################
# The filter_array method and its associated functions


F_LAST = 0 #fill with last value
F_AVG = 1 #fill with average
F_NONE = 2 #fill with nones
F_INT = 3 #linear interpolation
F_ZERO = 4 #fill with zeroes
F_NEXT = 5 #fill with next value

# For all this methos arguments may be just values sequence or currentsequence / previousvalue

def average(*args):
    return fun.avg(args[0])

def rms_value(*args):
    return fun.rms(args[0])

def maxdiff(*args):
    """ Filter that maximizes changes (therefore, noise) """
    seq,ref = args
    if None in seq: return None
    try:
        return sorted((fun.absdiff(s,ref),s) for s in seq)[-1][-1]
    except Exception,e:
        print args
        raise e

def notnone(*args):
    seq,ref,method = args[0],fun.first(args[1:] or [0]),fun.first(args[2:] or [average])
    print 'notnone from %s'%ref
    try:
      if np: return method(*((v for v in seq if v is not None and not np.isnan(v)),ref))
      else: return method(*((v for v in seq if v is not None),ref))
    except:
      traceback.print_exc()
      return ref

def maxmin(*args):
    """ 
    Returns timed ((t,max),(t,min)) values from a (t,v) dataset 
    When used to filter an array the winndow will have to be doubled to allocate both values (or just keep the one with max absdiff from previous).
    """
    data = args[0]
    t = sorted((v,t) for t,v in data)
    mn,mx = (t[0][1],t[0][0]),(t[-1][1],t[-1][0])
    return mx,mn

##METHODS OBTAINED FROM PyTangoArchiving READER

def choose_first_value(v,w,t=0,tmin=-300):
    """ 
    Args are v,w for values and t for point to calcullate; 
    tmin is the min epoch to be considered valid
    """  
    r = (0,None)
    t = t or max((v[0],w[0]))
    if tmin<0: tmin = t+tmin
    if not v[0] or v[0]<w[0]: r = v #V chosen if V.time is smaller
    elif not w[0] or w[0]<v[0]: r = w #W chosen if W.time is smaller
    if tmin>0 and r[0]<tmin: r = (r[0],None) #If t<tmin; value returned is None
    return (t,r[1])

def choose_last_value(v,w,t=0,tmin=-300):
    """ 
    Args are v,w for values and t for point to calcullate; 
    tmin is the min epoch to be considered valid
    """  
    r = (0,None)
    t = t or max((v[0],w[0]))
    if tmin<0: tmin = t+tmin
    if not w[0] or v[0]>w[0]: r = v #V chosen if V.time is bigger
    elif not v[0] or w[0]>v[0]: r = w #W chosen if W.time is bigger
    if tmin>0 and r[0]<tmin: r = (r[0],None) #If t<tmin; value returned is None
    return (t,r[1])
    
def choose_max_value(v,w,t=0,tmin=-300):
    """ 
    Args are v,w for values and t for point to calcullate; 
    tmin is the min epoch to be considered valid
    """  
    r = (0,None)
    t = t or max((v[0],w[0]))
    if tmin<0: tmin = t+tmin
    if tmin>0:
        if v[0]<tmin: v = (0,None)
        if w[0]<tmin: w = (0,None)
    if not w[0] or v[1]>w[1]: r = v
    elif not v[0] or w[1]>v[1]: r = w
    return (t,r[1])
    
def choose_last_max_value(v,w,t=0,tmin=-300):
    """ 
    This method returns max value for epochs out of interval
    For epochs in interval, it returns latest
    Args are v,w for values and t for point to calcullate; 
    tmin is the min epoch to be considered valid
    """  
    if t>max((v[0],w[0])): return choose_max_value(v,w,t,tmin)
    else: return choose_last_value(v,w,t,tmin)

import math
from math import log10

def logroof(x):
    m = math.floor(log10(x))
    i = float(x)/10**m
    v = (v for v,k in ((1,i<1),(2,i<2),(5,i<5),(10,True)) if k).next()
    return v*(10**m)

def logfloor(x):
    m = math.floor(log10(x))
    i = float(x)/10**m
    v = (v for v,k in ((0.1,i<1),(1,i<2),(2,i<5),(5,True)) if k).next()
    return v*(10**m)

def get_max_step(data,index=False):
    import numpy
    vs = numpy.array(data)
    diff = vs[1:]-vs[:-1]
    mx = numpy.nanmax(diff)
    if not index:
        return mx
    else: #Return at which position the step was found
        ix =1+numpy.where(diff==mx)[0][0]
        return (ix,mx)

def get_histogram(data,n=20,log=False):
    """ Groups data in N steps """
    import math
    mn = logfloor(min(data))
    mx = logroof(max(data))
    print('data=[%e:%e],ranges=[%e:%e]'%(min(data),max(data),mn,mx))
    if log: mn,mx = log10(mn),log10(mx)
    step = float(mx-mn)/n
    print('mn,mx,step = %s, %s, %s'%(mn,mx,step))
    ranges = []
    for i in range(n):     
        r0 = mn+i*step
        r1 = mn+(i+1)*step
        if log: r0,r1 = 10**r0,10**r1
        ranges.append((r0,len([d for d in data if r0<=d<r1])))
    return ranges

def print_histogram(data,n=20):
    """ Prints Groups of data in N steps """
    hist = get_histogram(data,n)
    total,mx = len(data),max(data)
    ranges = [min(data)]+[h[0] for h in hist[1:]]+[mx]
    for i,h in enumerate(hist):
        r = 100*float(h[1])/total
        print('%25s : %6s : %s'%(
            '%e < %e'%(ranges[i],ranges[i+1]),
            '%2.1f%%'%r,
            ' *'*(1+int(r/10.))
            ))

def filter_array(data,window=300,method=average,begin=0,end=0,filling=F_LAST,trace=False):
    """
    The array returned will contain @method applied to @data split in @window intervals
    First interval will be floor(data[0][0],window)+window, containing average of data[t0:t0+window]
    If begin,end intervals are passed, cut-off and filling methods are applied
    The value at floor(time) is the value that closes each interval
    
    IF YOUR DATA SOURCE IS A PYTHON LIST; THIS METHOD IS AS FAST AS NUMPY CAN BE 
    (crosschecked with 1e6 samples against the PyTangoArchiving.utils.decimate_array method using numpy)
    """
    data = sorted(data) #DATA MUST BE ALWAYS SORTED
    tfloor = lambda x: int(fun.floor(x,window))
    begin,end,window = map(int,((begin,end,window)))
    
    #CUT-OFF; removing data out of interval    
    #--------------------------------------------------------------------------
    if not data or (begin and begin>data[-1][0]) or (end and end<data[0][0]): 
        return []
    #Using loop instead of list comprehension (50% faster with normally-sorted data than list comprehensions)
    prev,post = None,None
    if begin and data and data[0][0]<begin:
        if data[-1][0]<begin: 
            prev,data = data[-1],[]
        else: 
            i = (i for i,v in enumerate(data) if v[0]>=begin).next()-1
            prev,data = data[i],data[i+1:]
    if end and data and data[-1][0]>end:
        if data[0][0]>end:
            post,data = data[0],[]
        else:
            j = (j for j,v in enumerate(data) if v[0]>end).next()
            post,data = data[j],data[:j]
    if trace: print 'prev,post: %s,%s'%(prev,post)
    
    if not data:
        if prev or post:
            nx = prev and prev[1] or post[1]
            return [(t,nx) for t in range(tfloor(begin)+window,end,window)]+[(tfloor(end)+window,post and post[1] or nx)]
        else: return []
    
    #Filling initial range with data
    #--------------------------------------------------------------------------
    if begin:
        nx =  prev and prev[1] or data[0][1]
        ndata = [(tt+window,nx) for tt in range(tfloor(begin),tfloor(data[0][0]),window)]
        if trace: print 'prev: %s'%str(ndata and ndata[-1])
    else: 
        ndata =[]
    
    #Inserting averaged data
    #--------------------------------------------------------------------------
    i,i0 = 0,0
    next = []
    ilast = len(data)-1
    if trace: print 't0: %s' % (window+tfloor(data[0][0]-1))
    try:
        for t in range(window+tfloor(data[0][0]-1),1+window+tfloor(max((end,data[-1][0]))),window):
            if i<=ilast:
                if data[i][0]>t:
                    #Filling "whitespace" with last data
                    nx = (
                        (filling==F_LAST and ndata and ndata[-1][1]) or
                        (filling==F_NONE and None) or
                        (filling==F_ZERO and 0) or
                        None)
                    ndata.append((t,nx))
                    #print 'whitespace: %s'%str(ndata[-1])
                else:
                    #Averaging data within interval
                    i0 = i
                    while i<=ilast and data[i][0]<=t: i+=1
                    #val = method([v[1] for v in data[i0:i]],ndata and ndata[-1][-1] or 0)
                    a1 = list(v[1] for v in data[i0:i])
                    a2 = ndata and ndata[-1][-1] or 0
                    val = method(a1,a2)
                    ndata.append((t,val))
                    #print '%s-%s = [%s:%s] = %s'%(t-window,t,i0,i,ndata[-1])
            else:
                #Adding data at the end, it will be applied whenever the size of array is smaller than expected value
                if ndata: nx = ndata[-1][1]
                else: nx = None
                ndata.append((t,nx))
                #print 'post: %s'%str(ndata[-1])
    except Exception,e:
        print i0,'-',i,'/',ilast,':',filling,':',data[i0:i]
        print ndata and ndata[-1] 
        print ndata and ndata[-1] and ndata[-1][-1]
        raise Exception(traceback.format_exc())
    return ndata
    
###############################################################################

def dict2array(dct):
    """ Converts a dictionary in a table showing nested data, lists are unnested columns """
    data,table = {},[]
    data['nrows'],data['ncols'] = 0,2 if fun.isDictionary(dct) else 1
    def expand(d,level):#,nrows=nrows,ncols=ncols):
        #self.debug('\texpand(%s(%s),%s)'%(type(d),d,level))
        for k,v in sorted(d.items() if hasattr(d,'items') else d):
            zero = data['nrows']
            data[(data['nrows'],level)] = k
            if fun.isDictionary(v): 
                data['ncols']+=1
                expand(v,level+1)
            else:
                if not fun.isSequence(v): v = [v]
                for t in v:
                    data[(data['nrows'],level+1)] = t
                    data['nrows']+=1
            #for i in range(zero+1,nrows): data[(i,level)] = None
    expand(dct,0)
    [table.append([]) for r in range(data.pop('nrows'))]
    [table[r].append(None) for c in range(data.pop('ncols')) for r in range(len(table))]
    for coord,value in data.items(): table[coord[0]][coord[1]] = value
    return table

def array2dict(table):
    """ Converts a table in a dictionary of left-to-right nested data, unnested columns are lists"""
    nrows,ncols = len(table),len(table[0])
    r,c = 0,0
    def expand(r,c,end):
        #self.debug('expand(%s,%s,%s)'%(r,c,end))
        i0,t0 = r,table[r][c]
        if t0 is None: return None
        if c+1<ncols and table[r][c+1]:
            d = SortedDict()
            keys = []
            new_end = r+1
            for i in range(r+1,end+1):
                t = table[i][c] if i<end else None
                if t or i>=end: 
                    keys.append((i0,t0,new_end)) #start,name,stop for each key
                    t0,i0 = t,i
                new_end = i+1
            for i,key,new_end in keys:
                d[key] = expand(i,c+1,new_end)
            #self.debug('expand(%s to %s,%s): %s'%(r,end,c,d))
            return d
        else:
            d = [table[i][c] for i in range(r,end)]
            #self.debug('expand(%s to %s,%s): %s'%(r,end,c,d))
            return d
    data = expand(0,0,nrows)
    return data

def tree2table(tree):
    """
    tree2table is different from dict2array, because allows list=row instead list=column
    {A:{AA:{1:{}},AB:{2:{}}},B:{BA:{3:{}},BB:{4:{}}}}
    should be represented like
    A    AA 1
        AB    2
    B    BA 3
        BB    4
    """
    from collections import deque
    if not isinstance(tree,dict): #The tree arrived to a leave
        if any(map(isinstance,2*[tree],(list,tuple))): return [tree]
        else: return [(tree,)]
    result = []
    for k in sorted(tree.keys()): #K=AA; v = {1:{}}
        v = tree[k]
        #print '%s:%s' % (k,v)
        if not v:
            #print '%s is empty' % k
            result.append([k])
        else:
            _lines = tree2table(v)
            #print 'tree2table(%s): tree2table(v) returned: %s' % (k,_lines)
            lines = [deque(dq) for dq in _lines]
            lines[0].appendleft(k)
            [line.appendleft('') for line in lines[1:]]
            [result.append(list(line)) for line in lines]
    #print 'result: tree2table(tree) returned: %s' % (result)
    return result

def values2text(table,order=None,sep='\t',eof='\n',header=True):
    """ 
    Input is a dictionary of {variable:[(time,values)]}; it will convert the dictionary into a text table with a column for each variable
    It assumes that values in diferent columns have been already correlated
    """
    start = time.time()
    if not order or not all(k in order for k in table): keys = list(sorted(table.keys()))
    else: keys = sorted(table.keys(),key=order.index)
    value_to_text = lambda s: str(s).replace('None','').replace('[','').replace(']','')
    is_timed = fun.isSequence(table.values()[0][0]) and len(table.values()[0][0])==2
    csv = '' if not header else (sep.join((['date','time'] if is_timed else [])+keys)+eof)
    for i,t in enumerate(table.values()[0]):
        if is_timed:
            row = [fun.time2str(t[0]),str(t[0])]+[value_to_text(table[k][i][-1]) for k in keys]
        else:
            row = [value_to_text(table[k][i]) for k in keys]
        csv+=sep.join(row) + eof
    #print('Text file generated in %d milliseconds'%(1000*(time.time()-start)))
    return csv
        
def correlate_values(values,stop=None,resolution=None,debug=False,rule=None,AUTO_SIZE=50000,MAX_SIZE=0,MIN_RESOLUTION=0.05):
    ''' Correlates values to have all epochs in all columns
    :param values:  {curve_name:[values]}
    :param resolution: two epochs with difference smaller than resolution will be considered equal
    :param stop: an end date for correlation
    :param rule: a method(tupleA,tupleB,epoch) like (min,max,median,average,last,etc...) that will take two last column (t,value) tuples and time and will return the tuple to keep
    '''
    start = time.time()
    #print('correlate_values(%d x %d,resolution=%s,MAX_SIZE=%d) started at %s'%(len(values),max(len(v) for v in values.values()),resolution,MAX_SIZE,time.ctime(start)))
    stop = stop or start
    keys = sorted(values.keys())
    table = dict((k,list()) for k in keys)
    index = dict((k,0) for k in keys)
    lasts = dict((k,(0,None)) for k in keys)
    first,last = min([t[0][0] if t else 1e12 for t in values.values()]),max([t[-1][0] if t else 0 for t in values.values()])
    if resolution is None:
        #Avg: aproximated time resolution of each row
        avg = (last-first)/min((AUTO_SIZE/6,max(len(v) for v in values.values()) or 1))
        if avg < 10: resolution = 1
        elif 10 <= avg<60: resolution = 10
        elif 60 <= avg<600: resolution = 60
        elif 600 <= avg<3600: resolution = 600
        else: resolution = 3600 #defaults
        print('correlate_values(...) resolution set to %2.3f -> %d s'%(avg,resolution))
    assert resolution>MIN_RESOLUTION, 'Resolution must be > %s'%MIN_RESOLUTION
    if rule is None: rule = fun.partial(choose_first_value,tmin=-resolution*10)
    #if rule is None: rule = fun.partial(choose_last_max_value,tmin=-resolution*10)
    epochs = range(int(first*1000-resolution*1000),int(last*1000+resolution*1000),int(resolution*1000)) #Ranges in milliseconds
    if MAX_SIZE: epochs = epochs[:MAX_SIZE]
    for k,data in values.items():
        #print('Correlating %s->%s values from %s'%(len(data),len(epochs),k))
        i,v,end = 0,data[0] if data else (first,None),data[-1][0] if data else (last,None)
        for t in epochs:
            t = t*1e-3 #Correcting back to seconds
            v,tt = None,t+resolution
            #Inserted value will  be (<end of interval>,<correlated value>)
            #The idea is that if there's a value in the interval, it is chosen
            #If there's no value, then it will be generated using previous/next values
            #If there's no next or previous then value will be None
            #NOTE: Already tried a lot of optimization, reducing number of IFs doesn't improve
            #Only could guess if iterating through values could be better than iterating times
            if i<len(data):
                for r in data[i:]:
                    if r[0]>(tt):
                        if v is None: #No value in the interval
                            if not table[k]: v = (t,None)
                            else: v = rule(*[table[k][-1],r,tt]) #Generating value from previous/next
                        break
                    #therefore, r[0]<=(t+resolution)
                    else: i,v = i+1,(t,r[1])
                    ## A more ellaborated election (e.g. to maximize change)
                    #elif v is None: 
                        #i,v = i+1,(t,r[1])
                    #else:
                        #i,v = i+1,rule(*[v,r,tt])
            else: #Filling table with Nones
                v = (t+resolution,None)
            table[k].append((tt,v[1]))
        #print('\t%s values in table'%(len(table[k])))
    #print('Values correlated in %d milliseconds'%(1000*(time.time()-start)))
    return table
        
###############################################################################

class Grid(dict):
    """ Sat May 28 13:07:53 CEST 2005
    You caught me in a good mood this morning. I woke to sunshine for the first time in
    many days, that
    might have something to do with it :-)
    Here is a dict subclass that extends __getitem__ and __setitem__ to allow setting
    an entire row. I
    included extensive doctests to show you what it does.
    Note: you can write d['A',1] instead of d[('A',1)], which looks a little cleaner.
    Kent
    
    A two-dimensional array that can be accessed by row, by column, or by cell.
    Create with lists of row and column names plus any valid dict() constructorargs.
    >>> data = Grid( ['A', 'B'], [1, 2] )
    Row and column lists must not have any values in common.
    >>> data = Grid([1, 2], [2, 3])
    Traceback (most recent call last): ValueError: Row and column lists must not have any values in common
    """
    def __init__(self, rowNames, colNames, *args, **kwds):
        dict.__init__(self, *args, **kwds)
        self.rowNames = list(rowNames)
        self.colNames = list(colNames)
        # Check for no shared row and col names
        if set(rowNames).intersection(colNames):
            raise ValueError, 'Row and column lists must not have any values in common'
    def __getitem__(self, key):
        """
        Here is an example with data:
        >>> rowNames = ['A','B','C','D']
        >>> colNames = [1,'J']
        >>> rawData = [ 'cat', 3, object, 9, 4, [1], 5, 6 ]
        >>> indices = [ (row, col) for col in colNames for row in rowNames ]
        >>> data = Grid(rowNames, colNames, zip(indices, rawData))
        Data can be accessed by cell:
        >>> for i in indices:
        ...    print i, data[i]
        ('A', 1) cat
        ('B', 1) 3
        ('C', 1) <type 'object'>
        ('D', 1) 9
        ('A', 'J') 4
        ('B', 'J') [1]
        ('C', 'J') 5
        ('D', 'J') 6
        >>> data['B', 'J'] = 5
        Cell indices must contain valid row and column names:
        >>> data[3]
        Traceback (most recent call last):
        ...
        KeyError: 3
        >>> data['C', 2] = 5
        Traceback (most recent call last): ValueError: Invalid key or value: Grid[('C', 2)] = 5
        Data can be accessed by row or column index alone to set or retrieve
        an entire row or column:
        >>> print data['A']
        ['cat', 4]
        >>> print data[1]
        ['cat', 3, <type 'object'>, 9]
        >>> data['A'] = ['dog', 2]
        >>> print data['A']
        ['dog', 2]
        When setting a row or column, data must be the correct length.
        >>> data['A'] = ['dog']
        Traceback (most recent call last): ValueError: Invalid key or value: Grid['A'] = ['dog']
        """
        if self._isCellKey(key):
            return dict.__getitem__(self, key)
        elif key in self.rowNames:
            return [ dict.__getitem__(self, (key, col)) for col in self.colNames ]
        elif key in self.colNames:
            return [ dict.__getitem__(self, (row, key)) for row in self.rowNames ]
        else:
            raise KeyError, key
    def __setitem__(self, key, value):
        if self._isCellKey(key):
            return dict.__setitem__(self, key, value)
        elif key in self.rowNames and len(value) == len(self.colNames):
            for col, val in zip(self.colNames, value):
                dict.__setitem__(self, (key, col), val)
        elif key in self.colNames and len(value) == len(self.rowNames):
            for row, val in zip(self.rowNames, value):
                dict.__setitem__(self, (row, key), val)
        else:
            raise ValueError, 'Invalid key or value: Grid[%r] = %r' % (key, value)
    def _isCellKey(self, key):
        """ Is key a valid cell index? """
        return isinstance(key, tuple) \
            and len(key) == 2 \
            and key[0] in self.rowNames \
            and key[1] in self.colNames
if __name__ == '__main__':
    import doctest
    doctest.testmod()

class DictFile(object):
    """ 
    @TODO
    f = IndexedFile('/a/b/c.eps',offset=0,split=',;
    \t',escape='"',comment='#',skip=True or '',strip=True or '#.*',case=True)
    f.__getitem__(row,word=None)

    exclusion regexp!!

    ()!()
    """
    def __init__(self,):
        pass
    def get(self,row,word=None,split=True):
        """
        Should understand both int or string indexes
        
        For int, return row
        For str, return line that first word matches (strip key)
        Word = int, return word at column
        Word = regexp, return list with matching strings
        If both regexp, return all matchings in single list
        If both int, return single element
        """
        return None
    
    def __getitem__(self,i):
        """
        should support D[2,3] or D['A*','b*'] syntaxes?
        """
        return None #get(i)
    
    def sections(self,begin,end):
        """
        begin,end are regexps
        returns a dict with begins as keys and begin-end texts as values
        
        txt = 
         <data 1>
          da da da
         </data>
         <data 2>
          ...
         </data>
         
        returns {'<data 1>':'da da da','<data 2>':'...'}
        
        It should work for texts like:
        
        Header: bla
        Data: 
         da
         di
         do
        End:
        
        {'Header:':bla,'Data:':'da\ndi\ndo'}
        """
        return {}
    def changed(self):
        """
        return True if file changed from last loading
        """
        pass
    def update(self):
        """
        reload from file (if changed)
        """
        pass

import time

class TimedQueue(list):
    """ A FIFO that keeps all the values introduced at least for a given time.
    Applied to some device servers, to force States to be kept at least a minimum time.
    Previously named as device.StateQueue
    pop(): The value is removed only if delete_time has been reached.
    at least 1 value is always kept in the list
    """
    def __init__(self,arg=None):
        """ Initializes the list with a sequence or an initial value. """
        if arg is None:
            list.__init__(self)
        elif operator.isSequenceType(arg):
            list.__init__(self,arg)
        else:
            list.__init__(self)
            self.append(arg,1)
    def append(self,obj,keep=15):
        """ Inserts a tuple with (value,insert_time,delete_time=now+keep) """
        now=time.time()
        l=(obj,now,now+keep)
        list.append(self,l)
    def pop(self,index=0):
        """ Returns the indicated value, or the first one; but removes only if delete_time has been reached.
        All values are returned at least once.
        When the queue has only a value, it is not deleted.
        """
        if not self: return None #The list is empty
        now=time.time()
        s,t1,t2 = self[index]
        if now<t2 or len(self)==1:
            return s
        else:
            return list.pop(self,index)[0]
    def index(self,obj):
        for i in range(len(self)): 
            if self[i][0]==obj: return i
        return None
    def __contains__(self,obj):
        for t in self: 
            if t[0]==obj: return True
        return False
    pass


class CSVArray(object):
      
    def size(self):
        return (len(self.rows)-self.xoffset, len(self.cols)-self.yoffset)
    
    #@Catched
    def __init__(self,filename=None,header=None,labels=None,comment=None,offset=0,trace=False):
        """
        @param[in] filename file to load
        @param[in] header row to use as column headers
        @param[in] labels column to use as row labels
        """
        self.rows = []
        self.cols = []
        self.nrows = 0
        self.ncols = 0
        self.filename = None
        self.xoffset = offset
        self.yoffset = 0
        self.comment = comment
        self.dialect = None
        self.header = header
        self.labels = labels
        self.filename = filename
        self.trace = trace
        if filename is not None: self.load(filename)
        return
       
    def __str__(self):
        result = ''
        for row in self.rows:
            for n in range(self.ncols):
                result = result + str(row[n]) + ('\t' if n<self.ncols-1 else '\n')
        return result
            
    def __len__(self):
        return self.size()[0]
    
    def __iter__(self):
        return (self.get(i) for i in range(len(self)))
       
    #@Catched
    def load(self,filename,comment=None,delimiter=None,prune_empty_lines=True,filters=None):
        if not comment: comment=self.comment
        filters = filters or {} # filters={key:filter} Lines will be added only if columnName.lower()==key and re.match(filter,value.lower()); header line does not apply
        rows = [];cols = []; readed = []; header = self.header if self.header is not None else self.xoffset
        
        try:
            fl=open(filename)
            flines = fl.readlines()
            if not delimiter:
                index = header
                sample = flines[index]
                self.dialect = csv.Sniffer().sniff(sample)
                if self.trace: print 'Dialect extracted is %s'%(str(self.dialect.__dict__))
                readed = [r for r in csv.reader(flines, self.dialect)]
            else:
                readed = [ r for r in csv.reader(flines, delimiter=delimiter)]
                #readed = csv.reader(fl, delimiter='\t')
        except Exception,e:
            print 'Exception while reading %s: %s' % (filename,str(e))
        finally:
            try: fl.close()
            except: pass
        
        if readed:
            i,check = 0,True
            for row in readed:
                #Empty rows are avoided, Row is added only if not commented
                if ( (not prune_empty_lines)
                     or (   max([len(el) for el in row] or [0]) is not 0 and
                            (not comment or not str(row[0]).startswith(comment))
                        ) ):
                    row2 = [str(r).strip() for r in row] 
                    if i == header: 
                        headers = [s.lower() for s in row2]
                    elif i>header and filters: #In all rows excepting header it is checked that the filter is matched for any column in filters
                        check = all( (k not in headers or re.match(f,row2[headers.index(k)].lower()) ) for k,f in filters.items())
                    if i<=header or not filters or not rows or check:
                        rows.append(row2)                        
                #Correcting initial header and offset when previous lines are being erased
                else: #The row is discarded
                    if i<=self.header: 
                        self.header-=1
                    if i<self.xoffset: 
                        self.xoffset-=1
                i=i+1
            if self.trace: print 'Header line is %d: %s' % (len(rows[self.header]),rows[self.header])
            ncols = max(len(row) for row in rows) if rows else 0
            for i in range(len(rows)):
                while len(rows[i])<ncols:
                    rows[i].append('')#'\t')
    
            for i in range(ncols):
                #cols.append([(lambda x,i: x[i])(row,i) for row in rows]) 
                cols.append([str(row[i]).strip() for row in rows])

        del self.rows; del self.cols
        self.rows=rows;self.cols=cols; self.nrows=len(rows); self.ncols=len(cols)
        if self.trace: print 'CSVArray initialized as a ',self.nrows,'x',self.ncols,' matrix'
    
    #@Catched
    def save(self,filename=None):
        if filename is not None:
            self.filename=filename
        if self.filename is None:
            return
        fl = open(self.filename,'w')
        writer = csv.writer(fl,delimiter='\t')
        writer.writerows(self.rows);
        if self.trace: print 'CSVArray written as a ',self.nrows,'x',self.ncols,' matrix'
        fl.close()
        
    #@Catched
    def setOffset(self,x=0,y=0):
        self.xoffset=x; self.yoffset=y;
        
    #@Catched
    def resize(self, x, y):
        """def resize(self, x(rows), y(columns)):
        TODO: This method seems quite buggy, a refactoring should be done
        """
        if self.trace: print 'CSVArray.resize(',x,',',y,'), actual size is (%d,%d)' % (self.nrows,self.ncols)
        if len(self.rows)!=self.nrows: print 'The Size of the Array has been corrupted!'
        if len(self.cols)!=self.ncols: print 'The Size of the Array has been corrupted!'
        
        if x<self.nrows:
            #print 'Deleting %d rows' % (self.nrows-x)
            self.rows = self.rows[:x]
            for i in range(self.ncols):
                self.cols[i]=self.cols[i][0:x]  
        
        elif x>self.nrows:
            #print 'Adding %d new rows' % (x-self.nrows)
            for i in range(x-self.nrows):
                self.rows.append(y*[''])
            for i in range(self.ncols):
                self.cols[i]=self.cols[i]+['']*(x-self.nrows)
        self.nrows = x
        if len(self.rows)!=self.nrows: print 'The Size of the Array Rows has been corrupted!'
        
        if y<self.ncols:
            #print 'Deleting %d columns' % (self.ncols-y)
            self.cols = self.cols[:y]
            for i in range(self.nrows):
                self.rows[i]=self.rows[i][0:y]
        elif y>self.ncols:
            #print 'Adding %d new columns' % (y-self.ncols)
            for i in range(y-self.ncols):
                self.cols.append(x*[''])
            for i in range(self.nrows):
                self.rows[i]=self.rows[i] + (y-len(self.rows[i]))*['']
        self.ncols = y
        if len(self.cols)!=self.ncols: print 'The Size of the Array Columns has been corrupted!'
        
        if self.trace: print 'CSVArray.rows dimension is now ',len(self.rows),'x',max([len(r) for r in self.rows])
        if self.trace: print 'CSVArray.cols dimension is now ',len(self.cols),'x',max([len(c) for c in self.cols])
        return x,y
        
    ###########################################################################
    # Methods for addressing (get/set/etc)
    ###########################################################################
      
    #@Catched
    def get(self,x=None,y=None,head=None,row=None,column=None,distinct=False,xsubset=[],ysubset=[]):
        """
        def get(self,x=None,y=None,head=None,distinct=False):
        """
        result = []
        if x is None: x = row
        head = head or column
        #if isinstance(y,basestring): head=y
        if type(y)==type('y'): head,y = y,None
        if head: y = self.colByHead(head)

        ##Getting row/column/cell using 'axxis is None' as a degree of freedom
        if y is None: #Returning a row
            x = x or 0
            if self.trace: print 'Getting the row ',x
            result = self.rows[self.xoffset+x][self.yoffset:]
        elif x is None: #Returning a column
            if self.trace: print 'Getting the column ',y
            result = self.cols[self.yoffset+y][self.xoffset:]
        else: #Returning a single Cell
            result = self.rows[self.xoffset+x][self.yoffset+y]

        if self.trace and xsubset: print 'using xsubset ',xsubset
        if self.trace and ysubset: print 'using ysubset ',ysubset
        
        if not distinct: 
            #if getting a column and theres an xsubset ... prune the rows not in xsubset
            if x is None and xsubset: result = [result[i] for i in xsubset]
            if y is None and ysubset: result = [result[i] for i in ysubset]
            return result

        if self.trace: print 'Getting only distinct values from ',['%d:%s'%(i,result[i]) for i in range(len(result))]
        ## DISTINCT VALUES, returns a dictionary with the distinct values (initialized with first match)
        #values={result[0]:[0]} #Doesn't add self.xoffset here, it has been done before!
        values={}
        #for i in range(1,len(result)):
        for i in range(len(result)):
            #If we are returning a column, rows must be in the subset
            if x is None and xsubset and i not in xsubset: continue
            #If we are returning a row, columns must be in the subset
            if y is None and ysubset and i not in ysubset: continue
            if result[i] not in values.keys():
                values[result[i]]=[i]
            else:
                values[result[i]].append(i)
        if self.trace: print 'Values are ',values
        return values
    
    def getd(self,row):
        """This method returns a line as a dictionary using the headers as keys"""
        d = {}
        Hrow = self.rows[self.header or 0]
        line = self.get(x=row)
        for i in range(len(line)): d[Hrow[i]]=line[i]
        return d
    
    def Labeled(self,fun):
        def labelator(self,*args,**kwargs):
            return self.fun(*args,**kwargs)
        return labelator
    
    #@Labeled(self)
    def find(self,values):
        #Values is a dict that contains {Column:regexp,Column2:regexp2,...}
        #The command will return all the matching rows for all columns given
        pass
    
    #@Catched   
    def set(self,x,y,val):
        """
        def set(self,x,y,val):
        """
        if self.trace: print 'CSVArray.set(x=',x,',y=',y,',val=',val,',xoffset=',self.xoffset,',yoffset=',self.yoffset,')'
        val = val if type(val) in [int,long,float] else (val or '')
        if x is None or x<0:
           #Setting a column
           if len(val)>self.nrows or len(val)<0: 
               raise Exception('CSVArray.set(column) ... wrong size of column')
           for i,v in enumerate(val):
               self.cols[y][i]=v
               self.rows[i][y]=v;
        elif y is None or y<0:
            #Setting an entire row
            if len(val)>self.ncols or len(val)<0: 
                raise Exception('CSVArray.set(row) ... wrong size of row')           
            for i,v in enumerate(val):
               self.rows[x][i]=v
               self.cols[i][x]=v;             
        else:
            self.rows[self.xoffset+int(x)][self.yoffset+int(y)]=val
            self.cols[self.yoffset+int(y)][self.xoffset+int(x)]=val
    
    def setRow(self,x,val):
        self.set(x,None,val)
    def setColumn(self,y,val):
        self.set(None,y,val)

    def getHeaders(self):
        index = self.header or 0
        return self.rows[index] if index<len(self.rows) else []

    #@Catched
    def colByHead(self,head,header=None):
        """
        Get the index of the column headed by 'head'
        """
        if not head: return head
        self.header = self.header or 0
        head = head.strip()
        if header is None:
            Hrow = self.rows[self.header]
        else:
            Hrow = self.rows[header]
        if head not in Hrow:
            if self.trace: print 'colByHead: Head="',head,'" does not exist in: %s'%Hrow
            return None
        return Hrow.index(head)
        
    ###########################################################################
    # Methods for conversion from/to Dictionary Trees
    ###########################################################################
        
    #@Catched
    def fill(self,y=None,head=None,previous=[]):
        """Fill all the empty cells in a column with the last value introduced on it
        By default this method adds new values to a column only when the previous column remains unchanged
        To force all the values to be filled set previous=True
        """
        if self.trace: print 'CSVArray.fill(%s,%s,%s)'%tuple(str(s) for s in [y,head,previous])
        if type(y) is str: head,y =  y,None
        c = y if y in range(self.ncols+1) else self.colByHead(head)
        column = self.get(y=c)
        last = ''
        previous = (type(previous) is list and previous) or (previous and len(column)*[previous]) or (c and self.get(y=c-1)) or []
        for r in range(len(column)):
            if r and column[r]=='' and (not previous or previous[r-1]==previous[r]):
                self.set(r,c,last)
            else: last = column[r]

    #@Catched
    def expandAll(self):
        for c in range(self.ncols): self.fill(y=c)
        return self
        
    def getAsTree(self,root=0,xsubset=[],lastbranch=None):
        """
        This method returns the content of the array as recursive dicts
        It will produce the right output only if the array has been filled before!
        [self.fill(head=h) for h in self.getHeaders()]
        
        headers={dict with headers as keys}
        for h in headers: fill with distinct keys on each column
        get the keys on first column
            for each key, get the distinct keys in the next column matching lines
                for each key, get the distinct keys in the next column matching lines       
        """
        if lastbranch is None: lastbranch=self.ncols
        elif type(lastbranch) is str: lastbranch=self.colByHead(lastbranch)
            
        klines=self.get(y=root,distinct=True,xsubset=xsubset)
        if len(klines)==1 and root>lastbranch: #Return resting columns in a single line
            return self.get(x=klines.values()[0][0],ysubset=range(root,self.ncols))
        elif root+1>=self.ncols: #Last column
            return dict.fromkeys(klines.keys(),{})
        else:
            tree={}
            for k in klines.keys():
                #if not k:  #!DEPRECATED AS WE WERE LOOSING INFORMATION IF A CELL IS EMPTY!
                    #print 'WARNING! %s has not been properly filled' % k
                    #continue
                tree[k]=self.getAsTree(root=root+1,xsubset=klines[k],lastbranch=lastbranch)
            return tree
            
    def updateFromTree(self,tree):
        """
        This method takes a dictionary of type {level0:{level1:{level2:{}}}}
        and converts it into a grid like level0 \t level1 \t level2
        WARNING!: This method deletes the actual content of the array!
        """
        if self.trace: print 'WARNING!: updateFromTree deletes the actual content of the array!'
        table = tree2table(tree)
        self.resize(1,1)
        self.resize(len(table),max(len(line) for line in table))
        [self.setRow(i,table[i]) for i in range(len(table))]

    #def printTree(self,level=None,depth=0):
        #if not level: level=self.getAsTree()
        #MAX_DEPTH=10
        #if depth>MAX_DEPTH or not hasattr(level,'items'): return
        #for k,l in level.iteritems():
            #if operator.isMappingType(l):
                #print (' '*depth),k,'=',l.keys()
                #self.printTree(l,depth+1)
            #else:
                #print (' '*depth),k,'=',l
                
    def printArray(self):
        for r in range(len(self.rows)):
            print r,':','\t'.join([str(e or '\t') for e in self.rows[r]])
        #for r in range(len(self.rows)):
            #print r,':','\t'.join([self.cols[c][r] for c in range(len(self.cols))])
    
    pass #END OF CSVARRAY
