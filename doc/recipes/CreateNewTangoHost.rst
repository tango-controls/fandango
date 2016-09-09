Creating a New Host with Fandango
---------------------------------

To create a new host in we will follow the same steps done by Astor:

 - create a new Starter in tango database
 - create the servers that will run in this host
 - assign devices to run-levels in the host
 
Code::

 import fandango as fn
 myhost = 'hostname'
 
Astor locates hosts by searching all tango/admin/* devices::

 fn.tango.add_new_device('Starter/'+myhost,'Starter','tango/admin/'+myhost)
 
Before starting your servers, launch Starter (manually) in the host ...
 
Create the servers to be run in this host::
 
 # fn.tango.add_new_device('Server/Instance','Class','dev/ice/name')
 fn.tango.add_new_device('PySignalSimulator/1','PySignalSimulator','test/test/A')
 fn.tango.add_new_device('PySignalSimulator/2','PySignalSimulator','test/test/B')

Start the servers using your already created starter::

 astor = fn.Astor()
 astor.load_from_devs_list(['test/test/A','test/test/B')
 astor.start_servers(host=myhost)

Assing host and runlevels using fandango.Astor object::

 astor.set_server_level('PySignalSimulator/1',host='controls03',level=2)
 astor.set_server_level('PySignalSimulator/2',host='controls03',level=3) 
 
