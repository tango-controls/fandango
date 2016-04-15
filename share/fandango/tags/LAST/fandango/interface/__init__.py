import traceback

from .inheritance import *

try:
  from CopyCatDS import CopyCatDS,CopyCatDSClass,CopyCatServer
except:
  print 'Unable to import fandango.interface.CopyCatDS'
  print traceback.format_exc()


