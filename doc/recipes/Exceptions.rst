===================================
Catching Exceptions with Decorators
===================================

The @Catched and @CatchedArgs(verbose,rethrow,postmethod,...) allow to easily catch and print any exception occurring in python methods.

The verbose argument controls system output, while rethrow allows to print and then throw the exception again to the upper layer.

See fandango.excepts test code for examples:

.. code::

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
