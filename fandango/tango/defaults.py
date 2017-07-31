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

#python imports
import time,re,os,traceback,threading

#pytango imports
import PyTango
from PyTango import AttrQuality,EventType,DevState,AttrDataFormat,\
  AttrWriteType,CmdArgType,AttributeProxy,DeviceProxy

if 'Device_4Impl' not in dir(PyTango):
    PyTango.Device_4Impl = PyTango.Device_3Impl

import fandango
import fandango.objects as objects
from fandango.functional import *

from fandango.dicts import CaselessDefaultDict,CaselessDict,Enumeration
from fandango.objects import Object,Struct,Cached
from fandango.log import Logger,except2str,printf
from fandango.excepts import exc2str

#taurus imports, here USE_TAU is defined for all fandango
global TAU,USE_TAU,TAU_LOGGER
TAU,USE_TAU = None,False
def loadTaurus():
    print '#'*80
    print '%s fandango.tango.loadTaurus()'%time.ctime()
    global TAU,USE_TAU,TAU_LOGGER
    try:
        assert str(os.getenv('USE_TAU')).strip().lower() not in 'no,false,0'
        import taurus
        TAU = taurus
        USE_TAU=True
        TAU_LOGGER = taurus.core.util.Logger
        """USE_TAU will be used to choose between taurus.Device and PyTango.DeviceProxy"""
    except:
        print 'fandango.tango: USE_TAU disabled'
        TAU = None
        USE_TAU=False
        TAU_LOGGER = Logger
    return bool(TAU)


TANGO_STATES = \
  'ON OFF CLOSE OPEN INSERT EXTRACT MOVING STANDBY FAULT INIT RUNNING ALARM DISABLE UNKNOWN'.split()
TANGO_COLORS = \
  'Lime White White Lime White Lime LightBlue Yellow Red Brown LightBlue Orange Magenta Grey'.split()

TANGO_STATE_COLORS = dict(zip(TANGO_STATES,TANGO_COLORS))

ATTR_ALARM = AttrQuality.ATTR_ALARM
ATTR_WARNING = AttrQuality.ATTR_WARNING
ATTR_VALID = AttrQuality.ATTR_VALID
ATTR_INVALID = AttrQuality.ATTR_INVALID

####################################################################################################################
##@name Access Tango Devices and Database

##TangoDatabase singletone
global TangoDatabase,TangoDevice,TangoProxies
TangoDatabase,TangoDevice,TangoProxies = None,None,None

def get_tango_host(dev_name='',use_db=False):
    """
    If device is a tango model, it will extract the host from the model URL
    If devicesis none, then environment variable or PyTango.Database are used to extract the host
    If TANGO_HOST is not defined it will always fallback to PyTango.Database()
    """
    try:
        if dev_name:
            if isString(dev_name):
              m  = matchCl(rehost,dev_name)
            else: 
              m,use_db = None,dev_name
            return m.groups()[0] if m else get_tango_host(use_db=use_db)
        elif use_db:
            use_db = use_db if hasattr(use_db,'get_db_host') else get_database()
            host,port = use_db.get_db_host(),int(use_db.get_db_port())
            if (matchCl('.*[a-z].*',host.lower())
              #and PyTango.__version_number__ < 800):
              ): #The bug is back!!
                #Remove domain name
                host = host.strip().split('.')[0]
            return "%s:%d"%(host,port)
        else:
            host = os.getenv('TANGO_HOST') 
            return host or get_tango_host(use_db=True) 
    except:
        print('ERROR: get_tango_host(): '+traceback.format_exc())
        return 'localhost:10000'
    
def get_database(host='',port='',use_tau=False): 
    """
    Method to get a singleton instance of the Tango Database
    host/port can be a host,port tuple; a 'host:port' string or a taurus model.
    @TODO: host/port is checked only at first creation, once initialized you can't change HOST
    """
    global TangoDatabase
    global TAU,USE_TAU
    if host in (True,False): use_tau,host,port = host,'','' #For backwards compatibility
    else:
      if '/' in host: 
        # Parsing a taurus model
        host = get_tango_host(host)
      if ':' in host: 
        # Parsing a host:port string
        host,port = host.split(':')
    args = [host,int(port)] if host and port else []
    
    ### DISABLED, CRUSHED WITH BAD_INV_ORDER CORBA in Tango8
    if False and not args and TangoDatabase:
        try:
            t = time.time()
            #TangoDatabase.get_info() #TOO SLOW TO BE A CHECK!
            #TangoDatabase.check_tango_host(TangoDatabase.get_db_host()+':'+TangoDatabase.get_db_port())
            #TangoDatabase.get_timeout_millis()
            print time.time()-t
            return TangoDatabase 
        except:
            #traceback.print_exc()
            pass #defaulting to Taurus/PyTango
    try: 
        if use_tau and not TAU: TAU = loadTaurus()
        db = (use_tau and TAU and TAU.Database(*args)) or PyTango.Database(*args)
        if not args: TangoDatabase = db
        return db
    except:
        print traceback.format_exc()
    return
        
def get_proxy(argin,use_tau=False,keep=False):
    """
    Returns attribute or device proxy depending on argin syntax
    """
    if argin.count('/')>(2+(':' in argin)):
        return PyTango.AttributeProxy(argin)
    else:
        return get_device(argin,use_tau,keep)

def get_device(dev,use_tau=False,keep=False): 
    if use_tau and not TAU: use_tau = loadTaurus()
    if isinstance(dev,basestring): 
        if dev.count('/')==1: dev = 'dserver/'+dev
        if use_tau and TAU: 
            return TAU.Device(dev)
        else:
            global TangoProxies
            if keep and TangoProxies is None: 
                TangoProxies = ProxiesDict(use_tau=use_tau)
            if TangoProxies and (dev in TangoProxies or keep):
                return TangoProxies[dev]
            else: 
                return PyTango.DeviceProxy(dev)
    elif isinstance(dev,PyTango.DeviceProxy) or (use_tau and TAU and isinstance(dev,TAU.core.tango.TangoDevice)):
        return dev
    else:
        return None

def get_database_device(use_tau=False,db=None): 
    global TangoDevice
    td = TangoDevice
    #print('get_database_device(%s,use_tau=%s,db=%s)'%(td,use_tau,db))
    if db is None and td is not None:
      return td
    else:
        try:
           dev_name = (db or get_database(use_tau=use_tau)).dev_name()
           dev_name = get_tango_host(use_db=db)+'/'+dev_name if db else dev_name
           td = get_device(dev_name,use_tau=use_tau)
        except: 
           print('get_database_device(%s,use_tau=%s,db=%s)'%(dev_name,use_tau,db))
           traceback.print_exc()
        if db is None: 
          TangoDevice = td
    return td
