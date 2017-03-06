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

Event flow
----------

PyTango Events are received by EventSource.push_event method. There, event.err, event(type), attr_conf and attr_value are extracted.  A tuple with (EventSource,type_,value) is inserted in the EventThread.queue

The EventThread.process loop will manage the events in queue; grouping received events by its source full name. 




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

Conditions for Client Polling
-----------------------------

Polling will be triggered from the client side if:

- Event source is registered in EventThread.sources (at least a listener has been added).
- source.getMode() is True ()
- last_read_time is older than (polling_period if isPollingEnabled() else KeepAlive).
- source.isPollingActive() is True or the EventThread.queue is EMPTY.

Thus, the KeepAlive polling (trigger a HW read() for attributes not receiving events) may not be ever executed if there are still many events in the queue to process.


Recipes
-------

Attribute used for the test::

  dev = 'sys/tg_devtest/1'
  attr = 'double_scalar'
  model = dev+'/'+attr

Create a proxy without listeners (just a Cached proxy)
......................................................

No polling should be active. Values should not be updated if read() is called faster than keeptime.

.. code:: python

  cached = fn.callbacks.TangoAttribute(model,keeptime=6000)
  t0,v0 = fn.now(),cached.read().value

  while fn.now() < t0+30.:
    fn.wait(1.)
    v = cached.read().value
    if v!=v0:
        print(fn.time2str(),v)
        v0 = v

  ('2017-03-06 12:41:26', -111.83805760016259)
  ('2017-03-06 12:41:32', -120.36249365482121)
  ('2017-03-06 12:41:38', -128.55702503785676)
  ('2017-03-06 12:41:44', -136.39919114627801)
  ('2017-03-06 12:41:50', -143.86749718418756)
  
Each read will try to fire client events, but it will have no effect unless a listener is added to the proxy.

If this is the only instantiated object the EventThread will not be active. If it is already active polling will not be enabled unless EventSource.getMode() returns True.

Proxy with listeners
....................

It has no secret::

 listened = fn.callbacks.TangoAttribute(model)
 el =  fn.callbackes.EventListener('test')
 el.setLogLevel('DEBUG')
 listened.addListener(el)
 
Automatically it will try to subscribe to Change,Archiving,Periodic events. You can avoid that using::

 #polled by client
 listened.addListener(el,use_events=False,use_polling=True) 
 
 #not polled nor subscribed, proxy updated only on explicit read() calls
 listened.addListener(el,use_events=False,use_polling=False) 

Persistent proxy with client polling
....................................

This test will show events only at client polling period::

  forced = fn.callbacks.TangoAttribute(model,enable_polling=True,polling_period=1000,use_events=False,loglevel='DEBUG')
  

Persistent proxy with events
............................

.. code::

  listened = fn.callbacks.TangoAttribute(model)
  listened.subscribe()
  listened.use_events
  Out[98]:['archive', 'change', 'periodic', 'quality']
  
This subscription will be persistent if you don't use listeners. But!, this may break if you add a listener and then remove all of them. This will disable events completely.

To ensure that an attribute is always subscribed, add the persistent flag at creation. This will add a permanent listener to ensure that events are never disabled::

  # This proxy is automatically subscribed to events if available.
  listened = fn.callbacks.TangoAttribute(model,persistent=True)
  
  listened = fn.callbacks.TangoAttribute(model,persistent=True,loglevel='DEBUG',use_events=['change'])

This test will show events only when pushed by device. From now on the device will start receiving events. If no listener is added there will be no callback, but the attribute cache will be always updated by the last event::
  
  In [133]:listened.read().value
  Out[133]:123.13220677602663
  In [134]:listened.read().value
  Out[134]:125.86398884679437
  In [147]:fn.now()-fn.ctime2time(listened.read().time)
  Out[147]:0.20083999633789062
  In [148]:fn.now()-fn.ctime2time(listened.read().time)
  Out[148]:0.82412290573120117
  In [149]:fn.now()-fn.ctime2time(listened.read().time)
  Out[149]:0.3119041919708252
  In [150]:fn.now()-fn.ctime2time(listened.read().time)
  Out[150]:0.039993047714233398

If this period is longer than keep_alive; and slow polling starts::

  EventThread    INFO 2017-03-06 16:29:50.668: KeepAlive(tango://controls02:10000/sys/tg_test/1/double_scalar) after   15000.0 ms
EventThread    INFO 2017-03-06 16:30:20.681: KeepAlive(tango://controls02:10000/sys/tg_test/1/double_scalar) after 15000.0 ms
EventThread    INFO 2017-03-06 16:30:50.680: KeepAlive(tango://controls02:10000/sys/tg_test/1/double_scalar) after 15000.0 ms
EventThread    INFO 2017-03-06 16:31:20.676: KeepAlive(tango://controls02:10000/sys/tg_test/1/double_scalar) after 15000.0 ms


  
