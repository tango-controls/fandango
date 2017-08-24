

import fandango
import os,sys

p = fandango.__file__.rsplit(os.path.sep,1)[0]
p += os.path.sep+'tango.pyc'

if os.path.exists(p):
    try:
        os.remove(p)
        print('%s removed ...')
    except Exception,e:
        print(e)
        print('fandango.tango ERROR!:')
        print('An old tango.pyc file still exists at:\n\t%s'%p)
        print('Remove it as sysadmin and try again')
        print('')
        sys.exit(-1)


from .defaults import *
from .methods import *
from .search import *
from .export import *
from .tangoeval import *
from .command import *



