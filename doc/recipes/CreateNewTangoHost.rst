Creating a New Host with Fandango
---------------------------------

To create a new host in we will follow the same steps done by Astor:

- create a new Starter in tango database
- create the servers that will run in this host
- assign devices to run-levels in the host

Astor locates hosts by searching all tango/admin/* devices:

.. code-block:: python

 import fandango as fn
 myhost = 'hostname'
 fn.tango.add_new_device('Starter/'+myhost,'Starter','tango/admin/'+myhost)

You may need to setup the path to device servers executables:

.. code-block:: python

 fn.tango.put_device_property('tango/admin/'+myhost,'StartDsPath',['/opt/bin'])
 
**NOW**: launch Starter (manually) in your host!
 
Create the servers to be run in the host:

.. code-block:: python

 # fn.tango.add_new_device('Server/Instance','Class','dev/ice/name')
 fn.tango.add_new_device('PySignalSimulator/1','PySignalSimulator','test/test/A')
 fn.tango.add_new_device('PySignalSimulator/2','PySignalSimulator','test/test/B')

Start the servers using your already created starter:

.. code-block:: python

 astor = fn.Astor()
 astor.load_from_devs_list(['test/test/A','test/test/B')
 astor.start_servers(host=myhost)

Assing host and runlevels using fandango.Astor object:

.. code-block:: python

 astor.set_server_level('PySignalSimulator/1',host='controls03',level=2)
 astor.set_server_level('PySignalSimulator/2',host='controls03',level=3) 
 
