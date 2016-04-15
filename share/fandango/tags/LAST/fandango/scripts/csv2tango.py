#!/usr/bin/python

"""
Script to import CSV Files to Tango Database
srubio@cells.es, 2008
ALBA Synchrotron Controls Group
"""

import sys,os, traceback
from PyTango import *

def main():

  if len(sys.argv)<1:
      exit()

  print 'Loading file ...'
  array = CSVArray()
  array.load(sys.argv[1],prune_empty_lines=True)
  array.setOffset(x=1)
  for s in ['server','class','device','property']: array.fill(head=s)

  #print array.get(x=0)
  print 'Getting device column ...'
  answer = raw_input('Do you want to force all device names to be uppercase? (Yes/No)')
  if answer.lower().startswith('y'):
      listofdevs = {}
      [listofdevs.__setitem__(s.upper(),i) for s,i in array.get(head='device',distinct=True).iteritems()]
  else:
      listofdevs = array.get(head='device',distinct=True)
  print '%s devices read from file.' % len(listofdevs)
  lkeys = listofdevs.keys()
  lkeys.sort()

  #######################################################################

  def getProperties(device):
      props={}
      for l in listofdevs[device]:
          pr = array.get(x=l,head='property')
          try: 
              if pr not in props:
                  props[pr]=[array.get(x=l,head='value')]
              else:
                  props[pr].append(array.get(x=l,head='value'))
          except Exception,e:
              print traceback.format_exc()
              print 'Failed to get %s property' % pr
      for p,v in props.items():
          if '\\n' in v[0]:
              print '------------------------rebuilding property ',p,'-----------------------------'
              props[p]='\\n'.join(v).split('\\n')
      return props
          
  def getField(line,field):
      server=array.get(x=line,head=field)
      _class=array.get(x=listofdevs[device][0],head='class')
      return server,_class,name

  def createStarter(hostnames,folders=[]):
      """
      TODO: createStarter imported from createStater.py but not implemented yet in the script
      """
      db = Database()
      def addStarterDev(host):
          server = 'Starter'; instance = host.split('.')[0]; member = instance
          sep = '/'; domain = 'tango'; family = 'admin';
          di = DbDevInfo()
          di.name,di._class,di.server = \
              sep.join([domain,family,member]), \
              server,sep.join([server,instance])
          db.add_device(di)
      for h in hostnames:
          addStarterDev(h)
      
      ## Setting Starter Class properties
      dclass = 'Starter'
      #db.put_class_property(dclass,{'ReadInfoDbPeriod':[60]})
      db.put_class_property(dclass,{'NbStartupLevels':[10]})
      #db.put_class_property(dclass,{'CmdPollingTimeout':[10]})
      #db.put_class_property(dclass,{'UseEvents':[1]})
      #db.put_class_property(dclass,{'ServerStartupTimeout':[60]})
      
      ## Setting Starter Device Properties
      folders = folders or ['~/devservers','~/ds','~/tango/bin','~/archiving/bin',]
      for dname in ['tango/admin/'+h.split('.')[0] for h in hostnames]:
          print 'Initial values for properties of ',dname,' are ', \
              db.get_device_property(dname,['StartDsPath','WaitForDriverStartup','UseEvents','StartServersAtStartup','InterStartupLevelWait','ServerStartupTimeout'])
          
          db.put_device_property(dname,{'StartDsPath':folders})
          #db.put_device_property(dname,{'WaitForDriverStartup':[60]})
          #db.put_device_property(dname,{'UseEvents':[1]})
          db.put_device_property(dname,{'StartServersAtStartup':['True']})
          db.put_device_property(dname,{'InterStartupLevelWait':[30]})
          #db.put_device_property(dname,{'ServerStartupTimeout':[60]})
          
          print 'Final values for properties of ',dname,' are ', \
              db.get_device_property(dname,['StartDsPath','WaitForDriverStartup','UseEvents','StartServersAtStartup','InterStartupLevelWait','ServerStartupTimeout'])
      
  print createStarter.__doc__
  #######################################################################
      
  print 'Get device properties ...'
  for device in listofdevs.keys():
      print 'Device ',device,' properties are:'
      props=getProperties(device)
      for p,v in props.items(): print '\t',p,':',str(v)
      
  def addTangoDev(server,_class,device):
          di = DbDevInfo()
          di.name,di._class,di.server = device,_class,server
          db.add_device(di)
      
  overwrite = False
  answer = raw_input('do you want to effectively add this devices and properties to the database %s? (Yes/No/Overwrite)'%os.environ['TANGO_HOST'])

  if answer.lower() in ['o','overwrite']:
      overwrite,answer = True,'yes'
      
  if answer.lower() in ['y','yes']:
      db = Database()
      for device,lines in listofdevs.items():
          server=array.get(x=lines[0],head='server').strip()
          _class=array.get(x=lines[0],head='class').strip()
          
          # Create the Device if it doesn't exists
          #----------------------------------------------------------------------------------------
          if not db.get_device_member(device) or overwrite:
              print 'Creating ',device,' device ...'
              addTangoDev(server,_class,device)
          else:
              print device,' device already exists ...'
          
          props=getProperties(device)
          oldprops=db.get_device_property(device,props.keys())
          
          ##@todo loading default properties
          # A way to define easily if some default properties must be defined and implemented here!

          # oldprops values must be updated with new values
          oldprops=db.get_device_property(device,props.keys())

          # Set properties in the Database (overwriting iff specified)
          #----------------------------------------------------------------------------------------
          for property,value in props.items():
              if overwrite or not oldprops[property]:
                  value = type(value) in (list,set) and value or [value]
                  while not value[-1] and len(value)>1: value.pop(-1)
                  print 'Device Property ',device,'.',property,', creating: ',value
                  db.put_device_property(device,{property:value})
              else:
                  print 'Device Property ',device,'.',property,' already exists: ',oldprops[property]

if __name__ == '__main__':
  main()    

