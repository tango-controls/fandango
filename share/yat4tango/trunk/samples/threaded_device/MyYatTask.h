// ============================================================================
//
// = CONTEXT
//		TANGO Project - DeviceTask example
//
// = File
//		MyYatTask.h
//
// = AUTHOR
//		Nicolas Leclercq - SOLEIL
//
// ============================================================================

#ifndef _MY_YAT_TASK_H_
#define _MY_YAT_TASK_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <tango.h>
#include <yat/DataBuffer.h>
#include <yat/threading/Task.h>

namespace ThreadedDevice_ns
{

// ============================================================================
// class: MyYatTask
// ============================================================================
class MyYatTask : public yat::Task, public Tango::LogAdapter
{
public:
  //- create a dedicated type from the yat::Buffer template class
  typedef yat::Buffer<double> MyDataBuffer;

	//- ctor ---------------------------------
	MyYatTask (size_t _periodic_timeout_ms, Tango::DeviceImpl * _host_device);

	//- dtor ---------------------------------
	virtual ~MyYatTask (void);

  //- returns the last available data ------
  MyYatTask::MyDataBuffer * get_data (void)
    throw (Tango::DevFailed);

protected:
	//- handle_message -----------------------
	virtual void handle_message (yat::Message& msg)
		throw (Tango::DevFailed);

private:
  //- the actual data produced by the task
  MyDataBuffer random_vector;

  //- a device proxy
  Tango::DeviceProxy * dp;

  //- the host device
  Tango::DeviceImpl * host_dev;
};

} // namespace ThreadedDevice_ns

#endif // _MY_YAT_TASK_H_
