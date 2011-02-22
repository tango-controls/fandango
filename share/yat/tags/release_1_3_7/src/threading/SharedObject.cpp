/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat/threading/SharedObject.h>

#if !defined (YAT_INLINE_IMPL)
# include <yat/threading/SharedObject.i>
#endif

namespace yat
{

// ============================================================================
// SharedObject::SharedObject
// ============================================================================
SharedObject::SharedObject (void) 
 : reference_count_ (1)
{
  YAT_TRACE("SharedObject::SharedObject");
}

// ============================================================================
// SharedObject::~SharedObject
// ============================================================================
SharedObject::~SharedObject (void)
{
  YAT_TRACE("SharedObject::~SharedObject");

  DEBUG_ASSERT(this->reference_count_ == 0);
}

// ============================================================================
// SharedObject::duplicate
// ============================================================================
SharedObject * SharedObject::duplicate (void)
{
  YAT_TRACE("SharedObject::duplicate");

  MutexLock guard(this->lock_);

  this->reference_count_++;

  return this;
}

// ============================================================================
// SharedObject::release
// ============================================================================
int SharedObject::release (bool _commit_suicide)
{
  YAT_TRACE("SharedObject::release");

  SharedObject * more_ref = this->release_i ();

  if (! more_ref && _commit_suicide)
    delete this;

  return more_ref ? 1 : 0;
}

// ============================================================================
// SharedObject::release_i
// ============================================================================
SharedObject *SharedObject::release_i (void)
{
  MutexLock guard (this->lock_);

  DEBUG_ASSERT(this->reference_count_ > 0);

  this->reference_count_--;

  return (this->reference_count_ == 0) ? 0 : this;
}

} //- namespace
