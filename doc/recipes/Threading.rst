=============================
Threading Classes in Fandango
=============================

.. contents::

Asynchronous methods / Tasklets
===============================

threads.AsynchronousFunction
----------------------------

...

threads.SubprocessMethod
------------------------

...


threads.ThreadedObject
======================

Developed for managing callbacks.EventThread queue within device servers. It provides
a persistent pool of threads running always in background with methods for clean
starting/pausing/killing and debugging.

Use target=callable or set_target(callable) to pass a method to be started periodically.

Properties
----------------------------

:target: task (callable) to be executed periodically
:period: seconds between executions

It can be set at initialization or using setters/getters.

Other Options at init()
-----------------------

:nthreads=1: *NOT IMPLEMENTED*: Split tasks in multiple threads.
:start=False: start to process tasks at startup (bg threads are always started)
:min_wait=1e-5: The internal threads will do its best to accomplish periods even if it is not allowed
by the current period config and task duration. In this case, min_wait will become the minimal 
time between executions.

Behaviour
---------

Once started, the threaded object will execute its task periodically. 

:start(): starts processing tasks (threads already running)
:stop(): pauses the threads, but not really stops them
:kill(): effectively end all threads; called at __del__


Diagnostics 
-----------

ThreadedObject will try to automatically compensate task execution time reducing
the delay between periods; but it will not trigger exception if late. It just provides
methods to inspect its performance externally.

:get_count:
:get_errors:
:get_delay:
:get_acc_delay:
:get_usage:
:get_next:
:get_last:
:is_alive(): tells you if it has been killed; 
:get_started(): whether if it is processing data

Class methods
-------------

This class keeps an INSTANCES list with all instantiated objects. 
It enables stop_all() / kill_all() methods to switch off all running threads.

threads.Worker``*``
===================

WorkerThread
------------

... Mostly based on delayed execution of functional.evalX

SingletonWorker
---------------

...

WorkerProcess
-------------

...

Pool
----

...

CronTab
-------

...

QThreads
========

qt.ModelRefresher
-----------------

...

qt.QWorker
----------

...

dicts.ThreadDict / DefaultThreadDict
====================================

...
