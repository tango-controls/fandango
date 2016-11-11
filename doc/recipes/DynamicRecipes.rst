==============================
Recipes using DynamicDS device
==============================

New keywords in Fandango 12
---------------------------

**SCALAR/SPECTRUM/IMAGE** : for creating typed attributes ( Attr=SPECTRUM(float,...) instead of Attr=DevVarDoubleArray(...) ) ; the main advantage is that it allows compact syntax and having Images as DynamicAttributes.
        
**@COPY:a/dev/name** : It COPIES! your DynamicAttributes from another dynamic device (e.g., for all power supplies you just have one as template and all the rest pointing to the first one, update one and you update all).
        
**@FILE:filename.txt** : It reads the attributes/states/commands from a file instead of properties; for templating hundreds of devices w/out having to go one by one in Jive.

Also, DynamicCommands become functions in your attribute calls!!: SumAttr = SumSomeNumbers([Attr1,Attr2,Attr3])

DynamicCommands
---------------

Write a command that writes an attribute::

  OpenFrontEnd=   WATTR( 'PLC_CONFIG_STATUS','0000000000100000')

The syntax for typed arguments now replaces ARGS by {SCALAR/SPECTRUM}({int/str/float/bool},ARGS), thus specifying type in Command and Arguments is::
  
  SumSomeNumbers = DevDouble(sum(SPECTRUM(float,ARGS))) 
  #Instead of sum(map(float,ARGS)) which is still available

The old syntax still works (DevVarStringArray always for argin, anything you declare for argout).

DynamicQualities
----------------

Change quality of an attribute depending on another one::

  (*)_VAL=ATTR_ALARM if ATTR('$_ALRM') else ATTR_VALID

Simulations
-----------

Some examples available in the SimulatorDS documentation: https://github.com/tango-controls/simulatords
