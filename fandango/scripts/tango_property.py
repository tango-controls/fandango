#!/usr/bin/env python

__doc__ = """
Script to obtain the value of a device, class, starter, server or free Tango property

Usage:

  > tango_property OBJECT "*"
  > tango_property VARX=OBJECT1.PropertyA VARY=OBJECT1.PropertyB  
  > tango_property [-e] OBJECT1.PropertyA OBJECT2.PropertyB
  > tango_property [-e] OBJECT Property1 Property2 Property3
  
For exporting environment variables:

  > PROPS=$(tango_property \
            DORB=ORBEndPoint.Server/Instance \
            LcPATH=Starter/$HOST.StartDSPath \
            DfPATH=PYTHON_CLASSPATH.DeviceClasses \
            PyPATH=PYTHON_CLASSPATH.Server)
  > echo $PROPS
    DORB=giop:tcp::50129 LcPATH=/opt/tango/ds:/usr/local/bin
  
  > for p in $PROPS; do export $p ; done
  
-e will insert the property name to the result ( Property=Value )

"""

import fandango

def get_property(obj,prop='',opts=[],var=''):
  #print('get_property(%s)'%str(args))
  if not prop and '.' in obj:
    obj,prop = obj.rsplit('.',1)
    
  db = fandango.tango.get_database()
  
  if obj.lower().startswith('starter/'):
    # Get an Starter property
    obj = fandango.clsub('starter/','tango/admin/',obj.split('.')[0])

  if obj.count('/')>=2:
    # Get a device property
    if '*' in prop:
      value = fandango.tango.get_matching_device_properties(obj,prop).keys()
    else:
      value = db.get_device_property(obj,[prop])[prop]
      
  elif obj.count('/')==1:
    # Get a server property
    value = db.get_device_property('dserver/'+obj,[prop])[prop]    
    
  else:
    # Get a class property
    value = db.get_class_property(obj,[prop])[prop]
    if not value:
      # Get a free property
      value = db.get_property(obj,[prop])[prop]
      
  if fandango.isSequence(value):
    value = (('\n',':')['-e' in opts].join(value)) if fandango.isSequence(value) else value
      
  if var or "-e" in opts:
    value = "%s=%s"%(var or prop,value)
    
  return list(value) if fandango.isSequence(value) else value


def main(args):
  #assert args,'Arguments must be OBJECT.Property'
  if not args:
    print(__doc__)
  else:
    var,obj,opts,vals = '','',set(),[]

    for i,a in enumerate(args):
      if a.startswith('-'):
        opts.add(a)
      else:
        var = ''
        if '.' in a:
          obj,a = a.rsplit('.',1)
          if '=' in obj:
            var,obj = obj.split('=',1)
          vals.append(get_property(obj,prop=a,opts=opts,var=var))
        elif not obj:
          obj = a
        else:
          if '=' in a:
            var,a = a.split('=',1)
          vals.append(get_property(obj,prop=a,opts=opts))
              
    return vals


def main_script():
  import sys
  value = main(sys.argv[1:])
  if not value:
    sys.exit(1)
  else:
    print('\n'.join(value) if fandango.isSequence(value) else value)
    sys.exit(0)


if __name__ == '__main__':
    main_script()
