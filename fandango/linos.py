#!/usr/bin/env python

#############################################################################
##
## $Author: Sergi Rubio Manrique, srubio@cells.es $
##
## $Revision: 2008 $
##
## copyleft :    ALBA Synchrotron Controls Section, CELLS
##               Bellaterra
##               Spain
##
#############################################################################
##
## This file is part of Tango Control System
##
## Tango Control System is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as published
## by the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## Tango Control System is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
###########################################################################

"""
#some Linux utilities

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

import time,sys,os,re,traceback
import fandango.objects as fun #objects module includes functional
import fandango.log as log
try:
    import psutil
except:
    psutil = None

################################################################################3
# Shell methods

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
            process.append(ps) #comm1 | comm2 | comm3 > result
    result = process[-1].communicate() 
    result = (result and len(result)>=1 and result[0]) or None #process returns a tuple, being stdout the first field
    
    ## @remark I know that it could fit in one line ... but I prefer to make it readable
    if not result: return
    elif split: return result.split('\n')
    else: return result
    
def sendmail(subject,text,receivers,sender='',attachments=None,trace=False):
    # method for sending mails
    if trace: print 'Sending mail to %s'%receivers
    chars = sorted(set(re.findall('[^a-zA-Z0-9/\ \n\.\=\(\),\[\]_\-]',text)))
    for c in chars:
        if c in text and '\\'+c not in text:
            text = text.replace(c,'\\'+c)
    if '\n' in text and '\\n' not in text:
        text = text.replace('\n','\\n')
    receivers = ' '+(receivers if isinstance(receivers,str) else ' '.join(receivers)) 
    sender = sender and " -r %s"%sender
    attachments = attachments and ' '+' '.join('-a %s'%a for a in attachments) or ''
    command = 'echo -e "'+text+'" '
    command += '| mail -s "%s" ' % subject
    #command += '-S from=%s ' % self.FromAddress #'-r %s ' % (self.FromAddress)
    #command += (MAIL_RECEIVER if fandango.isString(MAIL_RECEIVER) else ','.join(MAIL_RECEIVER))
    command += sender + attachments + receivers
    if trace: print(command.rsplit('|',1)[-1])
    os.system(command)
    
################################################################################3
# Platform/Architecture/Hostname methods

class MyMachine(fun.Struct):
    """ This method identifies the current Machine (OS/Arch/Hostname/Kernel) using the platform module """
    def __init__(self):
        import platform
        self.hostname = self.host = platform.node()
        self.dist = platform.dist()
        self.arch = platform.machine()
        self.kernel = platform.release()
        self.os = platform.system()
        self.platform = platform.platform()

################################################################################3
# Processes methods


def get_memstats(units='m'):
    """
    This method returns mem stats in Megabytes
    Remember that in linux buffers and cached memory should be considered FREE
    Dictionary returned is like:
    {   'buffers': '6',
        'cached': '557',
        'free': '16',
        'shared': '0',
        'total': '1002',
        'used': '986'
        }
    """
    txt = shell_command('free -%s'%units)
    txt = txt.split('\n')
    memstats = dict(zip(txt[0].strip().split(),map(int,txt[1].strip().split()[1:])))
    return memstats

def get_free_memory(units='m'):
    stats = get_memstats(units)
    return stats['buffers']+stats['cached']+stats['free']

def get_memory_usage():
    """This method returns the percentage of total memory used in this machine"""
    stats = get_memstats()
    mfree = float(stats['buffers']+stats['cached']+stats['free'])
    return 1-(mfree/stats['total'])

MEMORY_VALUES = []

def get_process_memory(pid=None,virtual=False):
    """
    This function uses '/proc/pid/status'
    to get the memory consumption of a process (current by default)
    """
    try:
        if pid is None: 
            pid = os.getpid()
        if psutil is not None:
            mi = psutil.Process(pid).memory_info()
            return mi.vms if virtual else mi.rss
        else:
            mem,units = shell_command('cat /proc/%s/status | grep Vm%s' 
                % (pid,'Size' if virtual else 'RSS')).lower().strip().split()[1:3]
            units = (('k' in units and 1e3) or ('m' in units and 1e6) 
                    or ('g' in units and 1e9) or 1)
            MEMORY_VALUES.append(int(mem)*units)
            while len(MEMORY_VALUES)>10: 
                MEMORY_VALUES.pop(0)
            return MEMORY_VALUES[-1]
    except:
        print traceback.format_exc()
        return 0

get_memory = get_process_memory

def get_cpu(pid):
    """ Uses ps to get the CPU usage of a process by PID ; it will trigger exception of PID doesn't exist """
    return float(linos.shell_command('ps h -p %d -o pcpu'%pid))
        
def get_process_pid(include='',exclude='grep|screen|kwrite'):
    if not include: return os.getpid()
    include = include.replace(' ','.*')
    exclude = exclude.replace(' ','.*')
    ps = shell_command('ps ax | grep -E "%s"'%include+(' | grep -viE "%s"'%exclude if exclude else ''))
    if not ps: 
        return None #raise Exception('No matching process found')
    lines = [s.strip() for s in ps.split('\n')]
    print '\n'.join(lines)
    pids = []
    for l in lines:
        for p in l.split():
            if re.match('[0-9]+',p):
                pids.append(int(p))
                break
    if len(pids)>1:
        raise Exception('Multiple PIDs found: please refine your search using exclude argument')
    return pids[0]
        
def check_process(pid):
    try: return file_exists('/proc/%s'%pid) #os.kill(pid,0)
    except: return False
        
def kill_process(process=None,signal=15):
    pid = process if fun.isNumber(process) else get_process_pid(process)
    os.kill(pid,signal)
    
def KillEmAll(klass):
    processes = shell_command('ps uax').split('\n')
    processes = [s for s in processes if '%s'%(klass) in s]
    for a in processes:
        print 'Killing %s' % a
        pid = a.split()[1]
        shell_command('kill -9 %s'%pid)        
        
################################################################################3
# Filesystem methods

import os,stat,time

def is_dir(path):
    return stat.S_ISDIR(os.stat(path)[stat.ST_MODE])

def is_link(path):
    mode  = os.lstat(path).st_mode
    return stat.S_ISLNK(mode)

def file_exists(path):
    try: 
        os.stat(path)
        return True
    except:
        return False

def get_file_size(path):
    return os.stat(path)[stat.ST_SIZE]

def listdir(folder,mask='.*',files=False,folders=False,links=False,caseless=True):
    try:
        if folders and not files:
            vals = os.walk(folder,followlinks=links).next()[1]
        elif files and not folders:
            vals = os.walk(folder,followlinks=links).next()[2]
        else:
            vals = os.listdir(folder)
        if mask:
            if caseless:
              return [f for f in vals if fun.clmatch(mask,f)]
            else:
              return [f for f in vals if re.match(fun.toRegexp(mask),f)]
        else:
            return vals
    except Exception,e:
        print e
        raise Exception('FolderDoesNotExist',folder)
 
def copydir(origin,destination,timewait=0.1,overwrite=False):
    """ 
    This method copies recursively a folder, creating subdirectories if needed and exiting at first error.
    Origin and destination must be existing folders.
    It includes a timewait between file copying
    """
    if not file_exists(origin): return
    if not is_dir(origin): return
    fs = listdir(origin)
    print '%s dir contains %d files' % (origin,len(fs))

    def exec_(com):
        print(com)
        r = os.system(com)
        assert not r, 'OS Error %s returned by: %s'%(r,com)
        
    if not file_exists(destination):
        exec_('mkdir "%s"'%(destination))
        
    for f in sorted(fs):
        if is_dir('%s/%s'%(origin,f)):
            #if the file to process is a directory, we create it and process it
            copydir('%s/%s'%(origin,f),'%s/%s'%(destination,f),timewait)
        else:
            #if it was not a directory, we copy it
            if not overwrite and file_exists('%s/%s'%(destination,f)): 
                print '\t%s/%s already exists'%(destination,f)
                continue
            size,t0 = file_size('%s/%s'%(origin,f)),time.time()
            exec_('cp "%s/%s" "%s/"'%(origin,f,destination))
            t1 = time.time()
            if t1>t0: print('\t%f b/s'%(size/(t1-t0)))
        time.sleep(timewait)
        
def diffdir(origin,destination,caseless=False,checksize=True):
    fs,nfs = listdir(origin),listdir(destination)
    lfs,lnfs = [s.lower() for s in fs],[n.lower() for n in nfs]
    missing = []
    for f in sorted(fs):
        df = '%s/%s'%(origin,f)
        if not (f in nfs) and (not caseless or not f.lower() in lnfs):
            print '> %s/%s not in %s'%(origin,f,destination)
            missing.append(df)
        elif is_dir(df):
            missing.extend(diffdir(df,'%s/%s'%(destination,f)))
        elif checksize:
            if file_size(df)!=file_size('%s/%s'%(destination,f)):
                print '---> %s and %s differs!'%(df,'%s/%s'%(destination,nf))
                missing.append(df)
    for n in sorted(nfs):
        if not (n in fs) and (not caseless or not n.lower() in lfs):
            print '>> %s/%s not in %s'%(destination,n,origin)
    return missing
        
def findfolders(target='',parent='',filter_=True,printout = False):
    import os,fandango,stat,re,sys
    result = []
    if not parent: parent = os.getcwd()
    
    if filter_:
        filter_folders = lambda fs: [f for f in fs if f not in '.svn tags branches'.split() and (f.count('/')<6 or not f in 'trunk xpand doc'.split())]
    else: filter_folders = lambda fs: fs
    
    def get_folders(path):
        folders = ['%s/%s'%(path,f) for f in filter_folders(linos.listdir(path,folders=True)) if not stat.S_ISLNK(os.lstat('%s/%s'%(path,f)).st_mode)]
        for f in folders:
            folders.extend(get_folders(f))
        return folders
    
    for f in get_folders():
        if not target or target.lower() in f.lower():
            if printout: print f
            result.append(f)
    return result

def get_disk_usage(folder='.'):
    cmd = 'df -h '+folder
    r = shell_command(cmd).strip('\n').split('\n')[-1].split()
    p = [f for f in r if '%' in f]
    return p and 1e-2*float(p[0].strip('% ')) or 0
    

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

fun.Cached(depth=1000,expire=300.)
def get_fqdn(hostname,keep_alias=True):
    """ Reimplemented to be cached for continuous tango host parsing """
    import socket
    fqdn = socket.getfqdn(hostname)
    if keep_alias:
        fqdn = '.'.join(hostname.split('.')[:1]+fqdn.split('.')[1:])
    return fqdn

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

def timefun(f):
    """ This function allow to get time spent by some method calls, use timefun(lambda:f(args)) if needed """
    now = time.time()
    result = f()
    return (time.time()-now,result)

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
# Managing arguments
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
import sys
try:
    from argparse import ArgumentParser
except:
    pass

def sysargs_to_dict(args=None,defaults=[],alias={},
                    trace=False,split=False,cast=True,lazy=True,multiflag=True,
                    multiarg=[],splitter='='):
    '''  
    DEPRECATED BY argparse.ArgumentParser IN FANDANGO > 13
    https://docs.python.org/3/library/argparse.html
    
    It parses the command line arguments into an understandable dict
    @defaults is the list [and values] of anonymous arguments 
    to accept (would be [] if not specified)
    
    @param split: if True: args,kwargs are returned; if False then {None:[defaults],'option':value} is returned instead
    @param cast: will try to cast all strings to python types
    @param lazy: will accept any A=B as an alternative to -A B
    
    @splitter: override it when '=' must be passed within values
    
    > cmd H=1 --option=value --parameter VALUE1 VALUE2 -test def1 def2
    
    will return
    
    {H:1,option:value,parameter:[V1,V2],test:True,params:[default_arg1,default_arg2]}
    
    getopt, optpase and argparse modules in python provide similar 
    functionality, but are not available in all of our distributions. 
    After Fandango 13 argparse will replace the usage of sysargs_to_dict
    
    '''
    log.debug('sysargs_to_dict is DEPRECATED, use python argparse instead')
    if args is None: args = sys.argv[1:]
    if trace: print 'sysargs_to_dict(%s,%s)'%(args,defaults)
    result,defargs,vargs = {},[],[]
    cast_arg = lambda x: fun.str2type(x,use_eval=True) if cast else x
    is_opt = lambda x: x.startswith('-') or splitter in x
    
    ##Separate parameter/options and unnamed arguments
    if multiarg: defaults.extend(multiarg)
    [args.insert(0,d) for d in defaults if is_opt(d)]
    defaults = [d for d in defaults if not is_opt(d)]
    i,e = 0,len(args)
    while i < e:
        a,l = args[i],vargs
        if lazy and splitter in a:
            # par=2
            pass #by default, added to vargs
          
        elif a.startswith('--'): 
            # --par=2 or --par 2 3 4
            if lazy and i+1<e:
                while lazy and i+1<e and not is_opt(args[i+1]):
                    i+=1
                    a = a+splitter+args[i]
                    
        elif a.startswith('-'):
            # -o or -oXcV
            if multiflag and splitter not in a: a = list(a.strip('-'))
            
        else: 
            l = defargs
        l.extend(a.lstrip('-') for a in fun.toList(a))
        i+=1
        
    for n,a in enumerate(vargs):
        a = a.split(splitter)
        if a: 
            if len(a) == 1: v = True
            elif len(a) == 2: v = cast_arg(a[1])
            else: v = cast_arg(a[1:])
            result[a[0]] = v
      
    defargs = map(cast_arg,defargs)
    if trace: print('defargs: %s'%defargs)
    if trace: print('defaults: %s'%defaults)
    
    defaults = [d.strip('-') for d in defaults if d.strip('-') not in result]
    if len(defaults)==1 and len(defargs)>1:
        result[defaults[0]] = defargs
    else:
        result[None] = defargs[len(defaults):]
        result.update(zip(defaults,defargs))
        result.update((d,False) for d in defaults if d not in result)
    
    if trace: print result
    if len(result)==1 and None in result: split = True
    
    if not split:
        return result
      
    else:
        args = result.pop(None,[])
        kwargs = result
        return args,kwargs

def arg_to_bool(arg):
    if type(arg) is str:
        return arg.lower() in ('true','yes') or False
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

if __name__ == '__main__':
    import sys
    #print sysargs_to_dict(defaults=['params'],cast=False,split=True)
    print sysargs_to_dict.__name__,'\n',sysargs_to_dict.__doc__
    print sysargs_to_dict(cast=False,split=True)

#from . import doc
from fandango.doc import get_fn_autodoc
__doc__ = get_fn_autodoc(__name__,vars())

