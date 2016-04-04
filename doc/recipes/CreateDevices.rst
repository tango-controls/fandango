Create and launch new devices
=============================

Import fandango
---------------

.. code-block:: python

  import fandango.tango as tango
  import fandango as fn

Creating a new server
---------------------

.. code-block:: python

  klass = 'PyAttributeProcessor'
  server = 'PyAttributeProcessor/SR_CT_CALC'
  tango.add_new_device(server,klass,'SR/CT/CALC-01')
  tango.add_new_device(server,klass,'SR/CT/CALC-02')

Starting and setting runlevel
-----------------------------

.. code-block:: python

  astor = fn.Astor(server)
  astor.start_servers(host='controlshost01')
  astor.set_server_level(server,'controlshost01',3)

Crosscheck devices
------------------

.. code-block:: python
  
  astor.states()
    ('pyattributeprocessor/sr_ct_calc', PyTango._PyTango.DevState.ON)



