/*!
 * \file    Barrier.cpp
 * \brief   YAT portable Barrier implementation
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat/threading/Barrier.h>

#if !defined (YAT_INLINE_IMPL)
# include <yat/threading/Barrier.i>
#endif // YAT_INLINE_IMPL


namespace yat {

// ----------------------------------------------------------------------------
// Barrier::Barrier
// ----------------------------------------------------------------------------
Barrier::Barrier (size_t _count)
 : m_thread_count (_count),
   m_condition (m_mutex),
   m_waiters_count (0)
{
  YAT_TRACE("Barrier::Barrier");

  YAT_LOG("Barrier::Barrier:: " << m_thread_count << " threads involved");
}

// ----------------------------------------------------------------------------
// Barrier::~Barrier
// ----------------------------------------------------------------------------
Barrier::~Barrier (void)
{
  YAT_TRACE("Barrier::Barrier");
}

// ----------------------------------------------------------------------------
// Barrier::wait
// ----------------------------------------------------------------------------
void Barrier::wait (void)
{
  //- enter critical section
  MutexLock guard(this->m_mutex);

  //- increment waiters count
  this->m_waiters_count++;

  YAT_LOG("Barrier::wait::thread " << DUMP_THREAD_UID << "::about to wait on Barrier");

  //- are all expected threads waiting on the barrier?
  if (this->m_waiters_count == m_thread_count)
  {
    YAT_LOG("Barrier::wait::all expected waiters present. Reset/notify Barrier...");
    //- reset the barrier
    this->m_waiters_count = 0;
    //- notify all waiters
    this->m_condition.broadcast();
    //- done: return 
    return;
  }

  //- make the calling thread wait
  this->m_condition.wait();

  YAT_LOG("Barrier::wait::thread " << DUMP_THREAD_UID << "::woken up");
}

} // namespace yat
