/*!
 * \file    DeviceTask.h
 * \brief   Header file of the YAT4tango DeviceTask class.
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _DEVICE_TASK_H_
#define _DEVICE_TASK_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat/threading/Task.h>
#include <yat4tango/Export.h>
#include <yat4tango/ExceptionHelper.h>

namespace yat4tango
{

// ============================================================================
// class: DeviceTask
// ============================================================================
class YAT4TANGO_DECL DeviceTask : public yat::Task, public Tango::LogAdapter
{
  //! a yat4tango::DeviceTask = yat::Task 
  //!                         + yat <-> tango exception handling
  //!                         + Tango logging support
  //-TODO: write some doc here

public:

	//! Default ctor
	DeviceTask (Tango::DeviceImpl * dev);
  
  //! Ctor
	DeviceTask (const yat::Task::Config& cfg, Tango::DeviceImpl * dev);

	//! Dtor
	virtual ~DeviceTask (void);

	//! Starts the task
  virtual void go (size_t tmo_ms = kDEFAULT_MSG_TMO_MSECS);
    //- throw (Tango::DevFailed)

 	//! Starts the task 
  //! An exception is thrown in case the specified message:
  //!   * is not of type yat::TASK_INIT
  //!   * is not "waitable"
  virtual void go (yat::Message * msg, size_t tmo_ms = kDEFAULT_MSG_TMO_MSECS);
    //- throw (Tango::DevFailed)

	//! Aborts the task (join with the underlying thread before returning).
  virtual void exit (void);
    //- throw (Tango::DevFailed)

  //! Posts a message to the task
	virtual void post (yat::Message * msg, size_t tmo_msecs = kDEFAULT_POST_MSG_TMO);
    //- throw (Tango::DevFailed)

	//! Posts a message to the task then wait for this msg to be handled
	virtual void wait_msg_handled (yat::Message * msg, size_t tmo_msecs = kDEFAULT_MSG_TMO_MSECS);
    //- throw (Tango::DevFailed)

protected:

  //! the yat::Task message handler (pure virtual method implementation)
  //! do not overload this method - its purpose is to deal with Tango to yat exception handling
  //! see DeviceTask::process_message below
  virtual void handle_message (yat::Message& msg)
    throw (yat::Exception);
    
  //! the actual yat::Message handler (must be implemented by derived classes)
  //! be sure that your implementation only throws Tango::DevFailed exceptions
  virtual void process_message (yat::Message& msg)
    throw (Tango::DevFailed) = 0;
};

} // namespace

#if defined (YAT_INLINE_IMPL)
# include <yat4tango/DeviceTask.i>
#endif // YAT_INLINE_IMPL

#endif // _DEVICE_TASK_H_
