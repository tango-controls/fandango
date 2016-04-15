#!/usr/bin/env python

#############################################################################
##
## file :       device.py
##
## description : CLASS FOR Enhanced TANGO DEVICE SERVERs
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
This module is used to have all those classes used inside DeviceServers or to control/configure them 
and are not part of the Astor api (ServersDict)
"""

#pytango imports
import PyTango
import types
#fandango imports
import fandango as fun
from fandango.log import Logger,except2str,printf
from fandango.excepts import *
from fandango.callbacks import *
import fandango.tango as tango #Double import to avoid ambiguous naming of some methods
from fandango.tango import * #USE_TAU imported here, get_polled_attrs and other useful methods
from fandango.dicts import CaselessDefaultDict,CaselessDict
from fandango.arrays import TimedQueue
from fandango.dynamic import DynamicDS,USE_STATIC_METHODS


##############################################################################################################
## DDebug, DS used to have access to DServer internal objects (as a complement of DServer admin device

from fandango.dynamic import DynamicDS,DynamicDSClass
class DDebug(DynamicDS):
    def __init__(self,cl, name):
        U = PyTango.Util.instance()
        import gc,resource
        try:
            import guppy
            heapy = guppy.hpy()
        except:guppy,heapy = None,None
        DynamicDS.__init__(self,cl,name,_locals={'Util':U,'PyUtil':U,'self':self,'fandango':fandango,
            'resource':resource,'gc':gc,'guppy':guppy,'heapy':heapy},
            useDynStates=False)
        DDebug.init_device(self)
    def init_device(self):
        self.set_state(PyTango.DevState.ON)
        #self.get_DynDS_properties()
    def always_executed_hook(self): pass #DynamicDS.always_executed_hook(self)
    def read_attr_hardware(self,data): pass
    @staticmethod
    def addToServer(py,server,instance):
        name = '%s/%s'%(server,instance)
        add_new_device(name,'DDebug','sys/%s/%s_%s'%('DDebug',server,instance))
        py.add_TgClass(DDebugClass,DDebug,'DDebug')
        
class DDebugClass(DynamicDSClass):
    class_property_list={}
    device_property_list={}
    cmd_list={'evaluateFormula':[[PyTango.DevString, "formula to evaluate"],[PyTango.DevString, "formula to evaluate"],],}  
    attr_list={}


