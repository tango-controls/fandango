
try:
  import DDebug as debug
  from DDebug import *
except:
  print('Unable to import DDebug')
try:
  import Dev4Tango as dev4tango
  from Dev4Tango import *
except:
  print('Unable to import Dev4Tango')
try:
  import FolderDS as folders
  from FolderDS import FolderDS,FolderAPI
except:
  print('Unable to import FolderDS')
try:
  import WorkerDS as workers
except:
  print('Unable to import WorkerDS')

