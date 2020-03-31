#!/usr/bin/env python

"""
Script to import CSV Files to Tango Database
srubio@cells.es, 2008
ALBA Synchrotron Controls Group
"""

import sys,os, traceback
from PyTango import *
import fandango as fn
from fandango import SortedDict,CSVArray
from fandango.functional import *
from fandango.tango import *
#from fandango.arrays import *

def remove_tango_devices(devices,db=None):
    """
    Remove Tango devices and its properties from Database
    """
    db = db or fn.get_database()
    servers = set()
    for d in devices:
      try:
        print('Removing %s from Tango database'%d)
        props = db.get_device_property_list(d,'*')
        for p in list(props):
          db.delete_device_property(d,p)
        servers.add(db.get_device_info(d).ds_full_name)
        db.delete_device(d)
      except:
        traceback.print_exc()
        print('Unable to delete %s device'%d)
    for server in servers:
      try:
        devs = list(db.get_device_class_list(server))
        if not devs or all(fn.clmatch('^deserver*',d) for d in devs):
          print('Removing %s from Tango database'%server)
          db.delete_server(server)
      except:
        traceback.print_exc()
        print('Unable to delete %s server'%server)
    return len(devices)

def main():

  if len(sys.argv)<=1:
      print('Insert devices and properties into Tango Database')
      print('Usage: csv2tango ["--filter=*/*/*"] filename.csv')
      exit()

  filename = sys.argv[-1]
  options = [o for o in sys.argv[1:-1] if o.startswith('-')]
  print('Loading %s ...'%filename)
  print('options = %s'%(options))
  filters = ([o.replace('--filter=','') for o in options if '--filter' in o] or ['*'])[0]
  
  array = CSVArray(filename,header=0,offset=1)
  [array.fill(head=s) for s in array.getHeaders()]

  #print('Getting device columns ...')
  classes = array.get(head='class',distinct=True)
  devices = array.get(head='device',distinct=True)
  devices = dict((k,v) for k,v in devices.items() if k and clmatch(filters,k))
  
  if '' in classes: 
    print(classes)
    print('-'*80)
    print('\n'.join('%03d:%s'%(i,'\t'.join(r)) for i,r in enumerate(array.rows)))
    print('-'*80)
  else:  
    print('%d classes: %s'%(len(classes),classes.keys()))
  print('%d devices read from file.' % (len(devices)))
  
  upper = raw_input('Do you want to force all device names '
                      'to be uppercase? (Yes/No)')
  upper = upper.startswith('y')
  devices = dict((k.upper() if k else k,v)
      for k,v in devices.items() if k and not fn.isRegexp(k))

  #######################################################################

  def getProperties(device):
      props={}
      lines= device if fn.isSequence(device) else devices[device.upper()]
      #Iterate through each line of device declaration
      for l in lines:
          pr = array.get(x=l,head='property')
          try: 
              if pr:
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
      _class=array.get(x=devices[device][0],head='class')
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
  
  kprops,dprops,wildcards = {},fn.dicts.CaselessDict(),fn.dicts.SortedDict()
  for lines,klass in sorted((v,k) for k,v in classes.items()):
      kdevs = array.get(head='device',distinct=True,xsubset=lines)
      print('%s has %d devices'%(klass,len(kdevs)))
      for lines,device in sorted((v,k) for k,v in kdevs.items()):
        props = {}
        if not device:
          print('Get Class Properties (%s,%s):'%(klass,lines))
          kprops[klass] = props = getProperties(lines)
        elif klass and fn.isRegexp(device):
          print('Get Wildcard Properties (%s,%s):'%(klass,device))
          if klass not in wildcards: wildcards[klass] = SortedDict()
          wildcards[klass][device] = props = getProperties(lines)
        else:
          if not clmatch(filters,device): continue
          if upper: device = device.upper()
          print('Get Device Properties (%s,%s,%s)'%(klass,device,lines))
          ## Parse wildcards
          for k,ds in wildcards.items():
            for d,ps in ds.items():
              if clmatch(k,klass) and clmatch(d,device):
                props.update(ps)
          if props: print('wildcard: %s'%props)
          props.update(getProperties(device))
          dprops[device] = props
        if props:
          for p,v in props.items(): print('\t%s:%s'%(p,v))
          print('\n')
  
  #for device,lines in devices.items():
      #print('getDeviceProperties(%s,%s)'%(device,lines))
      #dprops[device] = props = getProperties(device)
      #for p,v in props.items(): print('\t%s:%s'%(p,v))
      
  def addTangoDev(server,_class,device):
          di = DbDevInfo()
          di.name,di._class,di.server = device,_class,server
          db.add_device(di)
          
  if len(devices)!=len(dprops):
    print('!?: %s'%[d for d in devices if d not in dprops])
    print('!?: %s'%[d for d in dprops if d not in devices])
    
  alldevs = fn.tango.get_all_devices()
  db = fn.tango.get_database()
  already = [d for d in dprops if d.lower() in alldevs] 
  if already:
    answer = raw_input('%d devices already exist, '
      'do you want to DELETE its previous data from the database?'%len(already))
    if answer.lower() in ['y','yes']:
        remove_tango_devices(already,db)
        
  overwrite = False
  answer = raw_input('do you want to effectively add this devices and properties to the database %s? (Yes/No/Overwrite)'%get_tango_host())

  if answer.lower() in ['o','overwrite']:
      overwrite,answer = True,'yes'
      
  if answer.lower() in ['y','yes']:
      
      for k,props in kprops.items():
          oldprops = db.get_class_property(k,props.keys())
          
          # Set properties in the Database (overwriting iff specified)
          #----------------------------------------------------------------------------------------
          for prop,value in props.items():
              if not prop: continue
              if overwrite or not oldprops[prop]:
                  value = type(value) in (list,set) and value or [value]
                  while not value[-1] and len(value)>1: value.pop(-1)
                  print('Class Property ',k,'.',prop,', creating: ',value)
                  db.put_class_property(k,{prop:value})
              else:
                  print('Class Property ',k,'.',prop,' already exists: ',oldprops[prop])
      
      for device,lines in devices.items():
          server=array.get(x=lines[0],head='server').strip()
          klass=array.get(x=lines[0],head='class').strip()
          
          # Create the Device if it doesn't exists
          #----------------------------------------------------------------------------------------
          if device.count('/')>=2 and device.lower() not in alldevs:
              #DO NOT RECREATE EVEN ON OVERWRITE
              print('Creating %s.%s(%s) '%(server,klass,device))
              addTangoDev(server,klass,device)
          else:
              print('%s device already exists ...'%(device))
          
          ##@todo loading default properties
          # A way to define easily if some default properties must be defined and implemented here!
          props = dprops[device]

          # oldprops values must be updated with new values
          oldprops = db.get_device_property(device,props.keys())
          
          attr_props = fn.defaultdict(dict)

          # Set properties in the Database (overwriting iff specified)
          #----------------------------------------------------------------------------------------
          for prop,value in props.items():
              if not prop: 
                  continue

              if prop.startswith('/'):
                  attr,prop = prop.strip('/').split('.',1)
                  attr_props[attr][prop] = value
                  
              elif overwrite or not oldprops[prop]:
                  value = type(value) in (list,set) and value or [value]
                  while not value[-1] and len(value)>1: value.pop(-1)
                  if '.' not in prop:
                      print('Device Property ',device,'.',prop,', creating: ',value)
                      db.put_device_property(device,{prop:value})
                  else:
                      print('Attribute Property ',device,'.',prop,', creating: ',value)
                      attr,prop = prop.split('.',1)
                      db.put_device_attribute_property(device,{attr:{prop:value}})
              else:
                  print('Device Property ',device,'.',prop,' already exists: ',oldprops[prop])

          # Attribute properties should be managed here
          for attr,props in attr_props.items():
              for p,v in props.items():
                  if '.' in p:
                      raise Exception,'TODO: implement nested dicts smarter'
                      #attr.events
                      np = dict()
                      pp,vv = p.split('.',1)
                      #attr.events.ch_event
                      if '.' in vv:
                          nv,nvv = vv.split('.',1)
                          
                      np[pp] = vv
                      
              fn.tango.set_attribute_config(device,attr,configs)
              
if __name__ == '__main__':
  main()    

