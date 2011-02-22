/*!
 * \file
 * \brief    
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
 */

namespace yat {

// ----------------------------------------------------------------------------
// Condition::wait
// ----------------------------------------------------------------------------
YAT_INLINE void Condition::wait (void)
{
  this->timed_wait(0);
}

// ----------------------------------------------------------------------------
// Condition::signal
// ----------------------------------------------------------------------------
YAT_INLINE void Condition::signal (void)
{
  ::pthread_cond_signal(&m_posix_cond);
}

// ----------------------------------------------------------------------------
// Condition::broadcast
// ----------------------------------------------------------------------------
YAT_INLINE void Condition::broadcast (void)
{
  ::pthread_cond_broadcast(&m_posix_cond);
}

} // namespace yat
