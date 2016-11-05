
Install and test CopyCatDS
==========================

Install fandango library
------------------------

Note that, although not mandatory, most of fandango requires PyTango previously installed.

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
  source test/bin/activate

Setup your CopyCatDS 
--------------------

Create and setup the device (image attributes not well supported yet)::

  fandango.sh add_new_device CopyCatDS/test CopyCatDS test/copycatds/01
  fandango.sh put_device_property test/copycatds/01 TargetDevice SYS/TG_TEST/1
  fandango.sh put_device_property test/copycatds/01 CopyAttributes '(?!.*image.*$)'

Start it
--------

::

  python $(fandango.sh findModule fandango)/interface/CopyCatDS.py test -v2 &

Show it with atkpanel or taurusdevicepanel::

  taurusdevicepanel test/copycatds/01 &
