/*!
 * \file
 * \brief    
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
 */

namespace yat {

// ****************************************************************************
// YAT NULL MUTEX IMPL
// ****************************************************************************
// ----------------------------------------------------------------------------
// NullMutex::lock
// ----------------------------------------------------------------------------
YAT_INLINE void NullMutex::lock (void)
{
 //- noop
}

// ----------------------------------------------------------------------------
// NullMutex::acquire
// ----------------------------------------------------------------------------
YAT_INLINE void NullMutex::acquire (void)
{
 //- noop
}

// ----------------------------------------------------------------------------
// NullMutex::unlock
// ----------------------------------------------------------------------------
YAT_INLINE void NullMutex::unlock (void)
{
 //- noop
}

// ----------------------------------------------------------------------------
// NullMutex::release
// ----------------------------------------------------------------------------
YAT_INLINE void NullMutex::release (void)
{
 //- noop
}

// ----------------------------------------------------------------------------
// NullMutex::try_lock
// ----------------------------------------------------------------------------
YAT_INLINE MutexState NullMutex::try_lock (void)
{
  return yat::MUTEX_LOCKED;
}

// ----------------------------------------------------------------------------
// NullMutex::try_acquire
// ----------------------------------------------------------------------------
YAT_INLINE MutexState NullMutex::try_acquire (void)
{
  return yat::MUTEX_LOCKED;
}

// ****************************************************************************
// YAT MUTEX IMPL
// ****************************************************************************
// ----------------------------------------------------------------------------
// Mutex::lock
// ----------------------------------------------------------------------------
YAT_INLINE void Mutex::lock (void)
{
  ::pthread_mutex_lock(&m_posix_mux);
}
// ----------------------------------------------------------------------------
// Mutex::acquire
// ----------------------------------------------------------------------------
YAT_INLINE void Mutex::acquire (void)
{
  this->lock();
}

// ----------------------------------------------------------------------------
// Mutex::try_acquire
// ----------------------------------------------------------------------------
YAT_INLINE MutexState Mutex::try_acquire (void)
{
  return this->try_lock();
}

// ----------------------------------------------------------------------------
// Mutex::unlock
// ----------------------------------------------------------------------------
YAT_INLINE void Mutex::unlock (void)
{
  ::pthread_mutex_unlock(&m_posix_mux);
}

// ----------------------------------------------------------------------------
// Mutex::acquire
// ----------------------------------------------------------------------------
YAT_INLINE void Mutex::release (void)
{
  this->unlock();
}

// ----------------------------------------------------------------------------
// Mutex::try_lock
// ----------------------------------------------------------------------------
YAT_INLINE MutexState Mutex::try_lock (void)
{
  MutexState result = MUTEX_LOCKED;

  if (::pthread_mutex_trylock (&m_posix_mux) != 0)
    result = MUTEX_BUSY;

  return result;
}

} // namespace yat