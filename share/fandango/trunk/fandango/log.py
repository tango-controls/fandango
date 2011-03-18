#!/usr/bin/env python2.5
"""
#############################################################################
##
## file :       log.py
##
## description : see below
##
## project :     Tango Control System
##
## $Author: tcoutinho@cells.es, extended by srubio@cells.es $
##
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

import logging, weakref, traceback
from objects import Object
import warnings


def printf(s):
    # This is a 'lambdable' version of print
    print s
    
class Logger(Object):
    root_inited    = False

    Error    = logging.ERROR
    Warning  = logging.WARNING
    Info     = logging.INFO
    Debug    = logging.DEBUG
    
    def __init__(self, name='', parent=None,format='%(levelname)-8s %(asctime)s %(name)s: %(message)s'):
        self.call__init__(Object)
        self._ForcePrint    = False
        self.__levelAliases    = {'ERROR':self.Error,'WARNING':self.Warning,'INFO':self.Info,'DEBUG':self.Debug}
        
        if not Logger.root_inited:
            #print 'log format is ',format
            self.initRoot(format)
            Logger.root_inited = True
            
        self.log_name = name
        if parent is not None:
            self.full_name = '%s.%s' % (parent.full_name, name)
        else:
            self.full_name = name

        self.log_obj = logging.getLogger(self.full_name)
        self.log_handlers = []

        self.parent = None
        self.children = []
        if parent is not None:
            self.parent = weakref.ref(parent)
            parent.addChild(self)

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

    def setLogLevel(self,level):
        ''' This method allows to change the default logging level'''
        if isinstance(level,basestring): level = level.upper() 
        if level in self.__levelAliases:
            level = self.__levelAliases[level]
            if type(level)==type(logging.NOTSET):
                self.debug('log.Logger: Logging  level set to %s'%str(level).upper())
                self.log_obj.setLevel(level)
            if type(level) is str and level.upper() in logging.__dict__.keys():
                self.debug('log.Logger: Logging  level set to %s'%str(logging.__dict__[level.upper()]))
                self.log_obj.setLevel(logging.__dict__[level.upper()])
        elif level in self.__levelAliases.values():
            self.log_obj.setLevel(level)
        else:
            self.warning('log.Logger: Logging level cannot be set to %s'%str(level))
            pass
        
    setLevel = setLogLevel

    def setLevelAlias(self,alias,level):
        ''' setLevelAlias(alias,level), allows to setup predefined levels for different tags '''
        self.__levelAliases[alias]=level

    def getRootLog(self):
        return logging.getLogger()

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
        try:
            if self._ForcePrint: print 'DEBUG: %s'%msg
            #logging.getLogger().debug(msg, *args, **kw)
            self.log_obj.debug(str(msg).replace('\r',''), *args, **kw)
        except Exception,e:
            print 'Exception in self.debug! \ne:%s\nargs:%s\nkw:%s'%(str(e),str(args),str(kw))
            print traceback.format_exc()            
            #raise e
    
    
    def info(self, msg, *args, **kw):
        try:
            if self._ForcePrint: print 'INFO: %s'%msg
            self.log_obj.info(str(msg).replace('\r',''), *args, **kw)
        except Exception,e:
            print 'Exception in self.info! \ne:%s\nargs:%s\nkw:%s'%(str(e),str(args),str(kw))
            print traceback.format_exc()
            #raise e
     

    def warning(self, msg, *args, **kw):
        try:
            if self._ForcePrint: print 'WARNING: %s'%msg
            self.log_obj.warning(str(msg).replace('\r',''), *args, **kw)
        except Exception,e:
            print 'Exception in self.warning! \ne:%s\nargs:%s\nkw:%s'%(str(e),str(args),str(kw))
            print traceback.format_exc()
            #raise e
            
    def error(self, msg, *args, **kw):
        try:
            if self._ForcePrint: print 'ERROR: %s'%msg
            self.log_obj.error(str(msg).replace('\r',''), *args, **kw)
        except Exception,e:
            print 'Exception in self.error! \ne:%s\nargs:%s\nkw:%s'%(str(e),str(args),str(kw))
            print traceback.format_exc()
            #raise e            
        

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
