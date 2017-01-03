Create and launch new devices
=============================

.. contents::

Import fandango
---------------

.. code-block:: python

  # git clone https://github.com/tango-controls/fandango
  # cd fandango
  # python setup.py install     
  #or export PYTHONPATH=$(pwd):$PYTHONPATH 
  
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


Move devices between servers
----------------------------

.. code-block:: python

  import fandango as fn
  oldserver = 'Pool/1'
  newserver = 'Pool/2'
  sd = fn.ServersDict(oldserver)
  for c in sd.get_all_classes():
    devs = sd.get_class_devices(c)
    for d in devices:
      fn.tango.add_new_device(newserver,c,d) 
