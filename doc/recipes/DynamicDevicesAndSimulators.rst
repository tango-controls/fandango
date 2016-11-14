==============================
Dynamic Devices and Simulators
==============================

.. contents::

What DynamicAttributes / DynamicDS allow
========================================

The DynamicAttributes property allows to declare attributes using formulas in a property::

  PRESSURE = DevDouble(SerialCommand('PR1?'))

Attribute values can be combined, also with attributes from other devices::

  AVERAGE = DevDouble((ATTR1+ATTR2+XATTR('other/tango/device/attribute'))/3)

It's also possible to write READ/WRITE attributes::

  SETPOINT = DevDouble(READ and SerialCommand('SP?') or WRITE and SerialCommand('SP=%s'%VALUE))

Add Dynamic Attributes features to an existing device
=====================================================

Modify the following lines of your device::

  from fandango.dynamic import *

Declaration of your device, replace DevImpl::

  class GaugeController(fandango.DynamicDS):

Class creator, initialize DynamicDS instead of DevImpl; methods added to _locals dictionary will be available in attributes formulas::

  def __init__(self,cl, name):
        ...
        fandango.DynamicDS.__init__(self,cl,name,_locals={'SerialCommand':self.SerialCommand})
        GaugeController.init_device(self)

Init() method of device, replace get_device_properties()::

  def init_device(self):
        ...
        self.get_DynDS_properties() 
        ...

Always executed hook
--------------------

  def always_executed_hook(self):
        print "In ", self.get_name(), "::always_excuted_hook()"
        fandango.DynamicDS.always_executed_hook(self)

Declaration of class, replace PyTango.DeviceClass::

  class GaugeControllerClass(fandango.DynamicDSClass): #<--- Declaration of Class
        ...

And then create the DynamicAttributes property and put there your attributes formulas.::

  SETPOINT=type(READ and SerialComm('SP?') or WRITE and SerialComm('SP=%s'%VALUE))

A higher fandango integration (dynamic states, commands, online update) can be achieved modifying the main method::

  if __name__ == '__main__':
    try:
        py = PyTango.Util(sys.argv)
        from fandango.interface import FullTangoInheritance
        GaugeController,GaugeControllerClass =  FullTangoInheritance('GaugeController',GaugeController,GaugeControllerClass,DynamicDS,DynamicDSClass,ForceDevImpl=True)
        py.add_TgClass(GaugeControllerClass,GaugeController,'GaugeController')
        U = PyTango.Util.instance()
        fandango.dynamic.CreateDynamicCommands(GaugeController,GaugeControllerClass)
        U.server_init()
        U.server_run()

Usage of Dynamic Attributes
===========================

Setting Dynamic Attributes property
-----------------------------------

The DynamicAttributes Property is used to create the read/write attributes of the PyPLC Device or any other device inheriting from DynamicDS.

This is the format that can be used to declare the Dynamic Attributes (more information is available in the PyTango_utils module user guide). Remember that it is python code and is Case Sensitive!::

  ATT_NAME=type(READ and !DevComm1(args) or WRITE and !DevComm2(args,VALUE))

Setting Dynamic States
----------------------

For DynamicStates a boolean operation must be set to each state ... but the name of the State should match an standard Tango.DevState name (ON, FAULT, ALARM, OPEN, CLOSE, ...)::

  ALARM=(SomeAttribute > MaxRange)
  ON=True

The "STATE" clause can be used also; forcing the state returned by the code. (NOTE: States are usable within formulas, so it should not be converted to string!)::

  STATE=ON if Voltage>0 else OFF

Setting Dynamic Status
----------------------

Every line in Dynamic Status will be evaluated and joined in the result if has a value. Every line of the DynamicStatus property will be evaluated as a new line in the status attribute value. You can use the reserved STATUS keyword to append the default status.

Using different Tango Types
---------------------------

The type of attributes can be declared using DevLong/DevDouble/DevBool/DevString, DevVarLongArray/DevVarDoubleArray/DevVarBoolArray/DevVarStringArray

Or the equivalent python types: int , float, bool, str, list(int(i) for i in []), [float(i) for i in[]], ...

Therefore::

  AnalogIntsREAD=list(long(r) for r in Regs(7800,100)) #Array of 100 integers read from address 7800

equals to::

  AnalogIntsREAD=DevVarLongArray(Regs(7800,100)) #Array of 100 integers read from address 7800

Warning!: DynamicAttributes sometimes fail with python generators; it must be inside list(gen) or between [gen]

Using Attribute Values (own or external)
----------------------------------------

DynamicDS.dyn_values dictionary::

        This dictionary keeps all the information related to dynamic attributes (name,type,value,formula,dependencies,keep).

Direct access::

        Reads the last generated value of another dynamic attribute
        NewAttribute = type(Attribute)

ATTR()::

        Forces an eval() execution
        NewAttribute = type(ATTR('Attribute'))

XATTR()::

        Reads an attribute from an external device
        NewAttribute = type(XATTR('Attribute')).

WATTR()::

        Allows to Write a VALUE in an external attribute
        WritableAttribute = type(READ and XATTR('Attribute') or WRITE and WATTR('Attribute',VALUE)).

Using TAU 
---------

If import tau is available a tau.Attribute object is used to read the attributes. If not then PyTango.AttributeProxy objects are used

The KeepAttributes property
---------------------------

This property may contain 'yes', 'no' or a list of attribute names. It controls if the last attribute values generated are kept for later calculations or not (using .value and .keep variables).

Meta Variables
==============

Several variables are available by default in DynamicAttributes and DynamicStates declaration::

    t : seconds passed since device startup 

    READ : Boolean set to True when read_attribute is being executed 

    WRITE : Boolean set to True when write_attribute is being executed 

    VALUE : Value passed to write_attribute as argument 

    STATE : Actual state of the device (although STATE=new_value equals to a set_state() execution) 

    STATUS : Last generated status 

    ATTRIBUTE : Name of the attribute being evaluated 

 

    NAME : The device name 

    POLLING(pending) : Actual Polling period of the Attribute (POLLING=new_value is NOT allowed) 

Variables, Tango Properties and EVAL
====================================

Property values can be read using the PROPERTY('prop_name') command. The EVAL(expression) command can be used to evaluate any string ... including property contents::

    Property Name 	Value
    DynamicAttributes 	AttributeFromProperty=EVAL(PROPERTY('SomeProperty')))
    SomeProperty 	3*sin(t/3.1415)

Other usages are::

    PROPERTY(name,True) to force reloading of the value,
    WPROPERTY(name,VALUE) to store a new value in Tango DB. 

The method VAR('attribute_name',new_value) can be used to store a forced value in an internal mapping of the Dynamic Device Server. This value returned if VAR('attribute_name') is called with a single argument.

Example: for creating a simulated attribute that returns the same value that has been written::

  OP-PNV-01=DevBoolean(READ and VAR('OP-PNV-01') or WRITE and VAR('OP-PNV-01',VALUE))

Using Tango Device Commands to create new Attributes
----------------------------------------------------

Example: In the case of a PyPLC Device any of the Device Commands can be used in the Attribute declaration:

=======   =====   ======  ====== ===========
Command 	Argin 	Argout 	Result Description
=======   =====   ======  ====== ===========
Reg(Address) 	DevShort 	DevShort 	Value of the given register
Coil(Address) 	DevShort 	DevShort 	Value of the given coil ()
Flag(Address,Bit) 	DevVarShortArray 	DevShort 	Value of a bit in the given register
Bit(Number,Bit) 	DevVarShortArray 	DevShort 	Value of a bit in the given integer
Regs(Address,N) 	DevVarShortArray 	DevVarShortArray 	Values of N consecutive registers
Regs32(Address,N) 	DevVarShortArray 	DevVarShortArray 	N 32bit values from 2*N consecutive registers
Coils(Address,N) 	DevVarShortArray 	DevVarShortArray 	Values of N consecutive coils
IeeeFloat(Address) 	DevVarShortArray 	DevDouble 	32bit IeeeFloat read from 2 consecutive registers
IeeeFloat(Int1,Int2) 	DevVarShortArray 	DevDouble 	32bit IeeeFloat build using two 16bit integers
WriteFloat(Address,Value) 	DevVarStringArray 	DevString 	Writes a IeeeFloat number in two registers
WriteCoil(Address,Value) 	DevVarShortArray 	DevVoid 	Writes a 0 or 1 in a coil
WriteBit(Address,Value) 	DevVarShortArray 	DevVoid 	Writes a 0 or 1 in a bit of a register
WriteInt(Address,Value) 	DevVarShortArray 	DevVoid 	Writes a 16bit value in a register
WriteLong(Address,Value) 	DevVarLongArray 	DevVoid 	Writes a 32bit value in two registers
=======   =====   ======  ====== ===========

The commands available in DynamicAttributes will depend on each DynamicDS implementation (it must be explicitly declared in DeviceServer implementation).

It uses self._locals dictionary to store the commands of the class to be available in attributes declaration.

These commands can be added directly to the self._locals dictionary, using the argument _locals of eval_attr method or in ``DynamicDS.__init__`` call::

    self.call__init__(DynamicDS,cl,name,_locals={
      'Command0': lambda argin: self.Command0(argin),
      'Command1': lambda _addr,val: self.Command1([_addr,val]), #typical Tango command that requires an array as argument
      'Command2': lambda argin,VALUE=None: self.Command1([argin,VALUE]), #typical write command, with VALUE defaulting to None only argin is used
                    },useDynStates=False)

Dynamic Attributes Qualitites
=============================

Using DynamicAttribute() method
-------------------------------

DynamicAttributes::

  DevDouble(DynamicAttribute(value=sin(t),quality=[ATTR_VALID,ATTR_WARNING][sin(t)>0.5]))

DynamicAttribute can also be abreviated as DYN.

Using DynamicQualities property
-------------------------------

:DynamicAttributes: x=READ and (VAR('x') or 0.0)  or WRITE and (VAR('x', VALUE) and VAR('t0',t))
:DynamicQualities:  x=VAR('t0')+10>t and ATTR_CHANGING  or ATTR_VALID

or

:DynamicQualitites: Analog(.*) = ATTR_WARNING if POLL>1 else ATTR_VALID

or::

  (*)_Status=ATTR_WARNING if '1' in ATTR('$_Status') else ATTR_VALID

Where $ will be equivalent to the expression returned by (*)

KeepTime / KeepAttributes /CheckDependencies properties
=======================================================

The values of dynamic attributes will be kept in dyn_values dictionary if KeepAttributes is equal to '*', 'yes' or 'true'; or if the attribute name appears in the property.

For each read_dyn_attr(Attribute) call the values will not be recalculated if interval between read_attribute calls is < KeepTime (500 ms by default).

ChekDependencies (True by default)
----------------------------------

will force a check of which attributes are accessed in other's formulas, creating an index for each attribute with its pre-requisites for evaluation (which will be automatically assigned to be kept). At each read_dyn_attr execution the dependency values will be added to _locals, and a read_dyn_attr(dependency) may be forced if its values are older than KeepTime.

Tango Events
============

The UseEvents property
----------------------

If UseEvents contains 'yes','true' or a list of attributes the dynamic push events will become enabled for those attributes that have relative/absolute change events configured.

Events will be pushed if after an evaluation of the attribute its value has changed above the change events range. Events will be pushed always as Change Events.

To allow pushing custom events (e.g. on quality changing) the default Tango event filtering is not used ( (set_change_event(attr_name,True,False) instead); therefore only absolute and relative change conditions are checked.

The parsing of UseEvents have been modified to prevent UseEvents=Yes to disable Taurus visualization of attributes. It occurs because if set_change_event is called for any attribute Taurus will no poll anymore its values.

But, if UseEvents is yes but the event is not configured or the internal polling is not active then no event will be pushed for the attribute!

To prevent this I established several UseEvents behaviours:

:No/False: No change event is set for any attribute
:Yes/True: Change event is set if configured both event and polling; if only event is set then polling is configured for the next device startup but events are not set. Change event for State will be set.
:reg.*exp: Only attributes that match the regular expression will be setup; but they will set even if no event is configured in database (to allow push if wanted). 

Example::

    UseEvents:yes: Will enable polling+events for State and for any other attribute if change event is configured in jive.
    UseEvents:(PNV*|WBAT*|State): It will enable polling+events only for state and attributes starting by PNV or WBAT. 

Triggering a push event
-----------------------

The attribute will be evaluated (therefore being able to push events) for any of these reasons::

    The attribute is read from an external client.
    The attribute is read using internal polling.
    The attribute uses XAttr to access external attributes and an event from those external attributes is received.
    The property CheckDependencies is True and an attribute depending from this one (having its name in the formula) is evaluated. 

Dynamic Commands
================

fandango.dynamic.CreateDynamicCommands method will modify both device and deviceClass objects. It requires to add a new line in the Device Server main method::

    if __name__ == '__main__':
      try:
        py = ('PyUtil' in dir(PyTango) and PyTango.PyUtil or PyTango.Util)(sys.argv)
        PyStateComposer,PyStateComposerClass=FullTangoInheritance(
          'PyStateComposer',PyStateComposer,PyStateComposerClass,
          DynamicDS,DynamicDSClass,ForceDevImpl=True)
          py.add_TgClass(PyStateComposerClass,PyStateComposer,'PyStateComposer')

        U = PyTango.Util.instance()
        fandango.dynamic.CreateDynamicCommands(PyStateComposer,PyStateComposerClass) #<=== It enables new Dynamic Commands
        U.server_init()
        U.server_run()

It will create new commands parsable from the DynamicCommands property:

DynamicAttributes::

  VALS=sum([XAttr('test/test/test/value%d'%i or 0.) for i in range(1,5)])

DynamicCommands::

  TEST=str(COMM('test/test/test/State',[]))+'='+str(VALS)
  TEST2=str(float(VALS)+float(ARGS[0]))

It will use an ARGS variable to manage the input arguments of the command. If ARGS appear in the formula the Command created will use DevVarStringArray as argin. If not, then it will be a DevVoid command.

The returning type can be explicitly specified:

:DynamicCommands:
  ReadHoldingRegisters=DevVarLongArray([ARGS[0]]*int(ARGS[1]))

Advanced DynamicDS creation
===========================

Creating the DynamicDS inheritance (as accepted by Pogo!)
---------------------------------------------------------

The inheritance is created calling to FullTangoInheritance before any py.add_TgClass(...) call::

    if __name__ == '__main__':
            try:
                    py = PyTango.PyUtil(sys.argv)

                    # Adding TRUE DeviceServer Inheritance
                    from PyTango_utils.interface import FullTangoInheritance
                    <YourDevice>,<YourDevice>Class = \
                        FullTangoInheritance('<YourDevice>',<YourDevice>,<YourDevice>Class,DynamicDS,DynamicDSClass,ForceDevImpl=True)

                    py.add_TgClass(<YourDevice>Class,<YourDevice>,'<YourDevice>')  

                    U = PyTango.Util.instance()
                    U.server_init()
                    U.server_run()

            except PyTango.DevFailed,e:
                    print '-------> Received a DevFailed exception:',e
            except Exception,e:
                    print '-------> An unforeseen exception occured....',e

 

The ForceDevImpl argument forces that PyTango.Device_3Impl always appear in the DeviceServer.bases list; it doesn't matter the lenght of the inheritance chain.

The fast way (not Pogo-compatible)
----------------------------------

Modify the following lines of your device::

  class LLRFFacade(fandango.DynamicDS):
    ...

    def __init__(self,cl, name):
        #PyTango.Device_4Impl.__init__(self,cl,name)
        fandango.DynamicDS.__init__(self,cl,name,_locals={'PhaseShift':lambda:None})
        LLRFFacade.init_device(self)
    ...

    def always_executed_hook(self):
        print "In ", self.get_name(), "::always_excuted_hook()"
        fandango.DynamicDS.always_executed_hook(self)
    ...

  class LLRFFacadeClass(fandango.DynamicDSClass):
    ...

Additional lines to be added for DynamicDS
------------------------------------------

Import everything from fandango.dynamic module::

  from PyTango_utils.dynamic import *

in __init__ : Substitute Device_3Impl by DynamicDS::

  #PyTango.Device_3Impl.__init__(self,cl,name)
  DynamicDS.__init__(self,cl,name,_locals={},useDynStates=True)

in always_executed_hook : Add a call to ``DynamicDS.always_executed_hook()``::
 
  def always_executed_hook(self):
    print "In ", self.get_name(), "::always_executed_hook()"

    DynamicDS.always_executed_hook(self)

Adding new attributes embedded within the device
================================================

Using DynamicAttributes property
--------------------------------

    The Syntax for declaring new Attributes using the DynamicAttributes property is described in the next chapter.

Or Pseudo Static Attributes (for configurable multiple input / output devices)
------------------------------------------------------------------------------

If you want to create the fixed attributes within your code you can use this method to add an attribute (attributes formula syntax is the same than in the previous case)::

    #Add this line for each new attribute:
    self.DynamicAttributes.append('MyNewAttribute=DevVarTangoType(python_code or any_command or any_attribute)')
    #The next one is not needed in init_device

    self.updateDynamicAttributes()

This two lines of code will enable all the features available in the DynamicDS template (use of commands, internal and external attributes, easy type casting, ...).

  **Note:** When inserted inside init_device these lines must be inserted after self.get_device_properties(self.get_device_class())

Using DynamicStates for changing the device State
=================================================

  **NOTE:** Using DynamicDS the automatic State generation using Attribute Alarm/Warning Properties is disabled 
    
This is a typical syntax to be used in DynamicStates property::

  FAULT=self.last_reading < time.time()-3600

  WARNING=max ([Temperature1,Temperature2])>70
  OK=1 #State by default

The DynamicDS evaluates sequentially each of the expressions; setting the State to the first one evaluating to True. If nothing is declared the State is set to UNKNOWN by default.


----

Examples
--------

Example using DynamicAttributes, DynamicStates and DynamicCommands
==================================================================

It will use a command to record a value in the 'C' variable, it can be returned from the C attribute and will affect the State.

DynamicAttributes::

  A = DevString("Hello World!")
  B = t
  C = DevLong(VAR('C'))

DynamicStates::

  STATE=ON if VAR('C') else OFF

DynamicCommands::

  test_command=str(VAR('C',int(ARGS[0])) or VAR('C'))


Creating a Ramp with a SimulatorDS
==================================

This device will generate a ramp in the **Value** attribute.

The sequence is:

* Write **Setpoint** attribute
* Write **Period** attribute
* Launch **Start()**

:DynamicAttributes: ::

  #Settings
  Setpoint=VAR('SP',WRITE=True)
  Period=VAR('T1',WRITE=True)
  #Intermediate values
  Start=GET('T0')
  Ramp=VAR('R')
  Origin=GET('V0')
  #Output value
  Value=float(Origin+(t-Start)*Ramp if t<(Start+Period) else (GET('V1') if (Start and t>Start) else Value))

:DynamicCommands: ::

  Start=str((SET('V0',ATTR('Value')),SET('T0',t),SET('V1',ATTR('Setpoint')),SET('R',(ATTR('Setpoint')-GET('V0'))/ATTR('Period'))))

:DynamicStates: ::

  ON=VAR('Init',default=0)
  INIT=[SET(x,v) for x,v in [('Init',1),('SP',0),('R',0),('T1',1),('V0',0),('V1',1),('T0',0)]]
