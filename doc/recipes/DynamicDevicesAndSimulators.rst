==============================
Dynamic Devices and Simulators
==============================

.. contents::

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
