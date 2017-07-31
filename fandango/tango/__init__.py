

import fandango
import os,sys

p = fandango.__file__.rsplit('/',1)[0]
p += '/tango.pyc'

if os.path.exists(p):
  print('fandango.tango ERROR!:')
  print('An old tango.pyc file still exists at:\n\t%s'%p)
  print('Remove it before proceed')
  print('')
  sys.exit(-1)


from .defaults import *
from .methods import *
from .search import *
from .export import *
from .tangoeval import *
from .command import *



