/*!
 * \file
 * \brief    
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
 */

namespace yat {

// ----------------------------------------------------------------------------
// Semaphore::wait
// ----------------------------------------------------------------------------
YAT_INLINE void Semaphore::wait (void)
{
  DWORD result = ::WaitForSingleObject(this->m_nt_sem, INFINITE);

  DEBUG_ASSERT(result != WAIT_OBJECT_0);
}

// ----------------------------------------------------------------------------
// Semaphore::timed_wait
// ----------------------------------------------------------------------------
YAT_INLINE bool Semaphore::timed_wait (unsigned long _tmo_msecs)
{
  DWORD result = ::WaitForSingleObject(this->m_nt_sem, _tmo_msecs);

  if (result == WAIT_TIMEOUT)
    return false;

  DEBUG_ASSERT(result == WAIT_OBJECT_0);

  return true;
}

// ----------------------------------------------------------------------------
// Semaphore::try_wait
// ----------------------------------------------------------------------------
YAT_INLINE SemaphoreState Semaphore::try_wait (void)
{
  DWORD result = ::WaitForSingleObject(this->m_nt_sem, 0);

  if (result == WAIT_TIMEOUT)
    return SEMAPHORE_NO_RSC;

  DEBUG_ASSERT(result == WAIT_OBJECT_0);

  return SEMAPHORE_DEC;
}

// ----------------------------------------------------------------------------
// Semaphore::post
// ----------------------------------------------------------------------------
YAT_INLINE void Semaphore::post (void)
{
  BOOL result = ::ReleaseSemaphore(this->m_nt_sem, 1, WIN_NT_NULL);

  DEBUG_ASSERT(result == TRUE);
}

} // namespace yat
