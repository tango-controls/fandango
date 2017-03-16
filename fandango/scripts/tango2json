#!/usr/bin/env python

import fandango as fn
import sys,json,gzip

__doc__ = """
Usage:

 > tango2json.py [--compress] [--commands] [--properties] "filename.json" dev/name/1 "dev/exp/*"
"""

args,params,devs,data = [],[],[],fn.CaselessDict()

t0 = fn.now()
i = 1
source = ''

while i<len(sys.argv):
  a = sys.argv[i]
  if a.startswith('-'): 
    if a == '--source':
      i+=1
      source = sys.argv[i]
    else:
      params.append(a)
  else: 
    args.append(a)
  i+=1

if not args[1:]:
  print(__doc__)
  sys.exit(-1)

if not source:
  for mask in args[1:]:
    devs.extend(fn.get_matching_devices(mask,exported='--properties' not in params))
else:
  raise 'Reading attr config from file not implemented'
  
filename = args[0] if '--compress' not in params else args[0]+'.gz'
  
print('Exporting %d devices to %s'%(len(devs),filename))

for d in devs:
  if d not in data:
    data[d] = fn.tango.export_device_to_dict(d,
            commands = '--commands' in params,
            properties = '--properties' in params
            )
    
data = fn.dict2json(data) #Do not convert, just filters

if '--compress' in params:
  jdata = json.dumps(data,encoding='latin-1')
  f = gzip.open(filename,'wb')
  f.write(jdata)
  f.close()
else:
  json.dump(data,open(filename,'w'),encoding='latin-1')
  
print('Finished in %d seconds.'%(fn.now()-t0))
print(fn.shell_command('ls -lah %s'%filename))
