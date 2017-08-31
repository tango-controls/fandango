#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""
#############################################################################
##
## project :     Functional tools for Tango Control System
##
## $Author:      Sergi Rubio Manrique, srubio@cells.es $
##
## $Revision:    2008 $
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


import traceback
import threading
import time

def timeit(target,args=[],kwargs={},setup='pass',number=1):
  if isinstance(target,str):
    import timeit
    return timeit.timeit(target,setup,number=number)
  elif callable(target):
    t0 = time.time()
    try:
      [target(*args) for i in range(number)]
    except:
      traceback.print_exc()
    return time.time()-t0
  
def Timed(target,tries=1):
    def wrapped(*args,**kwargs):
        times = []
        for i in range(tries):
            t0 = time.time()
            r = target(*args,**kwargs)
            times.append(1e3*(time.time()-t0))
        times = ', '.join('%3.1f'%t for t in times)
        print('%s needed %s ms'%(target,times))
        return r
    return wrapped

def test_xtreme(device,attribute,value):
    import PyTango
    i,dp = 0,PyTango.DeviceProxy(device)
    try:
        while i<value:
            i+=1
            dp.read_attribute(attribute)
            threading.Event().wait(0.01)
    except:
        print '%s.read_attribute(%s) failed after %d retries' % (device,attribute,i)
        print traceback.format_exc()
        PyTango.DeviceProxy(dp.adm_name()).command_inout('kill')
    return
       
from . import doc
__doc__ = doc.get_fn_autodoc(__name__,vars())
 
