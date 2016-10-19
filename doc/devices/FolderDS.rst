========
FolderDS
========

Usage
=====

The FolderDS/FolderAPI objects have been developed to allow the remote usage of log/config files.

You can use it to export your local files to the whole Tango Control System, so the FolderGUI can search for them.

You can also use it to write your logs into a remote machine, e.g. for saving local space or have persistent storage.

To start using the FolderDS API follow these steps:

* Create a FolderDS device:

.. code:: python

 import fandango.tango as ft
 ft.add_new_device('FolderDS/test','FolderDS','test/folder/tmp')
 ft.put_device_property('test/folder/tmp','SaveFolder','/tmp/folderds')
 ft.Astor('test/folder/tmp').start_servers()

* Load the API and save a file:

.. code:: python

 import fandango.device
 folders = fandango.device.FolderAPI()
 folders.save('test/folder/tmp','test.txt','Hello World!')
 
* Retrieve the contents from a client, even from another tango_host

.. code:: python

 import fandango.device
 folders = fandango.device.FolderAPI()
 v = folders.read('dbhost:10000/test/folder/tmp','test.txt')
 print(v)
   "Hello World!"
   
* Browse the stored files from FolderGUI (you'll need to add devices from other tango_hosts to FolderDS.ExtraDevices property)

.. code:: python

 import fandango.tango as ft
 devs = ft.get_class_property
 import fandango.device.FolderGUI
 ui = fandango.device.FolderGUI.main()

FolderAPI(fandango.ProxiesDict)
===============================

The FolderAPI object will allow to access all FolderDS instances in the system.
This will allow to easily save, read, list files in the FolderDS system.
Files can be tracked by any host, using get_all_hosts() and get_host_devices() methods.

FolderDS(DynamicDS)
===================

Properties
----------

:SaveFolder: Folder where to save data; /tmp/folderds by default

:DefaultMethod: Command to be called when from SaveFile(); SaveText by default.


Commands
--------

:SaveFile: It Calls the DefaultMethod

:SaveText: args (filename,[data]); it will save the contents of data as /$SaveFolder/filename

:GetFile: Returns contents of file

:GetFileTime: Returns timestamp of filename

:ListFiles: List all files matching mask (Use \* for getting all)

Attributes
----------

:State: Not Implemented

Other Methods
-------------

save_text_file
