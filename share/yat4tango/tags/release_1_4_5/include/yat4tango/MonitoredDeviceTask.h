//----------------------------------------------------------------------------
// YAT4Tango LIBRARY
//----------------------------------------------------------------------------
//
// Copyright (C) 2006-2010  The Tango Community
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
 * \authors N.Leclercq - Synchrotron SOLEIL
 */

#ifndef _MONITORED_DEVICE_TASK_H_
#define _MONITORED_DEVICE_TASK_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat4tango/DeviceTask.h>
#include <yat4tango/MonitoredDevice.h>

namespace yat4tango
{

// ============================================================================
// class: MonitoredMonitoredDeviceTask
// ============================================================================
class YAT4TANGO_DECL MonitoredDeviceTask : private yat4tango::DeviceTask, 
                                           public yat4tango::MonitoredDevice
{
public:
	//! Ctor
  //@param monitored_device The device to monitor
  //@param host_device The host Tango device (for logging purpose)
	MonitoredDeviceTask (const std::string & monitored_device, 
                       Tango::DeviceImpl * host_device = 0);

	//! Dtor
	virtual ~MonitoredDeviceTask ();

	//! Starts the underlying Task (i.e. start polling the device)
  //! Default polling freq. is 1 Hz (i.e. 1000 msecs period)
  void start ()
    throw (Tango::DevFailed);

	//! Suspends the polling mecanism
  void suspend ();

	//! Resumes the polling mecanism
  void resume ();

	//! Asks the the underlying Task to exit
  void quit ()
    throw (Tango::DevFailed);
  
  //- Sets the attributes polling period (unit is milliseconds)
  void set_polling_period (size_t pp_msecs);

  //- Returns the attributes polling period (unit is milliseconds)
  size_t get_polling_period () const;

protected:
  //! yat::Message handler
  //! You can overload this method in order to define your own task behaviour.
  //! In this case, don't forget to call the MonitoredDevice::poll_attributes 
  //! method uppon receipt of the yat::TASK_PERIODIC message.
  virtual void process_message (yat::Message& msg)
    throw (Tango::DevFailed);

private:
  //- suspend/resume flag
  bool m_suspended;

  //- polling period
  size_t m_pp;
};

} // namespace

#endif // _MONITORED_DEVICE_TASK_H_
