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
provides tango utilities for fandango, like database search methods and emulated Attribute Event/Value types

This module is a light-weight set of utilities for PyTango.
Classes dedicated for device management will go to fandango.device
Methods for Astor-like management will go to fandango.servers

.. contents::

.

"""

from .methods import *

##############################################################################################################
## Tango Command executions

class TangoCommand(object):
    """
    This class encapsulates a call to a Tango Command, it manages asynchronous commands in a background thread or process.
    It also allows to setup a "feedback" condition to validate that the command has been executed.
    
    The usage would be like::
    
      tc = TangoCommand('move',DeviceProxy('just/a/motor'),asynch=True,process=False)
      
      #In this example the value of the command will be returned once the state will change
      result = tc(args,feedback='state',expected=PyTango.DevState.MOVING,timeout=10000)
      
      #In this other example, it will be the value of the state what will be returned
      result = tc(args,feedback='state',timeout=10000)
      
    :param command: the name of a tango command; or a callable
    :param device: a device that can be an string, a DeviceProxy or a TaurusDevice
    :param timeout: when using asynchronous commands default timeout can be overriden
    :param feedback: attribute, command or callable to be executed
    :param expected: if not None, value that feedback must have to consider the command successful
    :param wait: time to wait for feedback (once command has been executed)
    :param asynch: to perform the wait in a different thread instead of blocking
    :param process: whether to use a different process to execute the command (if CPU intensive or trhead-blocking)
    :
    """
    
    class CommandException(Exception): pass
    class CommandTimeout(Exception): pass
    class BadResult(Exception): pass
    class BadFeedback(Exception): pass
    Proxies = ProxiesDict()
    
    def __init__(self,command,device=None,timeout=None,feedback=None,expected=None,wait=3.,asynch=True,process=False):
        
        self.device = device
        self.proxy = TangoCommand.Proxies[self.device]
        if isinstance(command,basestring):
            if '/' in command:
                d,self.command = command.rsplit('/',1)
                if not self.device: self.device = d
            else: self.command = command
            self.info = self.proxy.command_query(self.command)
        else: #May be a callable
            self.command,self.info = command,None
            
        self.timeout = timeout or 3.
        self.feedback = feedback and self._parse_feedback(feedback)
        self.expected = expected
        self.wait = wait
        self.asynch = asynch
        self.process = process
        
        self.event = threading.Event()
        if process:
            import fandango.threads
            self.process = fandango.threads.WorkerThread(device+'/'+command,process=True)
        else:
            self.process = None
        pass
        
    def trace(self,msg,severity='DEBUG'):
        print '%s %s fandango.TangoCommand: %s'%(severity,time.ctime(),msg)
    
    def _parse_feedback(self,feedback):
        if isCallable(feedback):
            self.feedback = feedback
        elif isinstance(feedback,basestring):
            if '/' in feedback:
                device,target = feedback.rsplit('/',1) if feedback.count('/')>=(4 if ':' in feedback else 3) else (feedback,state)
            else:
                device,target = self.device,feedback
            proxy = TangoCommand.Proxies[device]
            attrs,comms = proxy.get_attribute_list(),[cmd.cmd_name for cmd in proxy.command_list_query()]
            if inCl(target,comms):
                self.feedback = (lambda d=device,c=target: TangoCommand.Proxies[d].command_inout(c))
            elif inCl(target,attrs):
                self.feedback = (lambda d=device,a=target: TangoCommand.Proxies[d].read_attribute(a).value)
            else:
                raise TangoCommand.CommandException('UnknownFeedbackMethod_%s'%feedback)
        return self.feedback

    def __call__(self,*args,**kwargs):
        self.execute(*args,**kwargs)
    
    def execute(self,args=None,timeout=None,feedback=None,expected=None,wait=None,asynch=None):
        self.trace('%s/%s(%s)'%(self.device,self.command,args or ''))
        #args = (args or []) #Not convinient
        timeout = notNone(timeout,self.timeout)
        if feedback is not None:
            feedback = self._parse_feedback(feedback)
        else:
            feedback = self.feedback
        expected = notNone(expected,self.expected)
        wait = notNone(wait,self.wait)
        asynch = notNone(asynch,self.asynch)
        t0 = time.time()
        result = None
        
        if isString(self.command):
            if not asynch:
                if args: result = self.proxy.command_inout(self.command,args)
                else: result = self.proxy.command_inout(self.command)
            else:
                self.trace('Using asynchronous commands')
                if args: cid = self.proxy.command_inout_asynch(self.command,args)
                else: cid = self.proxy.command_inout_asynch(self.command)
                while timeout > (time.time()-t0):
                    self.event.wait(.025)
                    try: 
                        result = self.proxy.command_inout_reply(cid)
                        break
                    except PyTango.DevFailed,e:
                        if 'AsynReplyNotArrived' in str(e): 
                            pass
                        #elif any(q in str(e) for q in ('DeviceTimedOut','BadAsynPollId')):
                        else:
                            #BadAsynPollId is received once the command is discarded
                            raise TangoCommand.CommandException(str(e).replace('\n','')[:100])
        elif isCallable(self.command):
            result = self.command(args)
            
        t1 = time.time()
        if t1 > (t0+self.timeout): 
            raise TangoCommand.CommandTimeout(str(self.timeout*1000)+' ms')
        if feedback is not None:
            self.trace('Using feedback: %s'%feedback)
            tt,tw = min((timeout,(t1-t0+wait))),max((0.025,wait/10.))
            now,got = t1,None
            while True:
                self.event.wait(tw)
                now = time.time()
                got = type(expected)(feedback())
                if not wait or expected is None or got==expected:
                    self.trace('Feedback (%s) obtained after %s s'%(got,time.time()-t0))
                    break
                if now > (t0+timeout):
                    raise TangoCommand.CommandTimeout(str(self.timeout*1000)+' ms')
                if now > (t1+wait):
                    break
            if expected is None:
                return got
            elif got==expected:
                self.trace('Result (%s,%s==%s) verified after %s s'%(result,got,expected,time.time()-t0))
                return (result if result is not None else got)
            else:
                raise TangoCommand.BadFeedback('%s!=%s'%(got,expected))
        elif expected is None or result == expected:
            self.trace('Result obtained after %s s'%(time.time()-t0))
            return result
        else:
            raise TangoCommand.BadResult(str(result))
        if self.timeout < time.time()-t0: 
            raise TangoCommand.CommandTimeout(str(self.timeout*1000)+' ms')
        return result 
