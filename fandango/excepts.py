from __future__ import with_statement
#!/usr/bin/env python2.5
"""
#############################################################################
##
## file :       excepts.py
##
## description : see below
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

This module excepts provides two ways of simplifying exceptions logging.

ExceptionWrapper is a decorator that provides the @Catched keyword to be added before functions declarations.
    @Catched
    def fun(*args):
        pass
        
ExceptionManager is a Contextmanager object that can be used in a with statement:
    with ExceptionManager():
        fun(args)  
        
The usage of the parameter of the tango throw_exception() method:
This method have 3 parameters which are called (all of them are strings)

- Reason, one word like <TangoClassName>_<OneConstructedWordToSummarizeTheException>
- Desc
- Origin

Example:
    PyTango.Except.throw_exception("PyPLC_ModbusDevNotDef","Modbus Device not defined",inspect.currentframe().f_code.co_name)
    

ADVICE: PyTango.re_throw_exception it's failing a lot, try to use that instead:

    except PyTango.DevFailed, e:
            print e
            #PyTango.Except.re_throw_exception(e,"DevFailed Exception",str(e),inspect.currentframe().f_code.co_name)
            PyTango.Except.throw_exception(str(e.args[0]['reason']),str(e.args[0]['desc']),inspect.currentframe().f_code.co_name+':'+str(e.args[0]['origin']))
 cheers ...     
    
    
# Get the current frame, the code object for that frame and the name of its object
import inspect
print inspect.currentframe().f_code.co_name 
"""

import sys
import traceback
import functools
import contextlib
from fandango import log
from objects import decorator_with_args
import fandango.functional as fun

try:
    from PyTango import DevFailed,Except
except:
    DevFailed,Except = Exception,Exception

def trial(tries,excepts=None,args=None,kwargs=None,return_exception=None):
    """ This method executes a try,except clause in a single line
    :param tries: may be a callable or a list of callables
    :param excepts: it can be a callable, a list of callables, a map of {ExceptionType:[callables]} or just a default value to return	
    :param args,kwargs: arguments to be passed to the callable
    :return exception: whether to return exception or None (default)
    """
    try:
        return_exception = return_exception or (excepts is not None and not any(fun.isCallable(x) for x in fun.toSequence(excepts)))
        tries = fun.toSequence(tries)
        args = fun.toSequence(fun.notNone(args,[]))
        kwargs = fun.notNone(kwargs,{})
        excepts = fun.notNone(excepts,lambda e: log.printf(str(e)))
        result = [t(*args,**kwargs) for t in tries if fun.isCallable(t)]
        return result[0] if len(result)==1 else result
    except Exception,e:
        if fun.isCallable(excepts):
            v = excepts(e)
            return v if return_exception else None
        else:
            if fun.isDictionary(excepts):
                if type(e) in excepts: excepts = excepts.get(type(e))
                elif type(e).__name__ in excepts: excepts = excepts.get(type(e).__name__)
                else:
                    candidates = [t for t in excepts if isinstance(e,t)]
                    if candidates: excepts = excepts[candidates[0]]
                    else: excepts = excepts.get('') or excepts.get(None) or []
            vals = [x(e) for x in fun.toSequence(excepts) if fun.isCallable(x)]
            if return_exception:
               return vals or fun.notNone(excepts,None)

exLogger = log.Logger('fandango',level='WARNING')

def get_current_stack():
    r = []
    for i,line in enumerate(traceback.format_stack()):
        line = line.strip().split('\n')
        for l in line:
            r.append((' '*i)+l)
    return '\n'.join(r)

def getLastException():
    """ returns last exception traceback """
    return str(traceback.format_exc())

#@TODO: These methods failed with python 2.6; to be checked ...
#def get_exception_line(as_str=False):
    #ty,e,tb = sys.exc_info()
    #file,line = tb[-1][:2] if tb else ('',0)
    #result = (file,line,tb)
    #if as_str: return '%s[%d]: %s!'%result
    #else: return result

def exc2str(e):
    if isinstance(e,DevFailed):
        msg=''
        try:
            msg = getattr(e.args[0],'description',e.args[0]['description'])
        except:
            msg = [s for s in str(e).split('\n') if 'desc' in s][0].strip()
        return 'DevFailed(%s)'%msg
    else:
        #return get_exception_line(as_str=True)
        traceback.format_exc(e)

def getPreviousExceptions(limit=0):
    """
    sys.exc_info() returns : type,value,traceback
    traceback.extract_tb(traceback) :  returns (filename, line number, function name, text)
    """
    try:
        exinfo = sys.exc_info()
        if exinfo[0] is not None:
            stack = traceback.format_tb(exinfo[2])
            return str('\n'.join(['Tracebacks (most recent call last):',
                                ''.join(stack[(len(stack)>1 and 1 or 0):]),
                                ': '.join([str(exinfo[0].__name__),str(exinfo[1])])
                                ]))
        else:
            return ''
    except Exception,e:
        print 'Aaaargh!'
        return traceback.format_exc()
    
class RethrownException(Exception):
    pass
    

def ExceptionWrapper(fun,logger=exLogger,postmethod=None, showArgs=False,verbose=True,rethrow=False,default=None):
    ''' 
    Implementation of the popular Catched() decorator:
    
    * it will execute your method within a a try/except
    * it will print the traceback
    * if :rethrow: is False it will return :default: in case of exception
     
    Example:
    @ExceptionWrapper
    def funny():
        print 'what?'
        end
    
    funny()
    '''    
    def wrapper(*args,**kwargs):
        try:
            #logger.trace('Trying %s'%fun.__name__)
            result = fun(*args,**kwargs)
            #logger.trace('%s Succeed!\n'%fun)
            return result
              
        except Exception,e:
            etype = type(e).__name__
            exstring=getPreviousExceptions()
            
            elog,eargs = exstring,('Exception',exstring,"%s(...)"%fun.__name__)
            if isinstance(e,DevFailed):
              try:
                err = e.args[0]
                eargs = (err.reason, exstring, "%s(...)"%fun.__name__)
                elog = str((err.reason,err.desc,err.origin))
              except: pass

            if verbose:
                logger.warning('<'*80)
                logger.error('%s Exception catched: \n%s'%(etype,elog))
                try:
                    if showArgs: logger.info('%s(*args=%s, **kwargs=%s)'%(fun.__name__,args,kwargs))
                except:pass

            if postmethod: 
                ExceptionWrapper(postmethod)(exstring)
                
            if rethrow:
                #Except.re_throw_exception(e,'','',"%s(...)"%fun.__name__)
                logger.warning('%s Rethrow!'%etype)
                Except.throw_exception(*eargs)
            else:
                if isinstance(e,DevFailed) and elog and not verbose and not postmethod: 
                  logger.warning(elog)
                return default
        finally:
            #if verbose: logger.warning('<'*80)
            pass
    
    ##ExceptionWrapper behaves like a decorator
    functools.update_wrapper(wrapper,fun) #it copies all function information to the wrapper
    logger.debug('wrapped(%s) => %s'%(fun,wrapper))
    return wrapper
    
Catched = ExceptionWrapper
CatchedArgs = decorator_with_args(ExceptionWrapper) #stdout may have problems with it
Catched2 = CatchedArgs #For backwards compatibility

class ExceptionManager(object):
    """
    This was a version of ExceptionWrapper to be used as ContextManager together with *with* statement.
    Not really tested nor used, just a proof of concept.
    """
    def __init__(self,logger=exLogger,origin=None,postmethod=None,verbose=True,rethrow=True):
        self.logger=logger
        self.postmethod=postmethod
        self.verbose=verbose
        self.rethrow=rethrow
        self.origin=origin
        pass

    def __enter__(self):
        pass

    #@Catched
    def __exit__(self,etype,e,tb): #Type of exception, exception instance, traceback
        if not e and not etype:
            pass
        else:
            stack = traceback.format_tb(tb)
            exstring = '\n'.join(stack)
            if self.verbose:
                print '-'*80
                self.logger.warning('%s Exception Catched, Tracebacks (most recent call last): %s;\n%s'%(etype.__name__,str(e),exstring))
                sys.stdout.flush(); sys.stderr.flush()
                print '-'*80

            if self.postmethod: self.postmethod(exstring)
            if etype is DevFailed:
                #for k,v in e[0].items():print k,':',v
                if True: #not self.rethrow: #re_throw doesn't work!
                    #The exception is throw just as it was
                    err = e[0]
                    Except.throw_exception(err.reason,err.desc,err.origin)
                    #Except.throw_exception(e.args[0]['reason'],e.args[0]['desc'],e.args[0]['origin'])
                else: #It doesn't work!!!
                    #ex=DevFailed(e[0]['reason'],e[0]['desc'],e[0]['origin'])
                    #Except.re_throw_exception(ex, '','','')
                    pass
            else: #elif etype is Exception:
                exstring = self.origin or len(exstring)<125 and exstring or stack[-1]
                Except.throw_exception(etype.__name__,str(e),exstring)
                
def __test__(args=[]):
  exLogger.setLogLevel('DEBUG')
  exLogger.info('Testing fandango.excepts')

  print('\n')
  exLogger.info('Raise ZeroDivError:\n')
  @Catched
  def failed_f():
    return 1/0.
  failed_f()
  
  print('\n')
  exLogger.info('Show custom message:\n')
  def custom_msg(s):
    print('CUSTOM: %s'%s.split('\n')[-1])
  @CatchedArgs(postmethod=custom_msg,verbose=False)
  def failed_f():
    return 1/0
  failed_f()
  
  def devfailed(d,a):
    import PyTango
    dp = PyTango.DeviceProxy(d)
    return dp.read_attribute(a)
  
  exLogger.info('Try a good tango call:\n')
  Catched(devfailed)('sys/tg_test/1','state')
  print('\n')
  exLogger.info('Try a bad attribute:\n')
  Catched(devfailed)('sys/tg_test/1','nanana')
  print('\n')
  exLogger.info('Raise DevFailed:\n')
  Catched(devfailed)('sys/tg_test/1','throw_exception')
  print('\n')
  exLogger.info('Try a rethrow:\n')
  try:
    CatchedArgs(rethrow=True)(devfailed)('sys/tg_test/1','throw_exception')
  except DevFailed,e:
    exLogger.info('Catched!')

if __name__ == '__main__':
  import sys
  __test__(sys.argv[1:])

from . import doc
__doc__ = doc.get_fn_autodoc(__name__,vars())

