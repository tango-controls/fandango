/*!
 * \file
 * \brief    
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
 */

namespace yat {

// ----------------------------------------------------------------------------
// Thread::priority
// ----------------------------------------------------------------------------
YAT_INLINE Thread::Priority Thread::priority (void)
{
  //- enter critical section
  yat::MutexLock guard(this->m_lock);

  return this->m_priority;
}
// ----------------------------------------------------------------------------
// Thread::state
// ----------------------------------------------------------------------------
YAT_INLINE Thread::State Thread::state (void)
{
  //- enter critical section
  yat::MutexLock guard(this->m_lock);

  return this->m_state;
}
// ----------------------------------------------------------------------------
// Thread::state
// ----------------------------------------------------------------------------
YAT_INLINE Thread::State Thread::state_i (void) const
{
  return this->m_state;
}
// ----------------------------------------------------------------------------
// Thread::yield
// ----------------------------------------------------------------------------
YAT_INLINE void Thread::yield (void)
{
#if (PthreadDraftVersion == 6)
  ::pthread_yield(NULL);
#elif (PthreadDraftVersion < 9)
  ::pthread_yield();
#else
  ::sched_yield();
#endif
}
// ----------------------------------------------------------------------------
// Thread::sleep
// ----------------------------------------------------------------------------
YAT_INLINE void Thread::sleep (unsigned long _msecs)
{
#define kNSECS_PER_SEC  1000000000
#define kNSECS_PER_MSEC 1000000

  unsigned long secs = 0;
  unsigned long nanosecs = kNSECS_PER_MSEC * _msecs;

	while (nanosecs >= kNSECS_PER_SEC)
	{
		secs += 1;
		nanosecs -= kNSECS_PER_SEC;
	}

  ThreadingUtilities::sleep(secs, nanosecs);

#undef kNSECS_PER_MSEC
#undef kNSECS_PER_SEC
}
// ----------------------------------------------------------------------------
// Thread::self
// ----------------------------------------------------------------------------
YAT_INLINE ThreadUID Thread::self (void) const
{
  return this->m_uid;
}

} // namespace yat
