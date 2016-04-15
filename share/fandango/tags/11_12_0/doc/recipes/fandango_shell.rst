
Fandango shell examples
=======================

Most fandango methods can be launched from Unix shell::

  # fandango.sh get_tango_host
  
    localhost:10000
  
  # fandango.sh findModule fandango
    
    /usr/lib/python2.7/site-packages/fandango
    
  # fandango.sh get_matching_attributes "mach/ct/composer/*"
  
    mach/ct/composer/averagepressure
    mach/ct/composer/averagecurrent
  
  # fandango.sh read_attribute mach/ct/composer/averagecurrent
  
    119.1
