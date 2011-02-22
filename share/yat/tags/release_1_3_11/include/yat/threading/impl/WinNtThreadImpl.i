/*!
 * \file
 * \brief    
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
 */

namespace yat {

// ****************************************************************************
// YAT THREAD IMPL
// ****************************************************************************
// ----------------------------------------------------------------------------
// Thread::priority
// ----------------------------------------------------------------------------
YAT_INLINE Thread::Priority Thread::priority (void)
{
  //- enter critical section
  yat::AutoMutex<> guard(this->m_lock);

  return this->m_priority;
}
// ----------------------------------------------------------------------------
// Thread::state
// ----------------------------------------------------------------------------
YAT_INLINE Thread::State Thread::state (void)
{
  //- enter critical section
  yat::AutoMutex<> guard(this->m_lock);

  return this->m_state;
}
// ----------------------------------------------------------------------------
// Thread::state_i
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
  ::Sleep(0);
}
// ----------------------------------------------------------------------------
// Thread::sleep
// ----------------------------------------------------------------------------
YAT_INLINE void Thread::sleep (unsigned long _msecs)
{
  ThreadingUtilities::sleep(0, 1000000 * _msecs);
}
// ----------------------------------------------------------------------------
// Thread::self
// ----------------------------------------------------------------------------
YAT_INLINE ThreadUID Thread::self (void) const
{
  return this->m_uid;
}

} // namespace yat
