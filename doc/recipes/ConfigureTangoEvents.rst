Configuring Tango Events
========================

The module fandango.tango provides 4 methods to manage attribute events:

Use them like::

  import fandango as fn
  curr = 'sr/di/dcct/averagecurrent'
  fn.tango.get_attribute_events(curr)
  {'arch_event': [0.05, None, 320.0], 'per_event': [1000.0], 'polling': 0}
  fn.tango.check_attribute_events('sr/di/dcct/averagecurrent')
  Out: {tango._tango.EventType.CHANGE_EVENT: True}
  
  # True means pushed, so the arch_event can be removed
  fn.tango.set_attribute_events(curr,arch_abs_event=0,arch_per_event=0)
  
  

check_attribute_events
----------------------

::

  def check_attribute_events(model,ev_type=None,verbose=False):
    """
    This method expects model and a list of event types.
    If empty, CHANGE and ARCHIVE events are tested.
    
    It will return a dictionary with:
     - keys: available event types
     - value: True for code-pushed events, int(period) for polled-based
     
    """

check_device_events
-------------------

::

  def check_device_events(device):
    """
    apply check_attribute_events to all attributes of the device
    """

get_attribute_events
--------------------

::

  def get_attribute_events(target,polled=True,throw=False):
    """
    Get current attribute events configuration 

    Pushed events will be not show, attributes not polled may not works
    
    Use check_attribute_events to verify if events are really working
    
    TODO: it uses Tango Device Proxy, should be Tango Database instead to 
    allow offline checking
    """

set_attribute_events
--------------------

::
    
  def set_attribute_events(target, polling = None, rel_event = None, 
                        abs_event = None, per_event = None,
                        arch_rel_event = None, arch_abs_event = None, 
                        arch_per_event = None,verbose = False):
    """
    Allows to set independently each event property of the attribute
    
    Event properties should have same type that the attribute to be set    
    
    Polling must be integer, in millisecons
    
    from fandango 14.3.0 onwards
    Setting any event to 0 or False will erase the current configuration
    
    """
                        
