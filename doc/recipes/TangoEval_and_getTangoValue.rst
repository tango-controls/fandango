===========================
TangoEval objects for Panic
===========================

.. contents::

TangoedValue class
==================

TangoedValue objects are returned by getTangoValue function and allow a compact syntax for attribute evaluation formulas.
This function will take a proxy or string as argument and will return an special struct as attribute value.

This struct provides several new members in addition to an AttrValue class:

 - device: simple device name
 - name: Attribute name
 - value: Attribute value
 - quality: AttrQuality value
 - time: Timestamp in seconds
 - type: CmdArgType 
 - domain: first part of the device name
 - family: second part
 - member: third part
 - host: Tango Host
 - ALARM: value in ALARM range
 - WARNING: value in WARNING or ALARM range
 - INVALID: value is not readable
 - VALID: value is readable
 - OK: value is readable and not in WARNING range
 
 TangoEval class
 ===============
 
 Engine to evaluate formulas containing tango attributes.
