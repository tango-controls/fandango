
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

import time,sys,os,re
import fandango.functional as fun

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
    
################################################################################3
# Processes methods

def get_memory(pid,virtual=False):
    """This function uses '/proc/pid/status' to get the memory consumption of a process """
    mem,units = shell_command('cat /proc/%s/status | grep Vm%s'%(pid,'Size' if virtual else 'RSS')).lower().strip().split()[1:3]
    return int(mem)*(1e3 if 'k' in units else (1e6 if 'm' in units else 1))
        
def get_process_pid(include,exclude='grep|screen'):
    include = include.replace(' ','.*')
    exclude = exclude.replace(' ','.*')
    lines = [s.strip() for s in shell_command('ps ax | grep -E "%s"'%include+(' | grep -viE "%s"'%exclude if exclude else '')).split('\n')]
    print '\n'.join(lines)
    pids = []
    for l in lines:
        for p in l.split():
            if re.match('[0-9]+',p):
                pids.append(int(p))
                break
    if len(pids)>1:
        raise Exception('Multiple PIDs found: please refine search using exclude argument')
    return pids[0]
    
def KillEmAll(klass):
    processes = shell_command('ps uax').split('\n')
    processes = [s for s in processes if '%s'%(klass) in s]
    for a in processes:
        print 'Killing %s' % a
        pid = a.split()[1]
        shell_command('kill -9 %s'%pid)        
        
################################################################################3
# Filesystem methods

def listdir(folder,mask='.*',files=False,folders=False):
    try:
        if folders and not files:
            vals = os.walk(folder).next()[1]
        elif files and not folders:
            vals = os.walk(folder).next()[2]
        else:
            vals = os.listdir(folder)
        if mask:
            return [f for f in vals if re.match(fun.toRegexp(mask),f)]
        else:
            return vals
    except Exception,e:
        print e
        raise Exception('FolderDoesNotExist',folder)
        
################################################################################3
# Kde methods        
        
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
        
################################################################################3
# Networking methods

def ping(ips,threaded = False, timeout = 1):
    ''' By Noah Gift's, PyCon 2008
    ips =  ['ivc%02d01'%(i+1) for i in range(16)]
    #ips = ["10.0.1.1", "10.0.1.3", "10.0.1.11", "10.0.1.51"]
    '''
    import subprocess
    if isinstance(ips,str): ips=[ips]
    def _ping(ip):
        return not subprocess.call("ping -c 1 -w %d %s" % (int(max((1,timeout))),ip),
                            shell=True,
                            stdout=open('/dev/null', 'w'),
                            stderr=subprocess.STDOUT)     
    if not threaded:
        return dict((ip,_ping(ip)) for ip in ips)
    else:
        from threading import Thread,Event
        from Queue import Queue        
        num_threads,event = 4,Event()
        pool,queue,results = [],Queue(),{}
        #wraps system ping command
        ## WARNING ... THIS IMPLEMENTATION OF THE THREAD IS GIVING A LOT OF PROBLEMS DUE TO THREAD NOT CLOSING! (waiting at q.get())
        def pinger(i, q, r):
            """Pings subnet"""
            while not event.isSet():
                ip = q.get()
                #print "Thread %s: Pinging %s" % (i, ip)
                ret = _ping(ip)
                #if ret == 0: print "%s: is alive" % ip
                #else: print "%s: did not respond" % ip
                r[ip] = (not ret)
                q.task_done()
                event.wait(.01)
        #Spawn thread pool
        for i in range(num_threads):
            pool.append(Thread(target=pinger, args=(i, queue,results)))
            pool[-1].setDaemon(True)
            pool[-1].start()
        #Place work in queue
        for ip in ips: queue.put(ip)
        queue.join() #Wait until worker threads are done to exit
        event.set(),event.wait(.01)
        #[t.join() for t in pool]
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
    ''' 
    It parses the command line arguments into an understandable dict
    defaults is the list of anonymous arguments to accept
    '''
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
  """ it generates a list of args from a sequence like 1,3,5 or 3-7 """
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
