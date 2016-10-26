==============================
Recipes using DynamicDS device
==============================

DynamicCommands
---------------

Write a command that writes an attribute::

OpenFrontEnd=   WATTR( 'PLC_CONFIG_STATUS','0000000000100000')

DynamicQualities
----------------

Change quality of an attribute depending on another one::

(*)_VAL=ATTR_ALARM if ATTR('$_ALRM') else ATTR_VALID
