.. _fandango_scripts:

fandango.scripts package
========================

Most methods from fandango can be directly called from unix shell:

Usage::

  fandango.sh [-h/--help] [-x/--extra] [fandango_method_0] [fandango_method_1] [...]

  Objects and Generators will not be allowed as arguments, only python primitives, lists and tuples

  
Examples::

  fandango.sh findModule fandango
  
  fandango.sh get_tango_host
  
  fandango.sh --help get_matching_devices | less
  
  fandango.sh get_matching_devices "tango/admin/*"
  
  fandango.sh get_matching_attributes "lab/ct/plctest16/*_af"
  
  fandango.sh -h | grep propert
  
  fandango.sh get_matching_device_properties "lab/ct/plctest16" "*modbus*"
  
  fandango.sh read_attribute "tango/admin/pctest/status"
  
  for attr in $(fandango.sh get_matching_attributes "tango/admin/pctest/*"); do echo "$attr : $(fandango.sh read_attribute ${attr})" ; done



Submodules
----------

.. toctree::

   fandango.scripts.fandango.sh
   fandango.scripts.fandango.qt
   fandango.scripts.csv2tango
   fandango.scripts.servers_lite
   fandango.scripts.tango2csv
   fandango.scripts.tango_create_device
   fandango.scripts.tango_create_starter
   fandango.scripts.tango_starter

Module contents
---------------

.. automodule:: fandango.scripts
    :members:
    :undoc-members:
    :show-inheritance:

