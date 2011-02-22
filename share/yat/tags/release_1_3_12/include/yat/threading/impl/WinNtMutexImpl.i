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
 * \file
 * \brief    
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
 */

namespace yat {

// ****************************************************************************
// YAT NULL MUTEX IMPL
// ****************************************************************************
// ----------------------------------------------------------------------------
// NullMutex::lock
// ----------------------------------------------------------------------------
YAT_INLINE void NullMutex::lock (void)
{
 //- noop
}

// ----------------------------------------------------------------------------
// NullMutex::acquire
// ----------------------------------------------------------------------------
YAT_INLINE void NullMutex::acquire (void)
{
 //- noop
}

// ----------------------------------------------------------------------------
// NullMutex::unlock
// ----------------------------------------------------------------------------
YAT_INLINE void NullMutex::unlock (void)
{
 //- noop
}

// ----------------------------------------------------------------------------
// NullMutex::release
// ----------------------------------------------------------------------------
YAT_INLINE void NullMutex::release (void)
{
 //- noop
}

// ----------------------------------------------------------------------------
// NullMutex::try_lock
// ----------------------------------------------------------------------------
YAT_INLINE MutexState NullMutex::try_lock (void)
{
  return yat::MUTEX_LOCKED;
}

// ----------------------------------------------------------------------------
// NullMutex::try_acquire
// ----------------------------------------------------------------------------
YAT_INLINE MutexState NullMutex::try_acquire (void)
{
  return yat::MUTEX_LOCKED;
}

// ****************************************************************************
// YAT MUTEX IMPL
// ****************************************************************************
// ----------------------------------------------------------------------------
// Mutex::lock
// ----------------------------------------------------------------------------
YAT_INLINE void Mutex::lock (void)
{
  //-TODO: the following may fail
  ::WaitForSingleObject(this->m_nt_mux, INFINITE);
}

// ----------------------------------------------------------------------------
// Mutex::acquire
// ----------------------------------------------------------------------------
YAT_INLINE void Mutex::acquire (void)
{
  this->lock();
}
// ----------------------------------------------------------------------------
// Mutex::try_acquire
// ----------------------------------------------------------------------------
YAT_INLINE MutexState Mutex::try_acquire (void)
{
  return this->try_lock();
}

// ----------------------------------------------------------------------------
// Mutex::unlock
// ----------------------------------------------------------------------------
YAT_INLINE void Mutex::unlock (void)
{
  //-TODO: the following may fail
  ::ReleaseMutex(this->m_nt_mux); 
}

// ----------------------------------------------------------------------------
// Mutex::acquire
// ----------------------------------------------------------------------------
YAT_INLINE void Mutex::release (void)
{
  this->unlock();
}

// ----------------------------------------------------------------------------
// Mutex::try_lock
// ----------------------------------------------------------------------------
YAT_INLINE MutexState Mutex::try_lock (void)
{
  switch (::WaitForSingleObject(this->m_nt_mux, 0))
  {
    case WAIT_OBJECT_0:
      return MUTEX_LOCKED;
    case WAIT_TIMEOUT:
      return MUTEX_BUSY;
  }
  //- make some compilers happy
  return MUTEX_LOCKED;
}


} // namespace yat
