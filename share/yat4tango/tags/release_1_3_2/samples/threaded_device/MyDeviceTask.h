// ============================================================================
//
// = CONTEXT
//		DeviceTask example
//
// = File
//		MyDeviceTask.h
//
// = AUTHOR
//		Nicolas Leclercq - SOLEIL
//
// ============================================================================

#ifndef _MY_DEVICE_TASK_H_
#define _MY_DEVICE_TASK_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <tango.h>
#include <yat/DataBuffer.h>
#include <yat4tango/DeviceTask.h>

namespace ThreadedDevice_ns
{

// ============================================================================
// class: MyDeviceTask
// ============================================================================
class MyDeviceTask : public yat4tango::DeviceTask
{
public:
  //- create a dedicated type from the yat::Buffer template class
  typedef yat::Buffer<double> MyDataBuffer;

	//- ctor ---------------------------------
	MyDeviceTask (size_t _periodic_timeout_ms, Tango::DeviceImpl * _host_device);

	//- dtor ---------------------------------
	virtual ~MyDeviceTask (void);

  //- returns the last available data ------
  MyDeviceTask::MyDataBuffer * get_data (void);

protected:
	//- process_message (implements yat4tango::DeviceTask pure virtual method)
	virtual void process_message (yat::Message& msg);

private:
  //- the actual data produced by the task
  MyDataBuffer random_vector;

  //- a device proxy
  Tango::DeviceProxy * dp;
};

} // namespace ThreadedDevice_ns

#endif // _MY_DEVICE_TASK_H_
