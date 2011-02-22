//----------------------------------------------------------------------------
// YAT4Tango LIBRARY
//----------------------------------------------------------------------------
//
// Copyright (C) 2006-2010 The Tango Community
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

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat4tango/MonitoredDeviceTask.h>

namespace yat4tango
{

// ======================================================================
// MonitoredDeviceTask::MonitoredDeviceTask
// ======================================================================
MonitoredDeviceTask::MonitoredDeviceTask (const std::string & mon_dev, Tango::DeviceImpl * host_dev)
  : yat4tango::DeviceTask (host_dev), 
    yat4tango::MonitoredDevice (mon_dev, host_dev),
    m_suspended (false),
    m_pp (1000)
{
	YAT_TRACE("MonitoredDeviceTask::MonitoredDeviceTask");
}

// ======================================================================
// MonitoredDeviceTask::~MonitoredDeviceTask
// ======================================================================
MonitoredDeviceTask::~MonitoredDeviceTask ()
{
	YAT_TRACE("MonitoredDeviceTask::~MonitoredDeviceTask");
}

// ======================================================================
// MonitoredDeviceTask::start
// ======================================================================
void MonitoredDeviceTask::start ()
  throw (Tango::DevFailed)
{
  this->enable_timeout_msg(true);

  this->enable_periodic_msg(true);
  this->set_periodic_msg_period(this->m_pp);

  this->DeviceTask::go();
}

// ======================================================================
// MonitoredDeviceTask::suspend
// ======================================================================
void MonitoredDeviceTask::suspend ()
{
  this->m_suspended = true;
}

// ======================================================================
// MonitoredDeviceTask::resume
// ======================================================================
void MonitoredDeviceTask::resume ()
{
  this->m_suspended = false;
}

// ======================================================================
// MonitoredDeviceTask::quit
// ======================================================================
void MonitoredDeviceTask::quit ()
  throw (Tango::DevFailed)
{
  this->DeviceTask::exit();
}

// ======================================================================
// MonitoredDeviceTask::set_polling_period 
// ======================================================================
void MonitoredDeviceTask::set_polling_period (size_t pp_msecs)
{
  if (pp_msecs == 0) 
    pp_msecs = this->m_pp;

  this->m_pp = pp_msecs;
}

// ======================================================================
// MonitoredDeviceTask::get_polling_period
// ======================================================================
size_t MonitoredDeviceTask::get_polling_period () const
{
  return this->m_pp;
}

// ======================================================================
// MonitoredDeviceTask::process_message
// ======================================================================
void MonitoredDeviceTask::process_message (yat::Message& msg)
    throw (Tango::DevFailed)
{
  switch (msg.type())
  {
    case yat::TASK_INIT:
    case yat::TASK_PERIODIC:
      if (! this->m_suspended)
        this->MonitoredDevice::poll_attributes();
      break;
    default:
      break;
  }
}

} // namespace
