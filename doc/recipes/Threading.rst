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

Class that provides a multiprocessing interface to process tasks in a background process and throw callbacks when finished.

The queries are sent between sender/receiver thread and worker process using tuples.
Queries may be: (key,) ; (key,target) ; (key,target,args):

- key is just an identifier to internally store data results and callbacks
- if target is a callable it will be thrown with args as argument (use [] if target is a void function)
- if it isn't, then executor(target) will be called
- executor can be fandango.evalX or other object/method assigned using WorkerProcess.bind(class,args)

By default fandango.evalX is used to perform tasks, a different executor can be defined as WorkerProcess argument or calling::

  CP = WorkerProcess(targetClass(initArgs))
  CP.bind(targetClass,initArgs)

Sending tasks to the process::

  CP.send(key='A1',target) 
  # Returns immediately and executes target() or executor(*target) in a background process
  CP.send('A1',target,args,callback=callback) 
  # Returns immediately, executes x=target(args) in background and launches callback(x) when ready
  
When a (key,target,args) tuple is received the procedure is:

* obtain the exec_ method (executor if args is None, 
* obtain arguments (target if args is None, if args is map/sequence it is pre-parsed):
* if args is None and there's a valid executor: return executor(target)

How the executable method is obtained:

- if args is None it tries to get a valid executor and target will be args.
- if target is string first it tries to get executor.target
- if failed, then it evals target (that may return an executable)
- if args is not none and target is not string, target is used as executable if callable
Return value:
- if a valid executable method is found it returns exec_([*/**]args)
- if not, it returns what has been found instead (evalX(target), executor.target or target)

To use it like a threadDict, allowing a fixed list of keys to be permanently updated::

  CP.add(key,target,args,period,expire,callback)
  #This call will add a key to dictionary, which target(args) method will be executed every period, value obtained will expire after X seconds.
  #Optional Callback will be executed every time value is updated.

Throwing commands in a sequential way (it will return when everything already in the queue is done)::

  CP.command('comm') # Execute comm() and returns result
  CP.command('comm',args=(,)) # Execute comm(*args) and returns result

Two different dictionaries will keep track of process results:

- data : will store named data with and update period associated
- callbacks : will store associated callbacks to throw-1 calls  

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
