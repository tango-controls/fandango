==============================
Recipes using DynamicDS device
==============================

DynamicDS device formulas are declared using four properties:

 - DynamicAttributes
 - DynamicCommands
 - DynamicStates
 - DynamicQualities
 
.. contents::

Directives and Keywords
=======================
 
Those formulas accept special directives and keywords

Special directives
------------------

**@COPY:a/dev/name** : It COPIES! your DynamicAttributes from another dynamic device (e.g., for all power supplies you just have one as template and all the rest pointing to the first one, update one and you update all).
        
**@FILE:filename.txt** : It reads the attributes/states/commands from a file instead of properties; for templating hundreds of devices w/out having to go one by one in Jive.

Keywords in Dynamic Properties
------------------------------

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

**FILE** : open a file

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

**ATTRIBUTE** : current attribute name

Examples
========

DynamicCommands
---------------

Remember that DynamicCommands need a full restart of the server to be created/updated.

Write a command that writes an attribute::

  OpenFrontEnd=   WATTR( 'PLC_CONFIG_STATUS','0000000000100000')

The syntax for typed arguments now replaces ARGS by {SCALAR/SPECTRUM}({int/str/float/bool},ARGS), thus specifying type in Command and Arguments is::
  
  SumSomeNumbers = DevDouble(sum(SPECTRUM(float,ARGS))) 
  #Instead of sum(map(float,ARGS)) which is still available

The old syntax still works (DevVarStringArray always for argin, anything you declare for argout).

DynamicCommands become functions in your attribute calls!!::

  SumAttr = SumSomeNumbers([Attr1,Attr2,Attr3])

DynamicQualities
----------------

Change quality of an attribute depending on another one::

  (*)_VAL=ATTR_ALARM if ATTR('$_ALRM') else ATTR_VALID

Simulations
-----------

Some examples available in the SimulatorDS documentation: https://github.com/tango-controls/simulatords
