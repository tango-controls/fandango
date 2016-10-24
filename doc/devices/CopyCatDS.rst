
Install and test CopyCatDS
==========================

Install fandango library
------------------------

Note that you need PyTango pre-installed to run any fandango Device Server.

With PIP (may need sudo)::

  pip install --upgrade fandango

From a GIT clone (may need sudo)::

  git clone https://github.com/tango-controls/fandango
  cd fandango
  python setup.py install

If you're just trying it, I suggest to use a VirtualEnv (no sudo required)::

  virtualenv test --system-site-packages
  source test/bin/activate
  pip install --upgrade fandango
  source test/bin/activate #needed to update the PYTHONPATH

Setup your CopyCatDS 
--------------------

Create and setup the device from Jive or shell::

  fandango.sh add_new_device CopyCatDS/test CopyCatDS test/copycatds/01
  
**TargetDevice** property is used to point to the device to be copied (could belong to other tango_host):

  fandango.sh put_device_property test/copycatds/01 TargetDevice SYS/TG_TEST/1
  
The **CopyAttributes** can be used to select/filter the attributes to export (* is the default but image attributes are not well supported yet)::

  fandango.sh put_device_property test/copycatds/01 CopyAttributes '(?!.*image.*$)'

Start it
--------

Run it manually::

  python $(fandango.sh findModule fandango)/interface/CopyCatDS.py test -v2 &

Or add it to starter::

  

Show it with atkpanel or taurusdevicepanel::

  taurusdevicepanel test/copycatds/01 &
