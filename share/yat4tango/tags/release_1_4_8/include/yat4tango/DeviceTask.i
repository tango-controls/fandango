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
 * \authors N.Leclercq, J.Malik - Synchrotron SOLEIL
 */

namespace yat4tango
{

// ============================================================================
// DeviceTask::handle_message
// ============================================================================
YAT_INLINE void DeviceTask::handle_message (yat::Message& msg)
  throw (yat::Exception)
{
  try
  {
    this->process_message(msg);
  }
  catch (const Tango::DevFailed& df)
  {
    throw TangoYATException(df);
  }
  catch (...)
  {
    throw yat::Exception();
  }
}

// ============================================================================
// DeviceTask::go
// ============================================================================
YAT_INLINE void DeviceTask::go (size_t _tmo_msecs)
  //- throw (Tango::DevFailed)
{
  try
  {
    this->Task::go(_tmo_msecs);
  }
  catch (const yat::Exception& ye)
  {
    throw YATDevFailed(ye);
  }
}

// ============================================================================
// DeviceTask::go
// ============================================================================
YAT_INLINE void DeviceTask::go (yat::Message * _msg, size_t _tmo_msecs)
  //- throw (Tango::DevFailed)
{
  try
  {
    this->Task::go(_msg, _tmo_msecs);
  }
  catch (const yat::Exception& ye)
  {
    throw YATDevFailed(ye);
  }
}
    
// ============================================================================
// DeviceTask::exit
// ============================================================================
YAT_INLINE void DeviceTask::exit ()
  //- throw (Tango::DevFailed)
{
  try
  {
    this->Task::exit();
  }
  catch (const yat::Exception& ye)
  {
    throw YATDevFailed(ye);
  }
}

// ============================================================================
// DeviceTask::post
// ============================================================================
YAT_INLINE void DeviceTask::post (yat::Message * _msg, size_t _tmo_msecs)
  //- throw (Tango::DevFailed)
{
  try
  {
    this->Task::post(_msg, _tmo_msecs);
  }
  catch (const yat::Exception& ye)
  {
    throw YATDevFailed(ye);
  }
}

// ============================================================================
// DeviceTask::wait_msg_handled
// ============================================================================
YAT_INLINE void DeviceTask::wait_msg_handled (yat::Message * _msg, size_t _tmo_msecs)
  //- throw (Tango::DevFailed)
{
  try
  {
    this->Task::wait_msg_handled(_msg, _tmo_msecs);
  }
  catch (const yat::Exception& ye)
  {
    throw YATDevFailed(ye);
  }
}

} //- namespace
