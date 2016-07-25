=======
SaverDS
=======


SaverAPI
========

The SaverAPI object will allow to access all SaverDS instances in the system.
This will allow to easily save, read, list files in the Saver ecosystem.
Files can be tracked by any host, using get_all_hosts() and get_host_devices() methods.

SaverDS Device Class
====================

Properties
----------

:SaveFolder: Folder where to save data; /tmp/ by default

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
