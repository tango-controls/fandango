#!/usr/bin/env python

#############################################################################
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

import fandango

__doc__ = """

Usage:

  fandango.sh [-h/--help] [-x/--extra] [fandango_method_0] [fandango_method_1] [...]

  Objects and Generators will not be allowed as arguments, only python primitives, lists and tuples
  
Examples:

  fandango.sh findModule fandango
  
  fandango.sh get_tango_host
  
  fandango.sh --help get_matching_devices | less
  
  fandango.sh get_matching_devices "tango/admin/*"
  
  fandango.sh get_matching_attributes "lab/ct/plctest16/*_af"
  
  fandango.sh -h | grep propert
  
  fandango.sh get_matching_device_properties "lab/ct/plctest16" "*modbus*"
  
  fandango.sh read_attribute "tango/admin/pctest/status"
  
  for attr in $(fandango.sh get_matching_attributes "tango/admin/pctest/*"); do echo "$attr : $(fandango.sh read_attribute ${attr})" ; done
  
"""

"""
A launcher like this can't be created as a function, because generic imports with 
wildcards are allowed only at module level.

If it is problem is solved in the future, then it will be moved to fandango.linos
"""

if __name__ == '__main__':
  import sys
  cmd = ''
  try:
    #comms = sys.argv[sys.argv.index('-c')+1:]
    comms,opts = fandango.sysargs_to_dict(split=True,cast=False,lazy=False)
    
    from fandango.functional import *
    from fandango.tango import *
    from fandango.servers import *
    from fandango.linos import *
    from fandango.objects import *
    
    if opts.get('-x',opts.get('extra',0)):
      try: 
        import PyTangoArchiving
        from PyTangoArchiving import Reader
        from PyTangoArchiving.files import LoadArchivingConfiguration
        locals()['pta'] = PyTangoArchiving
      except: pass
      try: 
        import panic
      except: pass
    
    if opts.get('-h',opts.get('help',0)):
      import inspect
      
      _locals=locals()
      def get_module_name(o):
          o = inspect.getmodule(o)
          return getattr(o,'__name__','')
      _locals['get_module_name'] = get_module_name
      
      target = comms[0] if comms else (opts.get('help') or '')
      if target and isString(target):
        cmd = 'inspect.getsource(%s)'%target
      else:
        cmd = "sorted([('%s.%s'%(get_module_name(o),k)).strip('.') for k,o in locals().items() if not k.startswith('_')])"
        
      r = evalX(cmd,_locals=_locals)
      if isSequence(r):
        r = list2str(r,'\n')
      for c in ('"""',"'''"):
        if c in r:
          r = c.join(r.split(c)[:2])+c
      if not target: 
        r = __doc__+'\n\nAvailable methods:\n\n'+r
      
    else:
      assert comms
      if '(' in comms[0]:
        _locals = locals()
        for c in comms:
          cmd = c
          r = evalX(c,_locals=_locals)
      else:
        args = ','.join((str(c) if isNumber(c) else "'%s'"%c) for c in comms[1:])
        cmd = '%s(*[%s])'%(comms[0],args)
        r = evalX(cmd,_locals=locals())
        
    if opts.get('-l'): print(cmd)
    print(r if not isSequence(r) else list2str(r,'\n'))
  except AssertionError,e:
    print(__doc__)
  except:
    print(cmd)
    import traceback
    traceback.print_exc()
    sys.exit(1)
  sys.exit(0)