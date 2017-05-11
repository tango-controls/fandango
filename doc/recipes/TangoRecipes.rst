===================
Basic Tango Recipes
===================

Some recipes on using fandango and Tango

.. contents::

Create Tango devices from shell
===============================

The fandango api provides helper commands to create devices and assign properties:

.. code:: python

  import fandango as fn
  fn.tango.add_new_device('Server/Instance','Class','your/device/name')
  fn.tango.put_device_property('your/device/name','Property','Value')


You can also call them from shell (use fandango.sh in <12.6 releases)::

  > fandango add_new_device Server/Instance Class your/device/name
  > fandango put_device_property your/device/name Property Value


To start it on any host managed by Starter::

  > tango_servers "yourhostname" start "YourServer/YourInstance"
  
Visualize its state::

  > tango_servers status "YourServer/YourInstance"
  
  > fandango check_device your/device/name
  
Or just browse how a system behaves using wildcards:

  > tango_servers status "PyPLC/*"
  
  > tando_servers hostname status "*/*"


Get devices or attributes matching a regular expression
=======================================================

Using fandango.tango.get_matching_devices or get_matching_attributes:

.. code:: python

  from fandango import tango
  tango.get_matching_devices('sr[0-9]+/vc/(ipct|vgct)*')
  ['SR01/VC/IPCT-01A08-01',
   'SR01/VC/IPCT-01A08-02',
   'SR01/VC/IPCT-02A01-01',
   'SR01/VC/VGCT-01A08-01',
   'SR01/VC/VGCT-02A01-01',
   'SR02/VC/IPCT-02A02-01',
   
   tango.get_matching_attributes('bo01*corv*/current')
   ['bo01/pc/corv-01/Current',
    'bo01/pc/corv-03/Current',
    'bo01/pc/corv-05/Current',
    'bo01/pc/corv-06/Current',
    'bo01/pc/corv-07/Current',
    'bo01/pc/corv-09/Current',
    'bo01/pc/corv-11/Current']
     
   import fandango as fn
   fn.kmap(tango.read_attribute,tango.get_matching_attributes('bo01*corv*/current'))
   [('bo01/pc/corv-01/Current', 0.090130000000000002),
    ('bo01/pc/corv-03/Current', 0.084650000000000003),
    ('bo01/pc/corv-05/Current', 0.099900000000000003),
    ('bo01/pc/corv-06/Current', -0.054309999999999997),
    ('bo01/pc/corv-07/Current', 0.0099299999999999996),
    ('bo01/pc/corv-09/Current', 0.052699999999999997),
    ('bo01/pc/corv-11/Current', 0.081900000000000001)]  
   
Search for device attribute/properties matching a regular expression:

.. code:: python

  fandango.tango.get_matching_device_properties('s01/*/*ct*','serial*')
  {'S01/VC/IPCT-01': {'SerialLine': 'S01/VC/SERIAL-01'},
   'S01/VC/IPCT-02': {'SerialLine': 'S01/VC/SERIAL-02'},
   'S01/VC/VGCT-01': {'SerialLine': 'S01/VC/SERIAL-10'}}
   


Obtain all information from a device
====================================

.. code:: python

  In [59]:fandango.tango.get_device_info('sr/vc/gll')
  Out[59]:fandango.Struct({
        'name': sr/vc/gll,
        'level': 4,
        'started': 11th February 2013 at 13:07:37,
        'PID': 11024,
        'ior': ...,
        'server': PyStateComposer/SR_VC,
        'host': nanana01,
        'stopped': 11th February 2013 at 12:49:49,
        'exported': 1,        })

start/stop all device servers in a machine (like Astor -> Stop All)
===================================================================

.. code:: python

  import fandango
  fandango.Astor(hosts=['my.host']).stop_all_servers()

  astor = fandango.Astor(hosts=['my.host'])
  astor.start_all_servers()

if you just want to see if things are effectively running or not::

  astor.states()
  

Example: Fast property update
=============================

This example will collect all running instances of PyAlarm and will replace its properties

.. code:: python

  import fandango as fn
  servers = fandango.Astor('PyAlarm/*')
  # Get running servers
  running = [s for for s,v in servers.states().items() if v is not None]
  # Get the list of devices
  devs = fn.chain(*[servers[s].get_device_list() for s in running])
  
  for d in devs:
    if not d.startswith('dserver'):
      prop = servers.proxies[d].get_property(['AlarmReceivers'])['AlarmReceivers']
      # Modify property values
      prop = [s.replace('%SRUBIO','%DFERNANDEZ') for s in prop]
      servers.proxies[d].put_property({'AlarmReceivers':prop})
      
  # Reload the devices properties
  for d in devs: 
    servers.proxies[d].Init()
  
Use TangoEval to evaluate strings containing Tango Attributes
=============================================================

TangoEval class provides PyAlarm-like evaluation of strings containing attribute names (replacing them by its values). It is part of fandango.device module.
The result of each evaluation is stored in te.result.

.. code:: python

  from fandango import TangoEval
  te = TangoEval('(s01/vc/gauge-01/pressure + s01/vc/gauge-01/pressure) / 2.')

  [Out]: TangoEval: result = 7.2e-10
  


