===================
Catching Exceptions
===================
.. contents

Methods
=======

trial
-----

.. code:: python

  def trial(tries,excepts=None,args=None,kwargs=None,return_exception=None):
    """ This method executes a try,except clause in a single line
    :param tries: may be a callable or a list of callables
    :param excepts: it can be a callable, a list of callables, a map of {ExceptionType:[callables]} or just a default value to return	
    :param args,kwargs: arguments to be passed to the callable
    :return exception: whether to return exception or None (default)
    """


getLastException
----------------

returns last exception traceback

getPreviousExceptions
---------------------

returns the full exception stack

Decorators Catched/CatchedArgs
==============================

The @Catched and @CatchedArgs(verbose,rethrow,postmethod,...) allow to easily catch and print any exception occurring in python methods.

The verbose argument controls system output, while rethrow allows to print and then throw the exception again to the upper layer.

See fandango.excepts test code for examples:

.. code:: python

  print('Raise ZeroDivError:\n')
  @Catched
  def failed_f():
    return 1/0.
  failed_f()
  
  
  print('Show custom message:\n')
  def custom_msg(s):
    print('CUSTOM: %s'%s.split('\n')[-1])
  @CatchedArgs(postmethod=custom_msg,verbose=False)
  def failed_f():
    return 1/0
  failed_f()
  
  def devfailed(d,a):
    import PyTango
    dp = PyTango.DeviceProxy(d)
    return dp.read_attribute(a)
  
  print('Try a good tango call:\n')
  Catched(devfailed)('sys/tg_test/1','state')
  
  print('Try a bad attribute:\n')
  Catched(devfailed)('sys/tg_test/1','nanana')
  
  print('Raise DevFailed:\n')
  Catched(devfailed)('sys/tg_test/1','throw_exception')
  
  print('Try a rethrow:\n')
  try:
    CatchedArgs(rethrow=True)(devfailed)('sys/tg_test/1','throw_exception')
  except DevFailed,e:
    print('Catched!')
