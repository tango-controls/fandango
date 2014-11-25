
#some Linux utilities

"""
<pre>
Executing shell commands and getting the stdout

The module subprocess must be used for that, instead of os.exec* or os.system.

import subprocess
ps = subprocess.Popen('ps uax',shell=True,stdout=subprocess.PIPE)
grep1 = subprocess.Popen('grep -i hdbarchiver',shell=True,stdin=ps.stdout,stdout=subprocess.PIPE)
grep1.communicate()
Out[77]:
('sicilia  13698  0.0  0.0  51000  1552 ?        Ss   Feb23   0:00 SCREEN -dm -S HdbArchiver-palantir01_BO01_VC /homelocal/sicilia/ap\nsicilia   6343  0.0  0.0  50872  2748 pts/13   S+   10:17   0:00 screen -r HdbArchiver-palantir01_BO01_VC\n',
 None)

</pre>
"""

def shell_command(*commands, **keywords):
    """Executes a list of commands linking their stdin and stdouts
    @param commands each argument is interpreted as a command
    @param split returns stdout as a file.readlines() result
    @return the last stdout result"""
    if not commands: return
    elif isinstance(commands,str): commands=[commands]
    split = keywords and 'split' in keywords and keywords['split']
    import subprocess    
    process = [subprocess.Popen(commands[0],shell=True,stdout=subprocess.PIPE)]
    if len(commands)>1:
        for comm in commands[1:]:
            ps = subprocess.Popen(comm,shell=True,stdin=process[-1].stdout,stdout=subprocess.PIPE)
            process.append(ps)
    result = process[-1].communicate() 
    result = (result and len(result)>=1 and result[0]) or None #process returns a tuple, being stdout the first field
    
    ## @remark I know that it could fit in one line ... but I prefer to make it readable
    if not result: return
    elif split: return result.split('\n')
    else: return result
        
        
        
        
def desktop_switcher(period,event=None,iterations=2):
    """ It uses wmctrl to switch between all desktops with a period as specified.
    @param period Time between desktop changes
    @param event Event to stop the application
    @param iterations Number of cycles to execute, -1 for infinite
    """
    import threading    
    if not event:
        event = threading.Event()
    def run():
        ndesks = len([d for d in shell_command('wmctrl -d',split=True) if d])
        i=0
        while True:
            if iterations>0 and i>=ndesks*iterations or event.isSet(): 
                break
            else: i+=1        
            shell_command('wmctrl -s %d'%(i%ndesks))
            event.wait(period)
        return event.isSet()
    thr = threading.Thread(target=run)
    thr.daemon = True #If it is false means that Python will exit if this is the last unfinished thread
    thr.start()
    return True
        
#!/usr/bin/env python2.5

def ping(ips):
    ''' By Noah Gift's, PyCon 2008
    ips =  ['ivc%02d01'%(i+1) for i in range(16)]
    #ips = ["10.0.1.1", "10.0.1.3", "10.0.1.11", "10.0.1.51"]
    '''
    from threading import Thread
    import subprocess
    from Queue import Queue
    if isinstance(ips,str): ips=[ips]
    num_threads = 4
    queue = Queue()
    results = {}
    #wraps system ping command
    def pinger(i, q, r):
        """Pings subnet"""
        while True:
            ip = q.get()
            #print "Thread %s: Pinging %s" % (i, ip)
            ret = subprocess.call("ping -c 1 %s" % ip,
                            shell=True,
                            stdout=open('/dev/null', 'w'),
                            stderr=subprocess.STDOUT)
            #if ret == 0: print "%s: is alive" % ip
            #else: print "%s: did not respond" % ip
            r[ip] = (not ret)
            q.task_done()
    #Spawn thread pool
    for i in range(num_threads):
        worker = Thread(target=pinger, args=(i, queue,results))
        worker.setDaemon(True)
        worker.start()
    #Place work in queue
    for ip in ips:
        queue.put(ip)
    #Wait until worker threads are done to exit    
    queue.join()
    return results
    
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
# time methods
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
import time

def timefun(fun):
    """ This function allow to get time spent by some method calls, use timefun(lambda:f(args)) if needed """
    now = time.time()
    result = fun()
    return (time.time()-now,result)

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
# Managing arguments
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
import sys

def sysargs_to_dict(defaults=[]):
    '''defaults is the list of anonymous arguments to accept'''
    i,n,result = 0,0,{}
    defargs,args = [],sys.argv[1:]
    
    ##First, default arguments (anonymous) are parsed
    while i<min((len(args),len(defaults))) and not (args[i].startswith('-') or '=' in args[i]): i+=1
    if i: defargs,args = args[:i],args[i:]
    [result.update(((defaults[i],a),)) for i,a in enumerate(defargs) if a]
        
    while n<len(args):
        a = args[n]
        if '=' in a: #argument like [-]ARG=VALUE
            while a.startswith('-'): a = a[1:]
            if a: result[a.split('=')[0]] = a.split('=')[1]
        elif a.startswith('-'): #argument with - prefix
            while a.startswith('-'): a = a[1:] 
            if not a: continue
            if (n+1)<len(args) and not args[n+1].startswith('-'): # --OPTION VALUE
                result[a],n = args[n+1],n+1 
            else: result[a]=True # --OPTION for option=True
        n+=1
    return result

def arg_to_bool(arg):
    if type(arg) is str:
        return 'true' in arg.lower() or False
    else:
        return bool(arg)

def expand_args_to_list(args,type_=int):
  result = []
  for arg in args.split(',' in args and ',' or ' '):
    if type_ is int and '-' in arg:
      vals = [type_(v) for v in arg.split('-',1)]
      result.extend(range(*(vals[0],vals[1]+1)))
    elif type_ is int and ':' in arg:
      vals = [type_(v) for v in arg.split(':',2)]
      result.extend(range(*(vals[0],vals[1]+1,vals[2])))
    else: result.append(type_(arg))
  return result

expand_args_to_int_list = lambda args: expand_args_to_list(args,int)
expand_args_to_str_list = lambda args: expand_args_to_list(args,str)
