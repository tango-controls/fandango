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

try: 
    from servers import ServersDict,Astor,ProxiesDict
except: print 'fandango: Unable to import servers module'

RELEASE = (7,0,0)

__all__ = ['dicts','excepts','log','object','db','dynamic','callbacks','arrays','servers']
#print 'module reloaded'
