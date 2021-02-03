#!/usr/bin/env python2.5
""" 
@if gnuheader
#############################################################################
##
## file :       interface.py
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
# Adding TRUE DeviceServer Inheritance
# Searchs all dicts in the ChildClass and updates its values using the Parent dicts
@endif

@package interface
@author srubio@cells.es

<h2 id="Proposals">Proposals of implementation</h2>
<h3 id="CommsDev">CommsDev</h3>
<p>
Hypothetical Abstract Class for Devices using Serial Line, Tcp Socket, Modbus, ...
</p>
<h4 id="Properties">Properties</h4>
<dl><dt><tt>str[] CommsDev__Properties</tt></dt><dd>
Allows to setup the properties of the device<br />
<tt>['key:value','key:value','key:[values]',...]</tt>
</dd></dl>
<h4 id="Attributes">Attributes</h4>
<dl><dt><tt>int LastComm</tt></dt><dd>
The last time that a communication was successful.
</dd></dl>

<dl><dt><tt>state ChannelState</tt></dt><dd>
State of the hardware device on charge of communications 
<tt>[ON/OFF/FAULT/UNKNOWN/RUNNING]</tt>
</dd></dl>
<h4 id="Commands">Commands</h4>
<dl><dt><tt>str Talk(str)</tt></dt><dd>
A direct raw writing/reading to the communication port
</dd></dl>

<h3>Example of making a Controller device with embedded Serial communications</h3>
    <pre>
        # Adding TRUE DeviceServer Inheritance
        from interface import FullTangoInheritance
        VacuumController,VacuumControllerClass = FullTangoInheritance('VacuumController', \
            VacuumController,VacuumControllerClass, \
            SerialDS,SerialDSClass,ForceDevImpl=True)
        py.add_TgClass(VacuumController,VacuumControllerClass,'VacuumController')    
    </pre>

"""

def getDeviceClassObjects(classname,path=''):
    """
    This method locates a Tango Device Class in the python Path and returns its (Device,DeviceClass) objects
    """
    import imp
    desc = imp.find_module(classname)
    print('getDeviceClassObjects(%s) from %s'%(classname,desc))
    module = imp.load_module(classname,*desc)
    return getattr(module,classname),getattr(module,classname+'Class')

def addAllClasses(obj,servername='',db=None,classes=None):
    """
    This method will add all classes listed in the database to the server object (if those classes are available in the pythonpath)
    
    obj argument must be a PyTango.Util(['exec_name','instance_name']) object
    If servername or db are not specified will be taken from obj.instance()
    
    Dependences can be added to pythonpath using sys.path.insert(0,'path/to/your/device')
    """
    if classes is None:
        instance = obj.instance()
        if not db:db = instance.get_database()
        if not servername: servername = instance.get_ds_name()
        if ' ' in servername or '.py' in servername: servename = '/'.join(s.replace('.py','').strip() for s in servername.split())
        classes = db.get_server_class_list(servername)
    for c in classes:
        dev,devclass = getDeviceClassObjects(c)
        print('Adding %s,%s to %s'%(dev,devclass,obj))
        obj.add_TgClass(devclass,dev,c)
    return obj
        

def updateChildClassDicts(Child,Parent,Exclude=[]):
    #print 'Updating %s from %s'%(Child.__name__,Parent.__name__)
    for attribute in dir(Child):
        cattr = getattr(Child,attribute)
        if (not attribute.startswith('__')) and isinstance(cattr,dict) and hasattr(Parent,attribute):
            pattr = getattr(Parent,attribute)
            if isinstance(pattr,dict): 
                #print 'Updating %s.%s from %s'%(Child.__name__,attribute,Parent.__name__)
                cattr.update((k,v) for k,v in pattr.items() if k not in Exclude and k not in cattr)
#updateChildClassDicts(AlbaPLCClass,PyPLCClass)        
        
def NewTypeInheritance(name,klass,parent,dikt={}):
    """ Based on NewClass = type('nameOfClass',(bases,),dikt={}) """
    return type(name,(klass,parent),dikt)

def FullTangoInheritance(name,child,childClass,parent,parentClass,Exclude=[],ForceDevImpl=False):
    """ arguments are: NewDeviceName, Device, DeviceClass, newParentDevice, newParentDeviceClass, parent members to exclude 
    @remark The code must be added always before each add_TgClass call (it could be outside the class definition file!)
    
    example:
    <pre>
        # Adding TRUE DeviceServer Inheritance
        from interface import FullTangoInheritance
        PySignalSimulator,PySignalSimulatorClass = FullTangoInheritance('PySignalSimulator', \
            PySignalSimulator,PySignalSimulatorClass, \
            DynamicDS,DynamicDSClass,ForceDevImpl=True)
        py.add_TgClass(PySignalSimulatorClass,PySignalSimulator,'PySignalSimulator')    
    </pre>
    """
    if parent not in child.__bases__:
        #THIS PRINT OUT BROKE FANDANGO.SH CALLS
        #print 'Applying FullTangoInheritance from %s and %s' % (child, parent)
        if not ForceDevImpl:
            newdevice = type(name,(child,parent),{})
            newdeviceclass = type(name+'Class',(childClass,parentClass),{})
        else:
            import PyTango
            newdevice = type(name,(child,parent,PyTango.LatestDeviceImpl),{})
            newdeviceclass = type(name+'Class',(childClass,parentClass,PyTango.DeviceClass),{})
        updateChildClassDicts(newdeviceclass,parentClass,Exclude)
        return newdevice,newdeviceclass
    else:
        return child,childClass
    
def DeviceClassInheritance(ChildClass):
    """ class decorator """
    for b in ChildClass.__bases__:
        for p in ('class_property_list','device_property_list','cmd_list','attr_list'):
            d = getattr(b,p,{})
            d and getattr(ChildClass,p).update((k,v) for k,v in d.items() if k not in getattr(ChildClass,p))
    return ChildClass
    
def addTangoInterfaces(device,interfaces):
    """ It adds properties and implementation to the parent class from a list of tuples (Device,DeviceClass)
    @param device A tuple (Device,DeviceClass) to be extended with interfaces
    @param interfaces A list of tuples (Device,DeviceClass) to the first server
    @return Returns a tuple (Device,DeviceClass) containing the new interfaces
    
        from interface import FullTangoInheritance
        PySignalSimulator,PySignalSimulatorClass = FullTangoInheritance('PySignalSimulator',PySignalSimulator,PySignalSimulatorClass,DynamicDS,DynamicDSClass,ForceDevImpl=True)
        py.add_TgClass(PySignalSimulatorClass,PySignalSimulator,'PySignalSimulator')    
    """
    if any(type(p) is not tuple for p in ([device]+interfaces)):
        raise Exception,'TangoInterface_ArgumentIsNotTuple'
    device,deviceclass = device
    for interface,interfaceclass in interfaces:
        device,deviceclass = FullTangoInheritance(device.__name__, \
            device,deviceclass, \
            interface,interfaceclass, \
            ForceDevImpl=True)
    return device,deviceclass
    
def addCommandToTgClass(dev,dev_class,cmd_name,cmd_def,cmd_fun):
    """
    @param cmd_def should be like [[argintype,"desc"],[argouttype,"desc"],{'property':value}]
    e.g: [[PyTango.DevString, "formula to evaluate"],[PyTango.DevString, "formula to evaluate"],{'Display level':PyTango.DispLevel.EXPERT,}]
    """
    #print 'Adding command %s to %s,%s device class' % (cmd_name,dev,dev_class)
    setattr(dev,cmd_name,cmd_fun)
    dev_class.cmd_list[cmd_name] = cmd_def
    return

#def getAllBases(klass):
    #""" Gets recursively all super classes for a given class """
    #bases = list(klass.__bases__)
    #for base in bases:
        #[bases.append(b) for b in getAllBases(base) if b not in bases]
    #return bases
