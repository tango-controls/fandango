
import traceback
import threading
import time

def timeit(target,args=[],kwargs={},setup='pass',number=1):
  if isinstance(target,str):
    import timeit
    return timeit.timeit(target,setup,number=number)
  elif callable(target):
    t0 = time.time()
    try:
      [target(*args) for i in range(number)]
    except:
      traceback.print_exc()
    return time.time()-t0
    

def test_xtreme(device,attribute,value):
    import PyTango
    i,dp = 0,PyTango.DeviceProxy(device)
    try:
        while i<value:
            i+=1
            dp.read_attribute(attribute)
            threading.Event().wait(0.01)
    except:
        print '%s.read_attribute(%s) failed after %d retries' % (device,attribute,i)
        print traceback.format_exc()
        PyTango.DeviceProxy(dp.adm_name()).command_inout('kill')
    return
        