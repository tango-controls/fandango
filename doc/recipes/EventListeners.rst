=======================
EventListener / EventSource
=======================

Synchronous / Asynchronous modes and glossary
=========================================

:poll(): an explicit call to AttributeProxy.Read()

:read(): a read() call from client will trigger poll() only if mode = Synchronous or if no event has been received yet.

:Synchronous: Client forces each communication  calling the read() method.

:Cached: A read() call returns the last processed value. In the case of a Synchronous client it will trigger a poll() call if the previous value was expired (t > KeepTime).

:Asynchronous: Clients don't force communications, instead it receives events triggered by  the EventThread or reads the last cache.

:Polled: Some devices may not provide events, or the event system may be not working for unknown reasons (pure asynchronous control is not used by any institute but Alba). In this cases, a periodical poll() will be scheduled by the EventThread (not a timer, just a lazy schedule to avoid cpu overloading).

use_events and polling_period properties
==================================

If both use_events or polling_period are False the attribute reading will be always synchronous, but cached if keep_time != 0.

If use_events or polling_period>0 then the asynchronous mode applies; using the EventThread to manage both the event queue and the polling schedule.

apart, there will be hw_asynch flag to manage if polling is done using asynchronous reading or not. But it will affect only to hw polling and not to synchronous reads.

The new Proxy is called EventSource as it will trigger event_received in all listeners at each event or poll() call; even on synchronous calls.

