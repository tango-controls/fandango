// ============================================================================
//
// = CONTEXT
//		TANGO Project - DeviceTask example
//
// = File
//		MyDeviceTask.cpp
//
// = AUTHOR
//		Nicolas Leclercq - SOLEIL
//
// ============================================================================

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <math.h>
#include <yat/threading/Mutex.h>
#include "MyDeviceTask.h"

// ============================================================================
// SOME CONSTs
// ============================================================================
#define kMAX_RAND_VECTOR_LEN      1024
#define kTARGET_DEVICE_NAME       "tmp/test/tangotest_1" //- should be a property!
#define kTARGET_DEVICE_ATTR_NAME  "long_scalar"
// ----------------------------------------------------------------------------
static const double __NAN__ = ::sqrt(-1);
// ----------------------------------------------------------------------------
 
// ============================================================================
// SOME USER DEFINED MESSAGES
// ============================================================================
#define kDOUBLE_SCALAR_MSG (yat::FIRST_USER_MSG + 1000)

namespace ThreadedDevice_ns
{
	// ======================================================================
	// MyDeviceTask::MyDeviceTask
	// ======================================================================
  MyDeviceTask::MyDeviceTask (size_t _periodic_timeout_ms, Tango::DeviceImpl * _host_device)
    : yat4tango::DeviceTask(_host_device),
		  random_vector(kMAX_RAND_VECTOR_LEN),
		  dp(0)
	{
		//- reset data content to NAN
		random_vector.fill(__NAN__);

    //- configure optional msg handling
    this->enable_timeout_msg(false);
    this->enable_periodic_msg(true);
    this->set_periodic_msg_period(_periodic_timeout_ms);
	}

	// ======================================================================
	// MyDeviceTask::~MyDeviceTask
	// ======================================================================
	MyDeviceTask::~MyDeviceTask (void)
	{
    //- noop
	}

	// ============================================================================
	// MyDeviceTask::process_message
	// ============================================================================
	void MyDeviceTask::process_message (yat::Message& _msg)
	{
	  DEBUG_STREAM << "MyDeviceTask::handle_message::receiving msg " << _msg.to_string() << std::endl;

	  //- handle msg
    switch (_msg.type())
	  {
	    //- THREAD_INIT ----------------------
	    case yat::TASK_INIT:
	      {
  	      DEBUG_STREAM << "MyDeviceTask::handle_message::THREAD_INIT::thread is starting up" << std::endl;

  	      //- "initialization" code goes here
          //----------------------------------------------------

  	      //- instanciate our ThreadSafeDeviceProxyHelper
  			  this->dp = new Tango::DeviceProxy(kTARGET_DEVICE_NAME);
          if (this->dp == 0)
          {
            THROW_DEVFAILED(_CPTC ("OUT_OF_MEMORY"),
                            _CPTC ("yat::ThreadSafeDeviceProxyHelper allocation failed"),
                            _CPTC ("MyDeviceTask::handle_message"));
          }
        } 
		    break;
        
		  //- THREAD_EXIT ----------------------
		  case yat::TASK_EXIT:
		    {
  			  DEBUG_STREAM << "MyDeviceTask::handle_message::THREAD_EXIT::thread is quitting" << std::endl;

  			  //- "release" code goes here
          //----------------------------------------------------
          
  			  //- release the ThreadSafeDeviceProxyHelper
          if (this->dp)
          {
            delete this->dp;
            this->dp = 0;
          }
        }
			  break;
        
		  //- THREAD_PERIODIC ------------------
		  case yat::TASK_PERIODIC:
		    {
  		    DEBUG_STREAM << "MyDeviceTask::handle_message::handling THREAD_PERIODIC msg" << std::endl;

          //- code relative to the task's periodic job goes here
          //----------------------------------------------------
          
		      { //- enter critical section
            yat::AutoMutex<> guard(this->m_lock);

  		      //- fill the random vector in a thread safe manner...
  		      for (size_t i = 0; i < random_vector.length(); i++)
                *(random_vector.base() + i) = ::rand();

            //- let's read an attribute on our target device
            try
            {
              //- this->dp->read_attribute...
            }
            catch (const Tango::DevFailed& df)
            {
              ERROR_STREAM << "Tango exception caught while trying to read on devproxy" << std::endl;
              ERROR_STREAM << df << std::endl;
              //- to something to manage the error...
            }
          } //- leave critical section
        }
		    break;
        
		  //- THREAD_TIMEOUT -------------------
		  case yat::TASK_TIMEOUT:
		    {
  		    //- code relative to the task's tmo handling goes here

  		    DEBUG_STREAM << "MyDeviceTask::handle_message::handling THREAD_TIMEOUT msg" << std::endl;
        }
		    break;
        
		  //- USER_DEFINED_MSG -----------------
		  case kDOUBLE_SCALAR_MSG:
		    {
  		  	DEBUG_STREAM << "MyDeviceTask::handle_message::handling kDOUBLE_SCALAR_MSG user msg" << std::endl;

  		  	//- get msg data...
  		  	//- msg data is always dettached by reference (i.e. pointer) and ownership is transfered 
          //- to the caller. it means that we will have to delete the returned pointer in order to 
          //- avoid memory leaks. that's the semantic of the yat::Message::dettach_data member!
          //- thanks to the template impl of yat::Message::dettach_data, we could extract any kind
          //- of data. here we just expect a single double...
  		    double my_double_value = _msg.get_data<double>();
          //- dump the received value
          DEBUG_STREAM << "MyDeviceTask::handle_message::double scalar value is " 
                       << my_double_value 
                       << std::endl;
  		  }
  		  break;
        
      //- UNHANDLED MSG --------------------
  		default:
  		  DEBUG_STREAM << "MyDeviceTask::handle_message::unhandled msg type received" << std::endl;
  			break;
	  }

	  DEBUG_STREAM << "MyDeviceTask::handle_message::message_handler:msg " 
                 << _msg.to_string() 
                 << " successfully handled" 
                 << std::endl;
  }

	// ============================================================================
	// MyDeviceTask::get_data
	// ============================================================================
	MyDeviceTask::MyDataBuffer * MyDeviceTask::get_data (void)
	{
    //- allocate the returned buffer
    MyDeviceTask::MyDataBuffer * data = 
            new MyDeviceTask::MyDataBuffer(this->random_vector.length());
    if (data == 0)
    {
      THROW_DEVFAILED(_CPTC ("OUT_OF_MEMORY"),
                      _CPTC ("MyDataBuffer allocation failed"),
                      _CPTC ("MyDeviceTask::get_data"));
    }

  	//- fill the returned buffer in a thread safe manner...
		{ //- enter critical section
      yat::AutoMutex<> guard(this->m_lock);
      //- copy using the yat::DataBuffer::operator=
		  *data = this->random_vector;
    } //- leave critical section

    return data;
 }

} // namespace
