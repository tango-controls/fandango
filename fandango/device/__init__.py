
try:
  from . import DDebug as debug
  from .DDebug import *
except:
  print('Unable to import DDebug')
try:
  from . import Dev4Tango as dev4tango
  from .Dev4Tango import *
except:
  print('Unable to import Dev4Tango')
try:
  from . import FolderDS as folders
  from .FolderDS import FolderDS,FolderAPI
except:
  print('Unable to import FolderDS')
try:
  from . import WorkerDS as workers
except:
  print('Unable to import WorkerDS')

