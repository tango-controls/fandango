//----------------------------------------------------------------------------
// YAT4Tango LIBRARY
//----------------------------------------------------------------------------
//
// Copyright (C) 2006-2009  The Tango Community
//
// The YAT4Tango library is free software; you can redistribute it and/or 
// modify it under the terms of the GNU General Public License as published 
// by the Free Software Foundation; either version 2 of the License, or (at 
// your option) any later version.
//
// The YAT4Tango library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
// Public License for more details.
//
// See COPYING file for license details  
//
// Contact:
//      Nicolas Leclercq
//      Synchrotron SOLEIL
//------------------------------------------------------------------------------
/*!
 * \authors N.Leclercq, J.Malik - Synchrotron SOLEIL
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
public:

	//! Default ctor
	DeviceTask (Tango::DeviceImpl * dev);
  
  //! Ctor
	DeviceTask (const yat::Task::Config& cfg, Tango::DeviceImpl * dev);

	//! Dtor
	virtual ~DeviceTask ();

	//! Starts the task
  virtual void go (size_t tmo_ms = kDEFAULT_MSG_TMO_MSECS);
    //-> might throw (Tango::DevFailed)

 	//! Starts the task 
  //! An exception is thrown in case the specified message:
  //!   * is not of type yat::TASK_INIT
  //!   * is not "waitable"
  virtual void go (yat::Message * msg, size_t tmo_ms = kDEFAULT_MSG_TMO_MSECS);
    //-> might throw (Tango::DevFailed)

	//! Aborts the task (join with the underlying thread before returning).
  virtual void exit ();
    //-> might throw (Tango::DevFailed)

  //! Posts a message to the task
	virtual void post (yat::Message * msg, size_t tmo_msecs = kDEFAULT_POST_MSG_TMO);
    //-> might throw (Tango::DevFailed)

	//! Posts a message to the task then wait for this msg to be handled
	virtual void wait_msg_handled (yat::Message * msg, size_t tmo_msecs = kDEFAULT_MSG_TMO_MSECS);
    //-> might throw (Tango::DevFailed)

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
