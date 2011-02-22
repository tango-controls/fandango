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
from functools import partial

######################################################3
## Some miscellaneous logic methods
######################################################3

def first(seq):
    """Returns first element of sequence"""
    try: 
        return seq[0]
    except Exception,e: 
        try: 
            return seq.next()
        except:
            raise e #if .next() also doesn't work throw unsubscriptable exception
    return

def last(seq,MAX_SEQ=1000):
    """Returns last element of sequence"""
    try:
        return seq[-1]
    except Exception,e:
        try: 
            n = seq.next()
        except: 
            raise e #if .next() also doesn't work throw unsubscriptable exception
        try:
            for i in range(1,MAX_SEQ):
                n = seq.next()
            if i>(MAX_SEQ-1):
                raise Exception,'SequenceLongerThan%d'%MAX_SEQ
        except StopIteration,e: 
            return n
    return

def anyone(seq):
    """Returns first that is true or last that is false"""
    for s in seq:
        if s: return s
    return s

def everyone(seq):
    """Returns last that is true or first that is false"""
    for s in seq:
        if not s: return s
    return s
        
######################################################3
## Methods for identifying types        
######################################################3
        
def isString(seq):
    if isinstance(seq,str): return True
    tt = str(type(seq))
    return 'str' in tt or 'QString' in tt
    
def isNumber(seq):
    return operator.isNumberType(seq)
    
def isSequence(seq):
    """ It excludes Strings and dictionaries """
    if any(isinstance(seq,t) for t in (list,set,tuple)): return True
    if isString(seq): return False
    if hasattr(seq,'items'): return False
    if hasattr(seq,'__iter__'): return True
    return False
    
def isDictionary(seq):
    """ It includes dicts and also nested lists """
    if isinstance(seq,dict): return True
    if hasattr(seq,'items') or hasattr(seq,'iteritems'): return True
    if seq and isSequence(seq) and isSequence(seq[0]):
        if seq[0] and not isSequence(seq[0][0]): return True #First element of tuple must be hashable
    return False
    
def isIterable(seq):
    """ It includes dicts and listlikes but not strings """
    return hasattr(seq,'__iter__') and not isString(seq)