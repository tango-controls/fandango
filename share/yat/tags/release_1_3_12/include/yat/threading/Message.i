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
 * \file    Message.i
 * \brief   Inlined code of the YAT Message abstraction class.
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

namespace yat
{

#if defined(_USE_MSG_CACHE_)
// ============================================================================
// Message::operator new - overload new operator (make class "cachable")
// ============================================================================
YAT_INLINE void * Message::operator new (size_t)
{
  YAT_TRACE_STATIC("Message::operator new");
  
  return (void *) Message::m_cache.malloc();
}

// ============================================================================
// Message::operator delete - overload delete operator (make class "cachable")
// ============================================================================
YAT_INLINE void Message::operator delete (void * p)
{
  YAT_TRACE_STATIC("Message::operator delete");
  
  Message::m_cache.free(reinterpret_cast<Message*>(p));
}
#endif

// ============================================================================
// Message::duplicate
// ============================================================================
YAT_INLINE Message * Message::duplicate (void)
{
  return reinterpret_cast<Message*>(this->SharedObject::duplicate ());
}

// ============================================================================
// Message::release
// ============================================================================
YAT_INLINE void Message::release (void)
{
  this->SharedObject::release ();
}
  
// ============================================================================
// Message::is_thread_ctrl_message
// ============================================================================
YAT_INLINE bool Message::is_thread_ctrl_message (void)
{
  return this->type_ == TASK_INIT || this->type_ == TASK_EXIT;
}

// ============================================================================
// Message::type
// ============================================================================
YAT_INLINE size_t Message::type (void) const
{
  return this->type_;
}

// ============================================================================
// Message::type
// ============================================================================
YAT_INLINE void Message::type (size_t t)
{
  this->type_ = t;
}

// ============================================================================
// Message::priority
// ============================================================================
YAT_INLINE size_t Message::priority (void) const
{
  return this->priority_;
}

// ============================================================================
// Message::priority
// ============================================================================
YAT_INLINE void Message::priority (size_t p)
{
  this->priority_ = p;
}

// ============================================================================
// template member impl: Message::user_data
// ============================================================================
YAT_INLINE void * Message::user_data (void) const
{
  return this->user_data_;
}

// ============================================================================
// template member impl: Message::user_data
// ============================================================================
YAT_INLINE void Message::user_data (void* _ud)
{
  this->user_data_ = _ud;
}

// ============================================================================
// Message::wait_processed
// ============================================================================
YAT_INLINE bool Message::wait_processed (unsigned long _tmo_ms)
  throw (Exception)
{
  YAT_TRACE("Message::wait_processed");
  
  AutoMutex<Mutex> guard (this->lock_);

  if (! this->waitable())
  {
    THROW_YAT_ERROR("PROGRAMMING_ERROR",
                    "Message::wait_processed called on a none waitable message [check code]",
                    "Message::wait_processed");
  }
  
  if (this->processed_)
    return true;
 
  return this->cond_->timed_wait(_tmo_ms);
}

// ============================================================================
// Message::processed
// ============================================================================
YAT_INLINE void Message::processed (void)
{
  YAT_TRACE("Message::processed");

  AutoMutex<Mutex> guard(this->lock_);

  this->processed_ = true;

  if (this->cond_) 
    this->cond_->broadcast();
}

// ============================================================================
// Message::waitable
// ============================================================================
YAT_INLINE bool Message::waitable (void) const
{
  return this->cond_ ? true : false;
}

// ============================================================================
// Message::has_error
// ============================================================================
YAT_INLINE bool Message::has_error (void) const
{
  return this->has_error_;
}

// ============================================================================
// Message::set_error
// ============================================================================
YAT_INLINE void Message::set_error (const Exception & e)
{
  this->has_error_ = true;
  this->exception_ = e;
}

// ============================================================================
// Message::get_error
// ============================================================================
YAT_INLINE const Exception & Message::get_error (void) const
{
  return this->exception_;
}

#if defined (YAT_DEBUG)
// ============================================================================
// Message::id
// ============================================================================
YAT_INLINE Message::MessageID Message::id (void) const
{
  return this->id_;
}

// ============================================================================
// Message::elapsed_msec
// ============================================================================
YAT_INLINE double Message::elapsed_msec (void)
{
  return this->timer_.elapsed_msec();
}

// ============================================================================
// Message::restart_timer
// ============================================================================
YAT_INLINE void Message::restart_timer (void)
{
  this->timer_.restart();
}
#endif //- YAT_DEBUG

} //- namespace

