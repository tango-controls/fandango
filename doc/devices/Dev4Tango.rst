========================
Dev4Tango Template Class
========================

.. contents::

Description
===========

This class provides several new features to TangoDevice implementations.
By including log.Logger it also includes objects.Object as parent class.
It allows to use call__init__(self, klass, *args, **kw) to avoid multiple inheritance from same parent problems.
Therefore, use self.call__init__(PyTango.Device_4Impl,cl,name) instead of PyTango.Device_4Impl.__init__(self,cl,name)
    
It also allows to connect several devices within the same server avoiding the taurus.core dependency.

To enable it just inherit from it and call init_my_Logger right after getting the device properties:

.. code::

  class Agilent4UHV(Dev4Tango):
   
   def __init__(self,cl,name):
     self.call__init__(Dev4Tango,cl,name)
     self.init_device()
     
   def init_device(self):
     self.get_device_properties(self.get_device_class())
     self.init_my_Logger(self)
    
State Machine
=============

The default state machine has been overriden to not allow qualities to modify the device state.

The is_Attr_allowed method provides a generic attribute disable when stat in INIT or UNKNOWN

Overriden methods are set_state, dev_state, State and get_state, default_status, is_Attr_allowed

Properties Initialization
=========================

:check_properties(props): verify that all properties have a proper value

:get_device_properties(class): it reads all properties and, if missing, updates the database with the default values

:update_properties(props): writes the default values to the database.

Child Attributes Update
=======================

*TODO* To be replaced by fandango.callbacks.EventListener API

API used by IonPump, PLCValve, VacuumGauge and PyStateComposer devices to periodically update the values of other devices
using an internal background thread.

Methods:

:subscribe_external_attributes(device,attributes):

:unsubscribe_external_attributes: remove all

:write_external_attribute(device,attribute,data):

:launch_external_command(device,target,argin):

:update_external_attributes: thread main loop.

Helper Methods
==============

:init_logger: initialize the internal logger and self.error/warning/info/debug/trace methods.

:getAttributeTime(any): extract epoch time from any of the different value objects in Tango

:getAttributeTemplate(name,type,rw,unit,format): Returns an Attr object ready to be inserted with self.add_attribute(&Attr,&reader,&writer,&allowed)

:get_devs_in_server(class): obtains the DevImpl objects instantiated in the same server

:get_admin_device: returns the admin device object itself, not a proxy

:get_polled_attrs: returns the list of internal polled attributes

:set_polled_attribute/set_polled_command: enables polling using the internal admin object

:event_received(source,type,value): event hook


    
    
