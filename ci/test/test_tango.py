
# Test file for fandango.tango submodule

import traceback,re,sys,json
import fandango as fn 
import fandango.tango as ft
from fandango.tango import *
from fandango.functional import *

###############################################################################
# Test routines for fandango.tango module

def test_get_matching_servers(*args,**kwargs):

  if not any((args,kwargs)):
    test,kwargs = True,{
      'expressions':'PyAlarm/*',#database
      'tango_host':'controls02:10000',
      'exported':True,
      } 
  else:
    test = False
    
  r = get_matching_servers(*args,**kwargs)
  assert not test or ('DataBaseds/2' in r)
  return r

def main(args):
  i2t = lambda t,v: (t,str2type(v))
  args = args or ['get_matching_servers']
  
  meth = 'test_'+args[0]
  kwargs = dict(i2t(*a.split('=')) for a in args[1:] if '=' in a)
  args = [str2type(a) for a in args[1:] if '=' not in a]

  fn.printf(__file__,':',meth,'(',args,kwargs,')')
  try:
    r = globals()[meth](*args,**kwargs)
    fn.printf('>>',r)
  except:
    traceback.print_exc()
  
if __name__ == '__main__':
  main(sys.argv[1:])
