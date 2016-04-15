#!/usr/bin/env python

__doc__ = """
Usage:
    tango_create Server/Instance Class DeviceName {properties as python dictionary}
"""

from PyTango import *

def main():
  import sys
  import fandango

  try:
      server,classname,devicename = sys.argv[1:4]
      props = eval(fandango.first(sys.argv[4:]) or ['{}'])
  except:
      print __doc__
      sys.exit(1)

  fandango.tango.add_new_device(server,classname,devicename)
  if props:
      fandango.get_database().put_device_property

  db = Database()

  rateDS = 100
  nDS = 30
  first = 31

  def addTangoDev(server,_class,device):
          di = DbDevInfo()
          di.name,di._class,di.server = device,_class,server
          db.add_device(di)

  _class = 'PySignalSimulator'
  domain = 'sim'
  family = 'pysignalsimulator'

  print 'Creating ',str(rateDS*nDS) , ' TangoTest device Servers ...'
  for m in range(first,nDS+first):
          server = '/'.join([_class,'%02d'%m])
          print 'Deleting server ',server
          try: db.delete_server(server)
          except: pass
          for n in range(1,rateDS+1):
                  server = '/'.join([_class,'%02d'%m])
                  member = '%02d'%m+'-'+'%02d'%n
                  device = '/'.join([domain,family,member])
                  print 'Creating device ',device
                  addTangoDev(server,_class,device)
                  print 'Adding Properties to class/device = ',_class,'/',device
                  db.put_class_property(_class,{'Description':['device used to test the archiving system']})
                  db.put_device_property(device,{'SimAttributes':['A1=sin((t+random())/2.)']})
                  db.put_device_property(device,{'SimStates':['FAULT=square(t,period=10)',"ALARM=Attr('A1')<0",'ON=1']})

if __name__ == '__main__':
  main()