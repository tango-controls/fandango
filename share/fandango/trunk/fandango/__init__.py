#!/usr/bin/env python2.5
"""
@if gnuheader
#############################################################################
##
## file :       PyTango_utils
##
## description :    This module includes some PyTango additional classes and methods that 
##               are not implemented in the C++ API. Some of them will be moved to the official 
##              TAU Core packages in the future.
##
## project :     Tango Control System
##
## $Author: Sergi Rubio Manrique, srubio@cells.es $
##
## $Revision: Created on 19th February 2008 $
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
@package fandango
@mainpage fandango "Functional tools for Tango" Reference
Several modules included are used in Tango Device Server projects, like @link dynamic @endlink and PyPLC. @n
@brief This module(s) include some PyTango additional classes and methods that are not implemented in the C++/Python API's; it replaces the previous PyTango_utils module
 
"""

import os,traceback
try:
    import objects,imp
    PATH = os.path.dirname(objects.__file__)
    ReleaseNumber = type('ReleaseNumber',(tuple,),{'__repr__':(lambda self:'.'.join(('%02d'%i for i in self)))})
    RELEASE = ReleaseNumber(imp.load_source('changelog',PATH+'/CHANGES').RELEASE)
except: 
    print traceback.format_exc()
    print 'Unable to load RELEASE number'

try:
    from functional import *
except: print 'Unable to import functional module'
try:
    from log import printf,Logger,LogFilter,shortstr,except2str,FakeLogger
except: print 'Unable to import log module'
try:
    from excepts import trial,getLastException,getPreviousExceptions,ExceptionWrapper,Catched,Catched2
except: print 'Unable to import excepts module'
try:
    from objects import Object,Singleton,SingletonMap,Struct,NamedProperty
except: 
    print 'Unable to import objects module'
try:
    from linos import shell_command,ping,sysargs_to_dict,listdir
except: print 'Unable to import linos module'
try: 
    from arrays import CSVArray
except: print 'Unable to import arrays module'
try:
    from dicts import ThreadDict,CaselessDict,ReversibleDict,CaselessDefaultDict,DefaultThreadDict,Enumeration,SortedDict,CaselessList
except: print 'Unable to import dicts module'

try:
    from threads import WorkerProcess,WorkerThread,SingletonWorker
except: print 'Unable to import threads module'

#TANGO related modules
try:
    from tango import get_device,get_database,get_database_device,get_all_devices,get_device_info,\
        get_alias_for_device,get_device_for_alias,get_tango_host, \
        find_devices,find_attributes,get_matching_devices,get_matching_attributes,\
        cast_tango_type,parse_tango_model,check_attribute,check_device,except2str,\
        TangoEval,ProxiesDict,getTangoValue,TangoCommand,fakeEvent,fakeEventType
    try: 
        from device import Dev4Tango,TangoEval,TimedQueue,DevChild,TangoCommand
    except Exception,e: raise Exception('fandango.device: %s'%e)
    try: 
        from servers import ServersDict,Astor,ProxiesDict,ComposersDict
    except Exception,e: raise Exception('fandango.servers: %s'%e)
    try: 
        from dynamic import DynamicDS,DynamicDSClass,DynamicAttribute,DynamicDSTypes,CreateDynamicCommands
    except Exception,e: raise Exception('fandango.dynamic: %s'%e)
    try: 
        from interface import FullTangoInheritance,NewTypeInheritance
    except Exception,e: raise Exception('fandango.interface: %s'%e)
except Exception,e: 
    print 'Unable to import fandango.*tango modules: %s'%e
    #print traceback.format_exc()

#OTHER fancy modules
if False:
    try: import web
    except: print 'Unable to import fandango.web module'
    try: import qt
    except: print 'Unable to import fandango.qt module'
    try: from db import FriendlyDB
    except: print 'Unable to import db module'

__all__ = ['dicts','excepts','log','objects','db','device','web','threads','dynamic','callbacks','arrays','servers','linos','functional','interface','qt']
#print 'module reloaded'
