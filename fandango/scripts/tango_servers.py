#!/usr/bin/env python

import sys,time,traceback
import fandango as fn

__doc__ = """
tango_servers
-------------

This script uses fn.servers.ServersDict class to start/stop devices on any point of the control system using Tango Starters.

  tango_servers [host] start|stop|kill|restart|status [server_name_expression_list]
  
Examples:

  tango_servers status              # Will display status of devices in localhost
  tango_servers hostname.you.org stop "*hdb*"    # Will stop all *hdb* devices in hostname.you.org
  tango_servers restart "pyalarm/*"     # Will restart PyAlarm devices in ALL hosts
  
NOTE: ctds and tango_admin scripts provide similar functionality

"""

def main(args = []):
  actions = 'start stop kill restart status states'.split()
  args = [] or sys.argv[1:]
  opts = [a for a in args if a.startswith('-')]
  args = [a for a in args if a not in opts]
  
  try:
      assert 'help' not in str(opts+args)
      host = args[0] if args[0] not in actions else ''
      action = fn.first([a for a in args if a in actions] or [''])
      targets = args[bool(host)+bool(action):]
      action = action or 'status' #order matters
  except:
      print __doc__
      sys.exit(1)
      
  print('%s of %s at %s'%(action,targets,host or '*'))
  
  try:
      astor = fn.Astor()
      if targets:
          for exp in targets:
              print('Loading %s devices\n'%exp)
              astor.load_by_name(exp)
      else:
          h = host or fn.MyMachine().host
          print('Loading %s devices\n'%h)
          astor.load_by_host(h)
          
      sts = astor.states()
      if action in ('status','states','info','list'):
          if targets:
              for k,v in sorted(astor.items()):
                print('%s (%s):\t%s'%(k,v.host,str(sts[k])))
                try:
                  for d,s in sorted(v.get_all_states().items()):
                    print('\t%s:\t%s'%(d,str(s)))
                except: pass
                print('')

          else:
            for h,ls in sorted(astor.get_host_overview().items()):
                print('Note: Devices not controlled by Astor will not appear in this report\n\n')
                for l,ds in sorted(ls.items()):
                    print '%s:%s'%(h,l)
                    for s,devs in sorted(ds.items()):
                        print '\t'+s
                        for d,st in sorted(devs.items()):
                            print '\t\t%s:\t%s'%(d,st)
                print('')

      matched = [s for s in astor] # if not targets or fn.clmatch(targets[0],s)]
      running = [s for s,st in sts.items() if st is not None]
      
      if action in ('kill',):
          print('Killing : %s'%matched)
          astor.kill_servers(matched)
      if action in ('stop','restart'):
          print('Stopping : %s'%running)
          conf = raw_input(('%d servers will be stop:\n\t%s' % (
            len(running),'\n\t'.join(running)))
            + '\nIs it ok? (y/n)')
          if conf.lower().strip() in ('y','yes'):
            astor.stop_servers(running)
      if action in ('restart',):
          time.sleep(15.)
      if action in ('start','restart'):
          print('Starting : %s'%matched)
          if not host and not all(astor[h].host for h in matched):
              not_match = [a for a in matched if not astor[h].host]
              conf = raw_input('Some servers (%s) will be started locally,'
                               ' is it ok? (y/n)' % not_match)
          else:
              conf = 'y'
          if conf.lower().strip() in ('y','yes'):
              astor.start_servers(matched,**(host and {'host':host} or {}))
      
      print('-'*80)
      print(' '.join(sys.argv)+': Done')  
  except:
      print traceback.format_exc()
      print('-'*80)
      print(' '.join(sys.argv)+': Failed!')   
      
if __name__ == '__main__':
  main()
