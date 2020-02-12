==============================
Dynamic Devices and Simulators
==============================

.. contents::

----

Introduction
============

The fandango library provides Dynamic Tango Device Classes through the fandango.dynamic module and the DynamicDS class.

DynamicDS device formulas are declared using four properties:

 - DynamicAttributes
 - DynamicCommands
 - DynamicStates
 - DynamicQualities
 
Devices implementing DynamicAttributes
--------------------------------------

The best example of DynamicAttributes is SimulatorDS: https://github.com/tango-controls/SimulatorDS

Other devices implementing this API are PyStateComposer, PyAttributeProcessor, PyPLC, CopyCatDS, CSVReader, RFFacade, ...

What DynamicAttributes / DynamicDS allow
----------------------------------------

The DynamicAttributes property allows to declare attributes using formulas in a property::

  PRESSURE = DevDouble(SerialCommand('PR1?'))

Attribute values can be combined, also with attributes from other devices::

  AVERAGE = DevDouble((ATTR1+ATTR2+XATTR('other/tango/device/attribute'))/3)

It's also possible to write READ/WRITE attributes::

  SETPOINT = DevDouble(READ and SerialCommand('SP?') or WRITE and SerialCommand('SP=%s'%VALUE))

----

Usage of Dynamic Attributes
===========================

Setting Dynamic Attributes property
-----------------------------------

The DynamicAttributes Property is used to create the read/write attributes of the PyPLC Device or any other device inheriting from DynamicDS.

This is the format that can be used to declare the Dynamic Attributes (more information is available in the PyTango_utils module user guide). Remember that it is python code and is Case Sensitive!::

  ATT_NAME=type(READ and !DevComm1(args) or WRITE and !DevComm2(args,VALUE))

Using different Tango Types
---------------------------

The type of attributes can be declared using DevLong/DevDouble/DevBool/DevString, DevVarLongArray/DevVarDoubleArray/DevVarBoolArray/DevVarStringArray

Or the equivalent python types: int , float, bool, str, list(int(i) for i in []), [float(i) for i in[]], ...

Therefore::

  AnalogIntsREAD=list(long(r) for r in Regs(7800,100)) #Array of 100 integers read from address 7800

equals to::

  AnalogIntsREAD=DevVarLongArray(Regs(7800,100)) #Array of 100 integers read from address 7800

Warning!: DynamicAttributes sometimes fail with python generators; it must be inside list(gen) or between [gen]

Reading Tango Attributes
------------------------

It's allowed to read attributes from the same device or others.

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
        
Writable Attributes
-------------------

You can use the VAR keyword to create a variable that will be stored as a writable attribute

        WritableAttribute = type(VAR(ATTRIBUTE,default=0.0,WRITE=True))
        
        
Type can be any Tango or python type; 
default will be the value returned if the attribute has not been read yet; 

The WRITE argument marks this attribute as writable; if you want to read afterwards just call VAR without WRITE argument.

        OtherAttributeUsingTheValue = type( 3 * VAR('WritableAttribute') )
        

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
        
The method will parse the DynamicCommands property, store declarations in ds.dyn_comms dictionary, add the command definitions to the ds_class and add a new method executing ds.evalCommand.

In principle it relies on using it with subclasses of DynamicDS; but you can implement your own evalCommand and it should work anyway.    

When used on DynamicDS devices, DynamicCommands will need a full restart of the server to be created, but just an updateDynamicAttributes() call to be updated.

Specify Arguments and Types
---------------------------

It will use an ARGS variable to manage the input arguments of the command. If ARGS appear in the formula the Command created will use DevVarStringArray as argin. If not, then it will be a DevVoid command.

The returning type can be explicitly specified:

:DynamicCommands:
  ReadHoldingRegisters=DevVarLongArray([ARGS[0]]*int(ARGS[1]))        
  
The syntax for typed arguments now replaces ARGS by {SCALAR/SPECTRUM}({int/str/float/bool},ARGS), thus specifying type in Command and Arguments is::

  SumSomeNumbers = DevDouble(sum(SPECTRUM(float,ARGS)))
  #Instead of sum(map(float,ARGS)) which is still available

Example
-------

If KeepAttributes=True; attribute values are available in commands.

DynamicAttributes::

  VALS=sum([XAttr('test/test/test/value%d'%i or 0.) for i in range(1,5)])

DynamicCommands::

  TEST=str(COMM('test/test/test/State',[]))+'='+str(VALS)
  TEST2=str(float(VALS)+float(ARGS[0]))
  
For a DevVoid command writing an attribute:

  OpenFrontEnd=   WATTR( 'PLC_CONFIG_STATUS','0000000000100000')

DynamicCommands become functions in your attribute calls:

:DynamicCommands:
  SumSomeNumbers = float(sum(SPECTRUM(float,ARGS)))
:DynamicAttributes:
  SumAttr = SumSomeNumbers([Attr1,Attr2,Attr3])

  
----

Dynamic States
==============

  **NOTE:** Using DynamicDS the automatic State generation using Attribute Alarm/Warning Properties is disabled 
    
This is a typical syntax to be used in DynamicStates property::

  FAULT=self.last_reading < time.time()-3600

  WARNING=max ([Temperature1,Temperature2])>70
  OK=1 #State by default

The DynamicDS evaluates sequentially each of the expressions; setting the State to the first one evaluating to True. If nothing is declared the State is set to UNKNOWN by default.

For DynamicStates a boolean operation must be set to each state ... but the name of the State should match an standard Tango.DevState name (ON, FAULT, ALARM, OPEN, CLOSE, ...)::

  ALARM=(SomeAttribute > MaxRange)
  ON=True

The "STATE" clause can be used also; forcing the state returned by the code. (NOTE: States are usable within formulas, so it should not be converted to string!)::

  STATE=ON if Voltage>0 else OFF

Setting Dynamic Status
----------------------

Every line in Dynamic Status will be evaluated and joined in the result if has a value. Every line of the DynamicStatus property will be evaluated as a new line in the status attribute value. You can use the reserved STATUS keyword to append the default status.

----

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

----

Directives and Keywords
=======================
 
All DynamicDS formulas accept special directives, functions and keywords

Special directives
------------------

**@COPY:a/dev/name** : It COPIES! your DynamicAttributes from another dynamic device (e.g., for all power supplies you just have one as template and all the rest pointing to the first one, update one and you update all).
        
**@FILE:filename.txt** : It reads the attributes/states/commands from a file instead of properties; for templating hundreds of devices w/out having to go one by one in Jive.

Functions in Dynamic Properties
-------------------------------

**DYN/SCALAR/SPECTRUM/IMAGE** : for creating typed attributes ( Attr=SPECTRUM(float,...) instead of Attr=DevVarDoubleArray(...) ) ; the main advantage is that it allows compact syntax and having Images as DynamicAttributes.

**ATTR('attribute')** : Read tango attribute (internal)

**XATTR('a/tango/dev/attribute')** : Read tango attribute (external)

**WATTR('a/tango/dev/attribute',$VALUE)** : Write tango attribute

**COMM('a/tango/dev/command',$ARGS?)** : Execute Tango command

**XDEV('a/tango/dev')** : Create a DeviceProxy

**VAR('name',v?,default?,WRITE=bool?)** : instantiate a new variable. If WRITE is True it will 
convert the whole formula into a writable attribute.

**VARS** : Access to variables dict.

**GET/SET** : helpers to VAR(name) or VAR(name,value)

**PROPERTY/WPROPERTY** : helpers to read/write properties.

**EVAL** : evaluate a DynamicDS formula

**MATCH(regexp,str)** : careless regexp matching

**FILE** : open a file as a list of strings

**time2str/ctime2time** : Time conversions

Keywords updated at every call
------------------------------

**now()/t** : get current timestamp / get seconds since device start

**WRITE/READ** : True if doing a WRITE attribute access, False when reading

**LOCALS** : local python namespace dictionary

**XATTRS** : all instantiated attributes

**ATTRIBUTES** : all dynamic attributes

**STATE** : current state

**NAME** : current device name

**ATTRIBUTE** : current attribute being evaluated

**VALUE** : Value passed to write_attribute as argument 

**ARGS** : Array passed to command as argument

**POLLING(pending)** : Actual Polling period of the Attribute (POLLING=new_value is NOT allowed) 



----

Examples
========

Simple example
--------------

It will use a command to record a value in the 'C' variable, it can be returned from the C attribute and will affect the State.

DynamicAttributes::

  A = DevString(VAR("Hello World!",WRITE=True))
  B = t
  C = DevLong(VAR('C'))

DynamicStates::

  STATE=ON if VAR('C') else OFF

DynamicCommands::

  test_command=str(VAR('C',int(ARGS[0])) or VAR('C'))

DynamicCommands
---------------

If KeepAttributes=True; attribute values are available in commands.

DynamicAttributes::

  VALS=sum([XAttr('test/test/test/value%d'%i or 0.) for i in range(1,5)])

DynamicCommands::

  TEST=str(COMM('test/test/test/State',[]))+'='+str(VALS)
  TEST2=str(float(VALS)+float(ARGS[0]))
  
For a DevVoid command writing an attribute:

  OpenFrontEnd=   WATTR( 'PLC_CONFIG_STATUS','0000000000100000')

DynamicCommands become functions in your attribute calls!!:

  SumAttr = SumSomeNumbers([Attr1,Attr2,Attr3])
  
specifying type in Command and Arguments is::

  SumSomeNumbers = DevDouble(sum(SPECTRUM(float,ARGS)))
  #Instead of sum(map(float,ARGS)) which is still available


DynamicQualities
----------------

Change quality of an attribute depending on another one::

  (*)_VAL=ATTR_ALARM if ATTR('$_ALRM') else ATTR_VALID


Creating a Ramp with a SimulatorDS
----------------------------------

This device will generate a ramp in the **Value** attribute.

The sequence is:

* Write **Setpoint** attribute
* Write **Period** attribute
* Launch **Start()**

DynamicAttributes::

  #Settings
  Setpoint=VAR('SP',WRITE=True)
  Period=VAR('T1',WRITE=True)
  #Intermediate values
  Start=GET('T0')
  Ramp=VAR('R')
  Origin=GET('V0')
  #Output value
  Value=float(Origin+(t-Start)*Ramp if t<(Start+Period) else (GET('V1') if (Start and t>Start) else Value))

DynamicCommands::

  Start=str((SET('V0',ATTR('Value')),SET('T0',t),SET('V1',ATTR('Setpoint')),SET('R',(ATTR('Setpoint')-GET('V0'))/ATTR('Period'))))

DynamicStates::

  ON=VAR('Init',default=0)
  INIT=[SET(x,v) for x,v in [('Init',1),('SP',0),('R',0),('T1',1),('V0',0),('V1',1),('T0',0)]]

Simulations
-----------

More examples available in the SimulatorDS documentation: https://github.com/tango-controls/simulatords

----

Advanced features / Syntax
==========================

Variables, Tango Properties and EVAL
------------------------------------

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
  
LoadFromFile
------------

It is possible to load attributes declaration from files. Just write attribute declarations in different rows in a txt file and set the full path to the file in the LoadFromFile property.

At init() and every time that updateDynamicAttributes() command is called ; the attribute formulas will be reloaded from the file.

Attributes declared in properties will have always precedence over attributes declared in files.

To update the attribute formulas from a file while running just use::

  import fandango
  with open('/tmp/config.txt','w') as f:  f.write("A = 5")
  dp = fandango.get_device('your/device/name')
  fandango.put_device_property('your/device/name','LoadFromFile','/tmp/config.txt')
  dp.updateDynamicAttributes()
  dp.A
  : 5

External python Modules
-----------------------

fandango.DynamicDS does not allow to use other modules in attribute declaration ; but you can use PyAttributeProcessor instead ( https://github.com/ALBA-Synchrotron/PyAttributeProcessor ) ; that integrates this feature using an ExtraModules property for module imports and renaming.

Using TAU 
---------

If import tau is available a tau.Attribute object is used to read the attributes. If not then PyTango.AttributeProxy objects are used

The KeepAttributes property
---------------------------

This property may contain 'yes', 'no' or a list of attribute names. It controls if the last attribute values generated are kept for later calculations or not (using .value and .keep variables).  

Using Tango Device Commands in attribute formulas
-------------------------------------------------

The commands available in DynamicAttributes will depend on each DynamicDS implementation (it must be explicitly declared in the DeviceServer implementation). But all the commands declared as DynamicCommands can be used in the Attribute declaration.

It uses self._locals dictionary to store the commands of the class to be available in attributes declaration.

These commands can be added directly to the self._locals dictionary, using the argument _locals of eval_attr method or in ``DynamicDS.__init__`` call::

    self.call__init__(DynamicDS,cl,name,_locals={
      'Command0': lambda argin: self.Command0(argin),
      'Command1': lambda _addr,val: self.Command1([_addr,val]), #typical Tango command that requires an array as argument
      'Command2': lambda argin,VALUE=None: self.Command1([argin,VALUE]), #typical write command, with VALUE defaulting to None only argin is used
                    },useDynStates=False)
                    
KeepTime / KeepAttributes /CheckDependencies properties
-------------------------------------------------------

The values of dynamic attributes will be kept in dyn_values dictionary if KeepAttributes is equal to '*', 'yes' or 'true'; or if the attribute name appears in the property.

For each read_dyn_attr(Attribute) call the values will not be recalculated if interval between read_attribute calls is < KeepTime (500 ms by default).

ChekDependencies (True by default)
..................................

will force a check of which attributes are accessed in other's formulas, creating an index for each attribute with its pre-requisites for evaluation (which will be automatically assigned to be kept). At each read_dyn_attr execution the dependency values will be added to _locals, and a read_dyn_attr(dependency) may be forced if its values are older than KeepTime.

Add DynamicAttributes to a Tango Device Class
---------------------------------------------

Modify the following lines of your device::

Declaration of your device, replace DevImpl by DynamicDS::

  from fandango.dynamic import *
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

Add always executed hook for evaluating states::

  def always_executed_hook(self):
        print "In ", self.get_name(), "::always_excuted_hook()"
        fandango.DynamicDS.always_executed_hook(self)

In the Tango class declaration, replace PyTango.DeviceClass::

  class GaugeControllerClass(fandango.DynamicDSClass): #<--- Declaration of Class
        ...

Finally, go to Jive and create the DynamicAttributes property and put there your attributes formulas.::

  SETPOINT=type(READ and SerialComm('SP?') or WRITE and SerialComm('SP=%s'%VALUE))
  

----

Tango Events on Dynamic Attributes
==================================

There are several Tango artifacts controlling the pushing of events from DynamicDS devices (SimulatorDS, PyAttributeProcessor, PyPLC, etc ...):

 - UseEvents Property: value can be yes/true/no/false, a list of attributes or a dict-like list 
 - AttributeConfig (in Jive): 
 - MaxEventStream Property:
 - ProcessEvents Command:

The Workflow is the following:

 - To push an attribute, its value must have changed (as detected by check_changed_event function).
 - If it was configured from Jive, this configuration is used to filter the emitted events.
 - If it wasn't configured; then any change is pushed.
 - UseEvents can be set as attr1:push to force inconditional pushing (filters ignored).
 - UseEvents can be set as attr1:archive to push archiving event together with change event.
 - See UseEvents property below for more information
 
 Apart of that, MaxEventStream > 0 will redirect events to a queue instead of being pushed immediately.
 
 The ProcessEvents command will read the queue and push MaxEventStream events at each call.

UseEvents property
------------------

Example:

    UseEvents:yes: Will enable polling+events for State and for any other attribute if change event is configured in jive.
    UseEvents:(PNV*|WBAT*|State): It will enable polling+events only for state and attributes starting by PNV or WBAT. 


If UseEvents contains 'yes','true' or a list of attributes the dynamic push events will become enabled for those attributes that have relative/absolute change events configured.

Events will be pushed if after an evaluation of the attribute its value has changed above the change events range. Events will be pushed always as Change Events.

To allow pushing custom events (e.g. on quality changing) the default Tango event filtering is not used ( (set_change_event(attr_name,True,False) instead); therefore only absolute and relative change conditions are checked.

The parsing of UseEvents have been modified to prevent UseEvents=Yes to disable Taurus visualization of attributes. It occurs because if set_change_event is called for any attribute Taurus will no poll anymore its values.

But, if UseEvents is "Yes" but the event is not configured or the internal polling is not active then no event will be pushed for the attribute!


To prevent this I established several UseEvents behaviours:

===========  =====================================================================
 UseEvents    Behaviour
===========  =====================================================================
 No/False     No change event is set for any attribute
 
 Yes/True     Change event is set if configured both event and polling; 
              if only event is set then polling is configured for the next device 
              startup but events are not set. Change event for State will be set.
              
 always       Change events are always pushed at attribute evaluation, 
              ignoring events configuration.
              
 push         Change events are pushed on any change, ignoring events configuration. 
 
 archive      appended to any of the previous clauses, it will trigger 
              archive together with change.
              
 reg.*exp     Only attributes that match the regular expression will be setup; 
              but they will set even if no event is configured in database 
              (to allow push if wanted).
===========  =====================================================================



Triggering a push event
-----------------------

The attribute will be evaluated (therefore being able to push events) for any of these reasons::

    The attribute is read from an external client.
    The attribute is read using internal polling.
    The attribute uses XAttr to access external attributes and an event from those external attributes is received.
    The property CheckDependencies is True and an attribute depending from this one (having its name in the formula) is evaluated. 

----

Advanced DynamicDS creation
===========================

You can add the dynamic attributes functionality to any Python Tango Device just inheriting from the fandango.DynamicDS class.

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
    
----

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

----

