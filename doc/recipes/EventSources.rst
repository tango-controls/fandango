==============================
fandango.callbacks.EventSource
==============================

.. contents::

Description
-----------

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
 
Behaviour
---------

Main differences with TaurusAttribute:

- simplified API:: enablePolling and activatePolling become synonymous.
- polling works always:: but adapting frequency to received events.

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

...
