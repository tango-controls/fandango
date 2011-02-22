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
