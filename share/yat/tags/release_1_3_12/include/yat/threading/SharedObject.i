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
 * \file    SharedObject.i
 * \brief   Inlined code of the YAT shared object class.
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

namespace yat
{

// ============================================================================
// SharedObject::reference_count
// ============================================================================
YAT_INLINE int SharedObject::reference_count (void) const
{
  return this->reference_count_;
}

// ============================================================================
// SharedObject::lock
// ============================================================================
YAT_INLINE void SharedObject::lock (void)
{
  this->lock_.lock();
}

// ============================================================================
// SharedObject::mutex
// ============================================================================
YAT_INLINE void SharedObject::unlock (void)
{
  this->lock_.unlock();
}

// ============================================================================
// SharedObject::mutex
// ============================================================================
YAT_INLINE Mutex & SharedObject::mutex (void)
{
  return this->lock_;
}

}  // namespace
