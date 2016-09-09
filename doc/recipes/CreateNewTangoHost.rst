Creating a New Host with Fandango
---------------------------------

To create a new host in we will follow the same steps done by Astor:

 - create a new Starter in tango database
 - create the servers that will run in this host
 - assign devices to run-levels in the host
 
Code::

 import fandango as fn
 myhost = 'hostname'
 
 # Astor locates hosts by searching all tango/admin/* devices
 fn.tango.add_new_device('Starter/'+myhost,'Starter','tango/admin/'+myhost)
 
 # Create the servers to be run in this host
 # fn.tango_add_new_device('Server/Instance','Class','dev/ice/name')
 fn.tango_add_new_device('MyServer/Inst-A','MyClass','test/test/test-01')
 fn.tango_add_new_device('MyServer2/Inst-B','MyClass2','test/test/test-02')
 
 # Assing host and runlevels using fandango.Astor object
 astor = fn.Astor()
 astor.load_from_devs_list(['test/test/test-01','test/test/test-02')
 astor.set_server_level('MyServer/Inst-A',host=myhost,level=1)
 astor.set_server_level('MyServer2/Inst-B',host=myhost,level=2)
 
 # Before starting your servers, launch Starter in the host
 
 # Then, start the servers using Starter:
 
 astor.start_servers()
 
