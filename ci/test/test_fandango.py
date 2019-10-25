#!/usr/bin/env python

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

import traceback,sys

try:
  import PyTango
except:
  PyTango = None
  
try:
  from PyQt4 import Qt
except:
  Qt = None

from fandango.log import InOutDecorator

@InOutDecorator
def test_log():
  import fandango.log
  try:
    fandango.log.info('Testing logs ...')
    return True
  except:
    traceback.print_exc()
    return False
  
def test_fandango():
  import fandango
  assert fandango
  assert fandango.objects
  assert fandango.functional
  assert test_log() is True
  assert fandango.dicts
  assert fandango.threads

  if PyTango:
    assert fandango.tango
    assert fandango.servers
    assert fandango.dynamic
    assert fandango.device
    assert fandango.device.DevChild
    assert fandango.device.DDebugClass

  if Qt:
    import fandango.qt
    assert fandango.qt
    
if __name__ == '__main__':
  test_fandango()