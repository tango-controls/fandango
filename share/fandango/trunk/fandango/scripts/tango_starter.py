#!/usr/bin/env python

import sys,time,traceback
import fandango

__doc__ = """
tango_starter.py
----------------

This script uses fandango.servers.ServersDict class to start/stop devices on any point of the control system using Tango Starters.

  tango_starter.py [host] start|stop|restart|status [server_name_expression_list]

Examples:

  tango_starter.py status              # Will display status of devices in localhost
  tango_starter.py hostname.you.org stop "*hdb*"    # Will stop all *hdb* devices in hostname.you.org
  tango_starter.py restart "pyalarm/*"     # Will restart PyAlarm devices in ALL hosts
"""

actions = 'start stop restart status'.split()

try:
    host = sys.argv[1] if not sys.argv[1] in actions else ''
    action = fandango.first([a for a in sys.argv if a in actions] or 'status')
    targets = sys.argv[(2 if sys.argv[1] in actions else 3):]
except:
    print __doc__
    sys.exit(1)
    
action,targets = sys.argv[1],sys.argv[2:]
try:
    astor = fandango.Astor()
    if targets:
        for exp in targets:
            print 'Loading %s devices'%exp
            astor.load_by_name(exp)
    else:
        h = host or fandango.MyMachine().host
        print 'Loading %s devices'%h
        astor.load_by_host(h)
        
    sts = astor.states()
    running = [s for s,st in sts.items() if st is not None]
    if action in ('status',):
        #if targets:
            #print '\n'.join(sorted('%s:\t%s'%(k,str(v)) for k,v in sts.items()))
        #else:
        for h,ls in sorted(astor.get_host_overview().items()):
            for l,ds in sorted(ls.items()):
                print '%s:%s'%(h,l)
                for s,devs in sorted(ds.items()):
                    print '\t'+s
                    for d,st in sorted(devs.items()):
                        print '\t\t%s:\t%s'%(d,st)

    if action in ('stop','restart'):
        astor.stop_servers(running)
    if action in ('restart',):
        time.sleep(5)
        sts = astor.states()
    if action in ('start',):
        astor.start_servers(running,**(host and {'host':host} or {}))
    
    print '-'*80
    print(' '.join(sys.argv)+': Done')  
except:
    print traceback.format_exc()
    print '-'*80
    print(' '.join(sys.argv)+': Failed!')   
