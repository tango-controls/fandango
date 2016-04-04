#!/usr/bin/python

__doc__ = 'An updated version of this script is included as createStarter function in csv2tango'

from PyTango import *
import sys

def main():
  db = Database()

  def addStarterDev(host):
          server = 'Starter'; instance = host.split('.')[0]; member = instance
          sep = '/'; domain = 'tango'; family = 'admin';
          di = DbDevInfo()
          di.name,di._class,di.server = \
                  sep.join([domain,family,member]), \
                  server,sep.join([server,instance])
          db.add_device(di)
          
  hostnames = []
  if len(sys.argv)>1: 
          for h in sys.argv[1:]:
                  hostnames.append(h)
  else:
          hostnames = ['palantir01']

  for h in hostnames:
          addStarterDev(h)

  """
  Class Properties
  Property name
          
  Property type
          
  Description
  ReadInfoDbPeriod 	Tango::DEV_SHORT 	Period to read database for new info if not fired from Database server.
  NbStartupLevels 	Tango::DEV_SHORT 	Number of startup levels managed by starter.
  CmdPollingTimeout 	Tango::DEV_LONG 	Timeout value in seconds to stop polling if no command has been received.
  UseEvents 	Tango::DEV_SHORT 	Use events if not null.
  ServerStartupTimeout 	Tango::DEV_LONG 	Timeout on device server startup in seconds.
  """

  dclass = 'Starter'
  #db.put_class_property(dclass,{'ReadInfoDbPeriod':[60]})
  db.put_class_property(dclass,{'NbStartupLevels':[10]})
  #db.put_class_property(dclass,{'CmdPollingTimeout':[10]})
  #db.put_class_property(dclass,{'UseEvents':[1]})
  #db.put_class_property(dclass,{'ServerStartupTimeout':[60]})

  """
  Device Properties
  Property name
          
  Property type
          
  Description
  StartDsPath 	Array of string 	Path to find executable files to start device servers
  WaitForDriverStartup 	Tango::DEV_SHORT 	The Starter will wait a bit before starting servers, to be sure than the drivers are started.This time is in seconds.
  UseEvents 	Tango::DEV_SHORT 	Use events if not null.
  StartServersAtStartup 	Tango::DEV_BOOLEAN 	Skip starting servers at startup if false.
  InterStartupLevelWait 	Tango::DEV_LONG 	Time to wait before two startup levels in seconds.
  ServerStartupTimeout 	Tango::DEV_LONG 	Timeout on device server startup in seconds.
  """

  for dname in ['tango/admin/'+h.split('.')[0] for h in hostnames]:
   print 'Initial values for properties of ',dname,' are ', \
     db.get_device_property(dname,['StartDsPath','WaitForDriverStartup','UseEvents','StartServersAtStartup','InterStartupLevelWait','ServerStartupTimeout'])
   db.put_device_property(dname,{'StartDsPath':[
                  '~/devservers',
                  '~/ds',
                  '~/tango/bin',
                  '~/archiving/bin',
                  ]})
   #db.put_device_property(dname,{'WaitForDriverStartup':[60]})
   #db.put_device_property(dname,{'UseEvents':[1]})
   db.put_device_property(dname,{'StartServersAtStartup':['True']})
   db.put_device_property(dname,{'InterStartupLevelWait':[30]})
   #db.put_device_property(dname,{'ServerStartupTimeout':[60]})
   print 'Final values for properties of ',dname,' are ', \
     db.get_device_property(dname,['StartDsPath','WaitForDriverStartup','UseEvents','StartServersAtStartup','InterStartupLevelWait','ServerStartupTimeout'])
          
 
if __name__ == '__main__':
  main()