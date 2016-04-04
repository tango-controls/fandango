#!/usr/bin/python

import fandango
import sys
import time

COMMANDS = 'status start stop restart init load'.split()
__doc__ = usage = 'USAGE: sardanact <%s> [filter]'%'|'.join(COMMANDS)

def main():
  args = fandango.sysargs_to_dict(sys.argv[1:],defaults=['action','filter'],trace=False)
  if args.get('action',None) not in COMMANDS:
      print(usage)
      sys.exit()

  keys = ('pool','macroserver')
  action,filters = args.get('action',None),args.get('filter','*')
  astor = fandango.Astor()
  [astor.load_by_name(k) for k in keys]
  target = sorted(k for k in astor if fandango.searchCl(filters,k))

  if action == 'status': 
      astor.states()
      print astor.__repr__()
  elif action == 'start': 
      print('Starting %s'%target)
      astor.start_servers()
  elif action == 'stop': 
      print('Stopping %s'%target)
      astor.stop_servers()
  elif action == 'restart':
      astor.stop_servers()
      print('Stopping %s'%target)
      print('Waiting 10 s ...')
      time.sleep(10.)
      print('Starting %s'%target)
      astor.start_servers()
    
if __name__ == '__main__':
  main()    