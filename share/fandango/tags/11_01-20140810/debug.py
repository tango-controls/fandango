import PyTango
import traceback
import threading
def test_xtreme(device,attribute,value):
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
		