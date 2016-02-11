Create and launch new devices
=============================

Import fandango
---------------

  import fandango.tango as tango
  import fandango as fn

Creating a new server
---------------------

  klass = 'PyAttributeProcessor'
  server = 'PyAttributeProcessor/SR_CT_CALC'
  tango.add_new_device(server,klass,'SR/CT/CALC-01')
  tango.add_new_device(server,klass,'SR/CT/CALC-02')

Starting and setting runlevel
-----------------------------

  astor = fn.Astor(server)
  astor.start_servers(host='controlshost01')
  astor.set_server_level(server,'controlshost01',3)

Crosscheck devices
------------------
  
  astor.states()
    ('pyattributeprocessor/sr_ct_calc', PyTango._PyTango.DevState.ON)



