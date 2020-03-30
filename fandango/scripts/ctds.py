#!/usr/bin/python

import fandango
import sys
import time
import traceback

print """
DEPRECATED: This script has been replaced by tango_servers
"""

COMMANDS = 'list search status start stop restart create export put'.split()
__doc__ = USAGE = 'USAGE: ctds <list|search|status|start|stop|restart|create|export|put> [servers....]'

def main():

  args = fandango.sysargs_to_dict(sys.argv[1:],defaults=['keys'],trace=False, cast=False)

  if not args['keys'] or len(args['keys'])<2 or args['keys'][0] not in COMMANDS:
      print USAGE
      sys.exit()

  action,keys = args['keys'][0],args['keys'][1:]

  try:
      if action in "status start stop restart":
          astor = fandango.Astor()
          [astor.load_by_name(k) for k in keys]
          if action == 'list':
              print '\n'.join(sorted(astor.keys()))
          if action == 'status': 
              astor.states()
              print astor.__repr__()
          elif action == 'start': 
              astor.start_servers()
          elif action == 'stop': 
              astor.stop_servers()
          elif action == 'restart':
              print('Stopping servers ...')
              astor.stop_servers()
              print('Waiting 10 s ...')
              time.sleep(10.)
              print('Starting servers ...')
              astor.start_servers()
      elif action == 'create':
          print('Creating a new server: %s'%keys)
          server,klass,device = keys
          fandango.tango.add_new_device(server,klass,device)
      elif action == 'export':
          matches = {}
          for k in keys:
              matches[k] = (fandango.tango.export_device_to_dict(k))
          print(matches)
      elif action == 'search':
          matches = []
          [matches.extend(fandango.TGet(k)) for k in keys]
          print(' '.join(sorted(matches))) 
      elif action == 'put':
          if len(keys) == 3:
              device,prop,value = keys
              fandango.tango.put_device_property(device,{prop:value})
          else:
              raise Exception('not supported yet, sorry')
  except:
      traceback.print_exc()
    
if __name__ == '__main__':
  main()    
