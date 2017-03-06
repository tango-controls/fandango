====================================================
fandango.callbacks.EventSource and EventListener API
====================================================

.. contents::

Description
===========

In a future release, fandango taurus.core dependencies will be fully replaced by 3 new objects:

 - EventSource : replacing TaurusAttribute
 - TangoEventSource : replacing TangoAttribute and/or CachedAttributeProxy
 - EventListener : replacing TaurusBaseComponent
 - EventThread : replacing TaurusPollingThread
 
This new Source/Listener API for polling events is added to fandango.callbacks module.

It is being developed in the new-cache-proxy branch.

Motivation
----------
These developments tried to resolve some of the issues found in the EventTest study and XBPM devices performance.

 http://github.com/sergirubio/EventTest
 
Synchronous / Asynchronous modes and glossary
---------------------------------------------

:poll(): an explicit call to AttributeProxy.Read()

:read(): a read() call from client will trigger poll() only if mode = Synchronous or if no event has been received yet.

:Synchronous: Client forces each communication  calling the read() method.

:Cached: A read() call returns the last processed value. In the case of a Synchronous client it will trigger a poll() call if the previous value was expired (t > KeepTime).

:Asynchronous: Clients don't force communications, instead it receives events triggered by  the EventThread or reads the last cache.

:Polled: Some devices may not provide events, or the event system may be not working for unknown reasons (pure asynchronous control is not used by any institute but Alba). In this cases, a periodical poll() will be scheduled by the EventThread (not a timer, just a lazy schedule to avoid cpu overloading).

Behaviour
=========

See the class definition to see argument definition at creation:

https://github.com/tango-controls/fandango/blob/develop/fandango/callbacks.py#L319

The Class __doc__ is::

    Simplified implementation of Taurus Attribute/Model and fandango.CachedAttributeProxy classes 
    
    It implements CachedAttributeProxy methods but doesnt inherit from it; 
    this regression is due to the lack of reliability of AttributeProxy in PyTango 9.
    
    Documentation at doc/recipes/EventsAndCallbacks.rst
    
    Slow Polling will be always enabled, as a KeepAlive is always kept reading
    the attribute values at an slow rate.
    
    Well, will be always enabled as long there are Listeners or Forced is True. If not polling
    will not be activated and it will be simply a CachedAttributeProxy.
    
    In this implementation, just a faster polling will be enabled if the 
    attribute provides no events. But the slow polling will never be fully disabled.
    
    If no events are received after EVENT_TIMEOUT, polling wil be also enabled.
    
    It will also subscribe to all attribute events, not only CHANGE and CONFIG
    
    All types are: 'CHANGE_EVENT,PERIODIC_EVENT,QUALITY_EVENT,ARCHIVE_EVENT,ATTR_CONF_EVENT,DATA_READY_EVENT,USER_EVENT'
    
    Arguments to EventSource(...) are:
    
    - name : attribute name (simple or full)
    - parent : device name or proxy
    - enablePolling (force polling by default)
    - pollingPeriod (3000)
    - keeptime (500 ms) min. time (in ms!) between HW reads
    - tango_asynch = True/False ; to use asynchronous Tango reading
    - listeners = a list of listeners to be added at startup
    
    Keep in mind that if tango_asynch=True; you will not get the latest value 
    when doing  read(cache=False). You must use read(cache=False,asynch=False) instead.
    

Differences with TaurusAttribute
--------------------------------

- simplified API:: enablePolling and activatePolling become synonymous.
- polling works always:: but adapting frequency to received events.
- event-fail tolerant:: uses slow polling to verify if events are working properly.
- polling-late tolerant:: if polling is late triggers warning but still returning a value.




use_events and polling_period properties
----------------------------------------

If both use_events or polling_period are False the attribute reading will be always synchronous, but cached if keep_time != 0.

If use_events or polling_period>0 then the asynchronous mode applies; using the EventThread to manage both the event queue and the polling schedule.

apart, there will be hw_asynch flag to manage if polling is done using asynchronous reading or not. But it will affect only to hw polling and not to synchronous reads.

The new Proxy is called EventSource as it will trigger event_received in all listeners at each event or poll() call; even on synchronous calls.

As TaurusAttribute
..................

It will be implemented when having a listener. This is the behaviour expected 
for persistent clients (PyAlarm, Composers).

Events are subscribed and polling is enabled. Polling is slow by default (15s.), 
switching to 3 seconds (or less) only if events not available.


As a CachedAttributeProxy (TangoEval)
.....................................

It will be used when no listener is provided. This is the behaviour for 
occasional clients (Panic GUI, ipython). 

Events are not subscribed, polling is not active, all reads go directly to HW
except those with period < keepTime ; thus returning a Cached value.



Recipes
-------

Attribute used for the test:

  dev = 'sys/tg_devtest/1'
  attr = 'double_scalar'
  model = dev+'/'+attr

Create a proxy without listeners (just a Cached proxy)
......................................................

No polling should be visible. Values should not be updated if read() is called faster than keeptime.

Persistent proxy with client polling
....................................

This test will show events only at client polling period

Persistent proxy with events
............................

This test will show events only at device polling period.

If this period is longer than keep_alive; polled values should appear.



