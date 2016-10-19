#!/usr/bin/env python

#############################################################################
##
## project :     Tango Control System
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
    
Example of usage:
class logged_class(Logger):
    def __init__(self,name,system):
        #parent must be also an instance of a Logger object
        self.call__init__(Logger,name,parent=system)
        pass
    ...

Example of logging:
In [17]: import logging  
In [18]: l = logging.getLogger("something")
In [19]: l.debug("message")
In [20]: l.error("message")
No handlers could be found for logger "something"   
In [21]: l.addHandler(logging.StreamHandler())
In [22]: l.error("message")
message

"""

import time, logging, weakref, traceback, sys
from objects import Object,Decorator
from pprint import pprint
from functional import \
  time2str,first,matchCl,isSequence,isMapping,isCallable,isString
import warnings


def printf(*args):
    # This is a 'lambdable' version of print
    print(''.join(map(str,args)))
    
def printerr(*args):
    sys.stderr.write(*args)
    
def shortstr(s,max_len=144):
    s = str(s)
    if max_len>0 and len(s) > max_len:
        s = s[:max_len-3]+'...'
    return s
    
def except2str(e=None,max_len=int(7.5*80)):
    if e is None: e = traceback.format_exc()
    e = str(e)
    if 'desc=' in e or 'desc =' in e:
        r,c = '',0
        for i in range(e.count('desc')):
            c = e.index('desc',c)+1
            r+=e[c-15:c+max_len-18]+'...\n'
        result =  r
    else: 
        result = str(e)[-(max_len-3):]+'...'
    return result or e[:max_len]
  
def test2str(obj,meth='',args=[],kwargs={}):
    """
    Executes a method providing a verbose output.
    For usage examples see fandango.device.FolderDS.FolderAPI.__test__()
    """
    fs = str(obj) if not meth else '%s.%s'%(obj,meth)
    r = 'Testing %s(*%s,**%s)\n\n' % (fs,args,kwargs)
    v = None
    try:
      f = getattr(obj,meth) if meth and isString(meth) else (meth or obj)
      v = f(*args,**kwargs)
      if isMapping(v):
        s = '\n'.join(map(str,v.items()))
      elif isSequence(v):
        s = '\n'.join(map(str,v))
      else: s = str(v)
    except:
      s = traceback.format_exc()
    r += '\n'.join('\t%s'%l for l in s.split('\n'))+'\n\n'
    return r,v
  
def printtest(obj,meth='',args=[],kwargs={}):
    """
    Executes a method providing a verbose output.
    For usage examples see fandango.device.FolderDS.FolderAPI.__test__()
    """
    r,v = test2str(obj,meth,args,kwargs)
    print(r)
    return v

ERROR,WARNING,INFO,DEBUG = logging.ERROR,logging.WARNING,logging.INFO,logging.DEBUG
LogLevels = {'ERROR':ERROR,'WARNING':WARNING,'INFO':INFO,'DEBUG':DEBUG,}
  
class FakeLogger():
    """
    This class just simulates a Logger using prints with date and header, it doesn't allow any customization
    """
    _instances = []
    def __init__(self,header='',keep=False):
        self.LogLevel = 1
        self.header = '%s: '%header if header else ''
        if keep: self._instances.append(self)
    def setLogLevel(self,s):
        self.LogLevel = str(s).lower()!='DEBUG'
    def trace(self,s):
        if not self.LogLevel:
          print time2str()+' '+'TRACE\t'+self.header+s
    def debug(self,s):
        if not self.LogLevel:
          print time2str()+' '+'DEBUG\t'+self.header+s
    def info(self,s):print time2str()+' '+'INFO\t'+self.header+s
    def warning(self,s):print time2str()+' '+'WARNING\t'+self.header+s
    def error(self,s):print time2str()+' '+'ERROR\t'+self.header+s
    
class Logger(Object):
    """
    This class provides logging methods (debug,info,error,warning) to all classes inheriting it.
    To use it you must inherit from it and add it within your __init__ method:
    
    def __init__(self,cl, name):
        PyTango.Device_4Impl.__init__(self,cl,name)
        self.call__init__(fandango.log.Logger,name,format='%(levelname)-8s %(asctime)s %(name)s: %(message)s')
    
    Constructor arguments allow to customize the output format:
     * name='fandango.Logger' #object name to appear at the beginning
     * parent=None
     * format='%(levelname)-8s %(asctime)s %(name)s: %(message)s'\
     * use_tango=True #Use Tango Logger if available
     * use_print=True #Use printouts instead of linux logger (use_tango will override this option)
     * level='INFO' #default log level
     * max_len=0 #max length of log strings
    """
    
    root_inited    = False
    Error    = ERROR
    Warning  = WARNING
    Info     = INFO
    Debug    = DEBUG
    
    def __init__(self, name='fandango.Logger', parent=None,\
          format='%(levelname)-8s %(asctime)s %(name)s: %(message)s',\
          use_tango=True,use_print=True,level='INFO',max_len=0):
      
        self.max_len = max_len
        self.call__init__(Object)
        self.__levelAliases = LogLevels.copy()
        
        self.log_name = name
        if parent is not None:
            self.full_name = '%s.%s' % (parent.full_name, name)
        else:
            self.full_name = name
            
        self.log_obj = logging.getLogger(self.full_name)
        self.log_handlers = []

        self.use_tango = use_tango and hasattr(self,'debug_stream')
        self._ForcePrint = use_print
        
        self.parent = None
        self.children = []
        if parent is not None:
            self.parent = weakref.ref(parent)
            parent.addChild(self)
        self.setLogLevel(level)
        
        if not Logger.root_inited:
            #print 'log format is ',format
            self.initRoot(format)
            Logger.root_inited = True
            
    def __del__(self):
        parent = self.getParent()
        if parent is not None:
            parent.delChild(self)

    def initRoot(self,_format='%(threadName)-12s %(levelname)-8s %(asctime)s %(name)s: %(message)s'):
        logging.basicConfig(level=logging.INFO,format=_format)
        #logging.basicConfig(level=logging.DEBUG,                           
#                            format='%(threadName)-12s %(levelname)-8s %(asctime)s %(name)s: %(message)s')        

    def setLogPrint(self,force):
        ''' This method enables/disables a print to be executed for each log call '''
        self._ForcePrint=force
        
    def getTimeString(self,t=None):
        if t is None: t=time.time()
        cad='%Y-%m-%d %H:%M:%S'
        s = time.strftime(cad,time.localtime(t))
        ms = int((t-int(t))*1e3)
        return '%s.%d'%(s,ms)
        
    def logPrint(self,prio,msg):
        name = self.log_name+'.' if self.log_name else ''
        l = self.__levelAliases.get(prio,prio)
        if l<self.log_obj.level: return
        print ('%s%s\t%s\t%s'%(name,prio,self.getTimeString(),str(msg).replace('\r','')))

    def setLogLevel(self,level):
        ''' This method allows to change the default logging level'''
        #if isinstance(level,basestring): level = level.upper() 
        if type(level)==type(logging.NOTSET):
            self.log_obj.setLevel(level)
            self.debug('log.Logger: Logging  level set to %s'%str(level).upper())
        else:
            l = self.getLogLevel(level)
            if l is not None:
                self.log_obj.setLevel(l)
                self.debug('log.Logger: Logging  level set to "%s" = %s'%(level,l))
            else:
                self.warning('log.Logger: Logging level cannot be set to "%s"'%level)
        return level
        
    setLevel = setLogLevel

    def setLevelAlias(self,alias,level):
        ''' setLevelAlias(alias,level), allows to setup predefined levels for different tags '''
        self.__levelAliases[alias]=level
        
    def getLogLevel(self,alias=None):
        if alias is None:
            l = self.log_obj.level
            try: l = (k for k,v in self.__levelAliases.iteritems() if v==l).next()
            except: return l
        else:
            if not isinstance(alias,basestring):
                try: return (k for k,v in self.__levelAliases.iteritems() if v==alias).next()
                except: return None
            elif alias.lower() in ('debug','info','warning','error'):
                return logging.__dict__.get(alias.upper())
            else:
                try: return (v for k,v in self.__levelAliases.iteritems() if k.lower()==alias.lower()).next()
                except: return None
        return

    def getRootLog(self):
        return logging.getLogger()
    
    def getTangoLog(self):
        if not self.use_tango: return None
        if getattr(self,'__tango_log',None): return self.tango_obj
        try:
            #import PyTango
            #if PyTango.Util.instance().is_svr_starting(): return None
            self.get_name() #Will trigger exception if Tango object is not ready
            self.__tango_log = self
        except:
            print(traceback.format_exc())
            self.warning('Unable to setup tango logging for %s'%self.log_name)
            self.__tango_log = None
        return self.__tango_log

    def getParent(self):
        if self.parent is None:
            return None
        return self.parent()

    def getChildren(self):
        children = []
        for ref in self.children:
            child = ref()
            if child is not None:
                children.append(child)
        return children
        
    def addChild(self, child):
        ref = weakref.ref(child)
        if not ref in self.children:
            self.children.append(ref)
        
    def delChild(self, child):
        ref = weakref.ref(child)
        if ref in self.children:
            self.children.remove(ref)

    def __eq__(self, other):
        return self is other

    def addLogHandler(self, handler):
        self.log_obj.addHandler(handler)
        self.log_handlers.append(handler)

    def copyLogHandlers(self, other):
        for handler in other.log_handlers:
            self.addLogHandler(handler)
            
    def output(self, msg, *args, **kw):
        self.log_obj.log(Logger.Output, msg, *args, **kw)
    
    def debug(self, msg, *args, **kw):
        self.sendToStream(msg,'debug',3,*args,**kw)
        
    def trace(self, msg, *args, **kw):
        self.sendToStream(msg,'debug',3,*args,**kw)
    
    def info(self, msg, *args, **kw):
        self.sendToStream(msg,'info',2,*args,**kw)

    def warning(self, msg, *args, **kw):
        self.sendToStream(msg,'warning',1,*args,**kw)
            
    def error(self, msg, *args, **kw):
        self.sendToStream(msg,'error',0,*args,**kw)
            
    def sendToStream(self,msg,level,prio,*args,**kw):
        #stream should be a number in trace=4,debug=3,info=2,warning=1,error=0
        try:
            prio = min(prio,3)
            if self.max_len>0: msg = shortstr(msg,self.max_len)
            msg = str(msg).replace('\r','').replace('%','%%')
            obj = self.getTangoLog()
            if obj: 
                stream = (obj.error_stream,obj.warn_stream,obj.info_stream,obj.debug_stream)[prio]
                stream(msg, *args, **kw)
            elif self._ForcePrint: 
                self.logPrint(level.upper(),msg)
            else: 
                stream = (self.log_obj.error,self.log_obj.warning,self.log_obj.info,self.log_obj.debug)[prio]
                stream(msg, *args, **kw)
        except Exception,e:
            print 'Exception in Logger.%s! \nmsg:%s\ne:%s\nargs:%s\nkw:%s'%(level,msg,e,str(args),str(kw))
            print traceback.format_exc()
        

    def deprecated(self, msg, *args, **kw):
        filename, lineno, func = self.log_obj.findCaller()
        depr_msg = warnings.formatwarning(msg, DeprecationWarning, filename, lineno)
        self.log_obj.warning(depr_msg, *args, **kw)

    def flushOutput(self):
        self.syncLog()

    def syncLog(self):
        logger = self
        synced = []
        while logger is not None:
            for handler in logger.log_handlers:
                if handler in synced:
                    continue
                try:
                    sync = getattr(handler, 'sync')
                except:
                    continue
                sync()
                synced.append(handler)
            logger = logger.getParent()          

    def changeLogName(self,name):
        """Change the log name.""" 
        p = self.getParent()
        if p is not None:
            self.full_name = '%s.%s' % (p.full_name, name)
        else:
            self.full_name = name
        
        self.log_obj = logging.getLogger(self.full_name)
        for handler in self.log_handlers:
            self.log_obj.addHandler(handler)
        
        for child in self.getChildren():
            self.changeLogName(child.log_name)

class LogFilter(logging.Filter):

    def __init__(self, level):
        self.filter_level = level
        logging.Filter.__init__(self)

    def filter(self, record):
        ok = (record.levelno == self.filter_level)
        return ok

__doc__ += """
fandango.logger submodule provides a default Logger instance
and its info/debug/warning/error/trace methods directly available
as module methods.

  import fandango.log
  fandango.log.info('just a test')
  fandango.Logger.INFO    2016-02-19 11:49:55.609 just a test
"""

_LogLevel = 'INFO'
for a in sys.argv:
  if a.startswith('--log-level='):
    _LogLevel = a.split('=')[-1].upper()
    
_Logger = Logger(level=_LogLevel)
info = _Logger.info
debug = _Logger.debug
warning = _Logger.warning
error = _Logger.error
trace = _Logger.trace


class InOutLogged(Decorator):
  """
  This class provides an easy way to trace whenever python enter/leaves
  a function.
  """
  
  def __call__(self,*args,**kwargs):
    debug('In %s(%s,%s)'%(self.f.__name__,args,kwargs,))
    r = self.f(*args,**kwargs)
    debug('Out of '+self.f.__name__)
    return r
