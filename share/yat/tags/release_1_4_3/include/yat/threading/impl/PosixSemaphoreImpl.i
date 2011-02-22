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
  this->timed_wait(0);
}

// ----------------------------------------------------------------------------
// Semaphore::timed_wait
// ----------------------------------------------------------------------------
YAT_INLINE bool Semaphore::timed_wait (unsigned long _tmo_msecs)
{
  bool r = false;
  this->m_mux.lock();
  while (! this->m_value)
  {
    r = this->m_cond.timed_wait(_tmo_msecs);
  }
  if (r)
  {
    this->m_value--;
  }
  this->m_mux.unlock();
  return r;
}

// ----------------------------------------------------------------------------
// Semaphore::try_wait
// ----------------------------------------------------------------------------
YAT_INLINE SemaphoreState Semaphore::try_wait (void)
{
  SemaphoreState s;
  this->m_mux.lock();
  if (this->m_value > 0)
  {
    this->m_value--;
    s = SEMAPHORE_DEC;
 	}
	else
	{
	  s = SEMAPHORE_NO_RSC;
	}
  this->m_mux.unlock();
  return s;
}

// ----------------------------------------------------------------------------
// Semaphore::post
// ----------------------------------------------------------------------------
YAT_INLINE void Semaphore::post (void)
{
  this->m_mux.lock();
  this->m_value++;
  this->m_cond.signal();
  this->m_mux.unlock();
}

} // namespace yat
