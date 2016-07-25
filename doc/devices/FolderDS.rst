========
FolderDS
========


FolderAPI(ServersDict)
======================

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
