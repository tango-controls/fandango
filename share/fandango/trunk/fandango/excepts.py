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
import PyTango
from . import log
import fandango.functional as fun

def trial(tries,excepts):
    """ This method executes a try,except clause in a single line
    :param tries: may be a callable or a list of callables
    :param excepts: it can be a callable, a list of callables or a map of {ExceptionType:[callables]}
    """
    try:
        tries = fun.toSequence(tries)
        [t() for t in tries if fun.isCallable(t)]
    except Exception,e:
        if fun.isDictionary(excepts):
            if type(e) in excepts: excepts = excepts.get(type(e))
            elif type(e).__name__ in excepts: excepts = excepts.get(type(e).__name__)
            else:
                candidates = [t for t in excepts if isinstance(e,t)]
                if candidates: excepts = excepts[candidates[0]]
                else: excepts = excepts.get('') or excepts.get(None) or []
        excepts = fun.toSequence(excepts)
        [x() for x in excepts if fun.isCallable(x)]

def decorator_with_args(decorator):
    '''
    Decorator with Arguments must be used with parenthesis: @decorated() 
    , even when arguments are not used!!!
    '''
    # decorator_with_args = lambda decorator: lambda *args, **kwargs: lambda func: decorator(func, *args, **kwargs)
    return lambda *args, **kwargs: lambda func: decorator(func, *args, **kwargs)

exLogger = log.Logger()

def getLastException():
    return str(traceback.format_exc())

"""
@TODO: These methods failed with python 2.6; to be checked ...

def get_exception_line(as_str=False):
    ty,e,tb = sys.exc_info()
    file,line = tb[-1][:2] if tb else ('',0)
    result = (file,line,tb)
    if as_str: return '%s[%d]: %s!'%result
    else: return result

def exc2str(e):
    if isinstance(e,PyTango.DevFailed):
        msg=''
        try:
            msg = getattr(e.args[0],'description',e.args[0]['description'])
        except:
            msg = [s for s in str(e).split('\n') if 'desc' in s][0].strip()
        return 'DevFailed(%s)'%msg
    else:
        return get_exception_line(as_str=True)
"""

def getPreviousExceptions(limit=0):
    """
    sys.exc_info() returns : type,value,traceback
    traceback.extract_tb(traceback) :  returns (filename, line number, function name, text)
    """
    try:
        exinfo = sys.exc_info()
        if exinfo[0] is not None:
            stack = traceback.format_tb(exinfo[2])
            return '\n'.join(['Tracebacks (most recent call last):',
                                ''.join(stack[(len(stack)>1 and 1 or 0):]),
                                ': '.join([str(exinfo[0].__name__),str(exinfo[1])])
                                ])
        else:
            return ''
    except Exception,e:
        print 'Aaaargh!'
        return traceback.format_exc()

#@decorator_with_args #This decorator disturbed stdout!!!! ... There's a problem calling nested decorators!!!
def ExceptionWrapper(fun,logger=exLogger,postmethod=None, showArgs=False,verbose=False,rethrow=False):
    ''' Example:
    @ExceptionWrapper
    def funny():
        print 'what?'
        end
    
    funny()
    '''    
    def wrapper(*args,**kwargs):
        try:
            #logger.debug('Trying %s'%fun.__name__)
            result = fun(*args,**kwargs)
            #sys.stdout.write('fun DONE!!!\n')
            return result
        except PyTango.DevFailed, e:
            exstring=getPreviousExceptions()            
            if verbose:
                print '-'*80
                #exstring = traceback.format_exc()
                logger.warning('PyTango.DevFailed Exception Catched: \n%s'%exstring)
                try:
                    if showArgs: logger.info('%s(*args=%s, **kwargs=%s)'%(fun.__name__,args,kwargs))
                except:pass
                sys.stdout.flush(); sys.stderr.flush()
                print '-'*80

            if postmethod: postmethod(exstring)
            err = e.args[0]
            if rethrow:
                #PyTango.Except.re_throw_exception(e,'','',"%s(...)"%fun.__name__)
                PyTango.Except.throw_exception(err.reason, exstring, "%s(...)"%fun.__name__)
            else:
                PyTango.Except.throw_exception(err.reason,err.desc,err.origin)
        except Exception,e:
            #exstring = traceback.format_exc()
            exstring=getPreviousExceptions()
            if verbose:
                print '-'*80
                logger.error('Python Exception catched: \n%s'%exstring)
                try:
                    if showArgs: logger.info('%s(*args=%s, **kwargs=%s)'%(fun.__name__,args,kwargs))
                except:pass
                print '-'*80                                 
            if postmethod: postmethod(exstring)
            PyTango.Except.throw_exception('Exception',exstring,"%s(...)"%fun.__name__)
        pass    
    
    #ExceptionWrapper behaves like a decorator
    functools.update_wrapper(wrapper,fun) #it copies all function information to the wrapper
    return wrapper
    
Catched = ExceptionWrapper
Catched2 = decorator_with_args(ExceptionWrapper)

class ExceptionManager(object):
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
            if etype is PyTango.DevFailed:
                #for k,v in e[0].items():print k,':',v
                if True: #not self.rethrow: #re_throw doesn't work!
                    #The exception is throw just as it was
                    err = e[0]
                    PyTango.Except.throw_exception(err.reason,err.desc,err.origin)
                    #PyTango.Except.throw_exception(e.args[0]['reason'],e.args[0]['desc'],e.args[0]['origin'])
                else: #It doesn't work!!!
                    #ex=PyTango.DevFailed(e[0]['reason'],e[0]['desc'],e[0]['origin'])
                    #PyTango.Except.re_throw_exception(ex, '','','')
                    pass
            else: #elif etype is Exception:
                exstring = self.origin or len(exstring)<125 and exstring or stack[-1]
                PyTango.Except.throw_exception(etype.__name__,str(e),exstring)
