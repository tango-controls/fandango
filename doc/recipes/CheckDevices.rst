Check status of Devices Attributes
==================================

  import fandango as fn
  import fandango.tango as ft

At server level
---------------

.. code-block:: python

  astor = fn.Astor('PyAttributeProcessor/*')
  astor.states()
  
  ('pyattributeprocessor/sr_ct_calc', PyTango._PyTango.DevState.ON)
  ('pyattributeprocessor/test_acc', PyTango._PyTango.DevState.ON)
  ('pyattributeprocessor/lab01_di_fft01', None)
  ('pyattributeprocessor/linacwatcher', PyTango._PyTango.DevState.ON)
  ('pyattributeprocessor/sr_calc', PyTango._PyTango.DevState.ON)
  
At device level
---------------

.. code-block:: python

  devices = astor.get_all_devices()
  
  OR
  
  devices = fn.get_matching_devices('SR/CT/*')
  
  THEN
  
  [(d,ft.check_device(d)) for d in devices]
    
  ('sr/ct/calc-01', True)
  ('sr/ct/calc-02', True)
  ('test/acc/calc', True)
  ('archiving/watcher/linac', None)
  ('sr/di/calc', True)
  
At attribute level
------------------

.. code-block:: python

  d = 'sr/di/calc'
  
  [(d,a,ft.read_attribute(a)) for a in fn.get_matching_attributes(d+'/*')]

  ('sr/di/calc', 'sr/di/calc/Gamma', 5832.0)
  ('sr/di/calc', 'sr/di/calc/Alpha', 0.00096000000000000002)
  ('sr/di/calc', 'sr/di/calc/MeasProduct', 2799.8000000000002)
  ('...
  
From Unix Shell
---------------

Using fandango.sh::

  for attr in $(fandango.sh get_matching_attributes "sr/di/calc/*Coup*"); do 
     echo "$attr : $(fandango.sh read_attribute ${attr})" ; 
     done
  
  sr/di/calc/SimulatorCoupling : 0.6
  sr/di/calc/UserDefCoupling : 0.6
  sr/di/calc/Coupling : 0.0
  sr/di/calc/SetMachineCoupling : False

See more Unix shell examples at :ref:`fandango_scripts`

  
   

