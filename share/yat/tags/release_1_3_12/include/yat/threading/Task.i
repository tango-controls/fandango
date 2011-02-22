//----------------------------------------------------------------------------
// YAT LIBRARY
//----------------------------------------------------------------------------
//
// Copyright (C) 2006-2009  The Tango Community
//
// Part of the code comes from the ACE Framework
// see http://www.cs.wustl.edu/~schmidt/ACE.html for more about ACE
//
// The thread native implementation has been initially inspired by omniThread
// - the threading support library that comes with omniORB. 
// see http://omniorb.sourceforge.net/ for more about omniORB.
//
// Contributors form the TANGO community:
// Ramon Sunes (ALBA) 
//
// The YAT library is free software; you can redistribute it and/or modify it 
// under the terms of the GNU General Public License as published by the Free 
// Software Foundation; either version 2 of the License, or (at your option) 
// any later version.
//
// The YAT library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
// Public License for more details.
//
// A copy of the GPL version 2 is available below. 
//
// Contact:
//      Nicolas Leclercq
//      Synchrotron SOLEIL
//------------------------------------------------------------------------------

/*!
 * \file    Task.i
 * \brief   Inlined code of the YAT task class.
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

namespace yat
{

// ============================================================================
// Task::enable_timeout_msg
// ============================================================================
YAT_INLINE void Task::enable_timeout_msg (bool behaviour)
{
  this->msg_q_.enable_timeout_msg_ = behaviour;
}

// ============================================================================
// Task::timeout_msg_enabled
// ============================================================================
YAT_INLINE bool Task::timeout_msg_enabled (void) const
{
  return this->msg_q_.enable_timeout_msg_;
}

// ============================================================================
// Task::set_timeout_msg_period
// ============================================================================
YAT_INLINE void Task::set_timeout_msg_period (size_t _tmo)
{
  this->timeout_msg_period_ms_ = _tmo;
}

// ============================================================================
// Task::get_timeout_msg_period
// ============================================================================
YAT_INLINE size_t Task::get_timeout_msg_period (void) const
{
  return this->timeout_msg_period_ms_;
}

// ============================================================================
// Task::enable_periodic_msg
// ============================================================================
YAT_INLINE void Task::enable_periodic_msg (bool b)
{
  this->msg_q_.enable_periodic_msg_ = b;
}

// ============================================================================
// Task::periodic_msg_enabled
// ============================================================================
YAT_INLINE bool Task::periodic_msg_enabled (void) const
{
  return this->msg_q_.enable_periodic_msg_;
}

// ============================================================================
// Task::set_periodic_timeout
// ============================================================================
YAT_INLINE void Task::set_periodic_msg_period (size_t _tmo)
{
  this->periodic_msg_period_ms_ = _tmo;
}

// ============================================================================
// Task::get_timeout_msg_period
// ============================================================================
YAT_INLINE size_t Task::get_periodic_msg_period (void) const
{
  return this->periodic_msg_period_ms_;
}

// ============================================================================
// Task::actual_timeout_msg_period
// ============================================================================
YAT_INLINE size_t Task::actual_timeout (void) const
{
  if (this->msg_q_.enable_periodic_msg_ && this->periodic_msg_period_ms_)
    return this->periodic_msg_period_ms_;
  if (this->msg_q_.enable_timeout_msg_ && this->timeout_msg_period_ms_)
    return this->timeout_msg_period_ms_;
  return kDEFAULT_TASK_TMO_MSECS;
}

// ============================================================================
// Task::post
// ============================================================================
YAT_INLINE void Task::post (yat::Message * _msg, size_t _tmo_msecs)
    //- throw (Exception)
{
  this->msg_q_.post (_msg, _tmo_msecs);
}

} //- namespace
