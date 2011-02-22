/*!
 * \file    Barrier.h
 * \brief   Header file of YAT portable Barrier implementation
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_BARRIER_H_
#define _YAT_BARRIER_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat/threading/Mutex.h>
#include <yat/threading/Condition.h>

namespace yat {

// ----------------------------------------------------------------------------
//! \class Barrier
//! \brief The YAT "a la Boost" Barrier class.
//!
//! An object of class barrier is a synchronization primitive used to cause a 
//! set of threads to wait until they each perform a certain function or each 
//! reach a particular point in their execution.
//!
//! When a Barrier is created, it is initialized with a thread count N. The 
//! first N-1 calls to \link wait wait \endlink will all cause their threads 
//! to be blocked. The Nth call to \link wait wait \endlink will allow all 
//! of the waiting threads to be woken up. The Nth call will also "reset" 
//! the barrier such that, if an additional N+1th call is made to \link wait 
//! wait \endlink, it will be as though this were the first call to \link wait 
//! wait \endlink; in other words, the N+1th to 2N-1th calls to \link wait wait
//! \endlink will cause their threads to be blocked, and the 2Nth call to \link 
//! wait wait\endlink will allow all of the waiting threads, including the 2Nth 
//! thread, to be woken up and reset the Barrier. This functionality allows the 
//! same set of N threads to re-use a Barrier object to synchronize their 
//! activity at multiple points during their execution.
//!
//! \remarks
//! While its destructor is virtual, this class is not supposed to be derived.\n
//! Be sure to clearly understand the internal behaviour before trying to do so.
// ----------------------------------------------------------------------------
class YAT_DECL Barrier
{
public:
  //! Constructor.
  //!
  //! Constructs a Barrier object that will cause \a count threads to block 
  //! on a call to \link wait wait \endlink.
  //! 
  //! \param count The number of threads to synchronize.
  Barrier (size_t count);

  //! Destructor.
  //!
  //! If threads are still blocking in a \link wait wait \endlink operation, 
  //! the behavior for these threads is undefined.
  virtual ~Barrier (void);

  //! Wait until N threads call \link wait wait \endlink, where N equals the 
  //! count provided to the constructor for the Barrier object. 
  //!
  //! \remarks 
  //! If the barrier is destroyed before wait() can return, the behavior is 
  //! undefined.
  void wait (void);

private:
  //! The number of threads to synchronize (involved threads).
  size_t m_thread_count;

  //! The mutex associated with m_condition
  Mutex m_mutex;

  //! The condition variable used to synchronized the involved threads.
  Condition m_condition;

  //! The number of threads currently waiting on the Barrier
  size_t m_waiters_count;

  //! Not implemented private member
  Barrier (const Barrier&);
  //! Not implemented private member
  Barrier & operator= (const Barrier&);
};

} // namespace yat

#if defined (YAT_INLINE_IMPL)
# include <yat/threading/Barrier.i>
#endif

#endif //- _YAT_BARRIER_H_
