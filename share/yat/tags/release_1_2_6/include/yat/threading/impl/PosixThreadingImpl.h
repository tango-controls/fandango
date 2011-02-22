/*!
 * \file
 * \brief    
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
 */

#ifndef _POSIX_THREADING_IMPL_
#define _POSIX_THREADING_IMPL_

// ----------------------------------------------------------------------------
// YAT MUTEX - YAT MUTEX - YAT MUTEX - YAT MUTEX - YAT MUTEX - YAT MUTEX - YAT
// ----------------------------------------------------------------------------
#define YAT_MUTEX_IMPLEMENTATION \
  pthread_mutex_t m_posix_mux; \
  friend class Condition;

// ----------------------------------------------------------------------------
// YAT CONDITION - YAT CONDITION - YAT CONDITION - YAT CONDITION - YAT CONDITI
// ----------------------------------------------------------------------------
#define YAT_CONDITION_IMPLEMENTATION \
  pthread_cond_t m_posix_cond;

// ----------------------------------------------------------------------------
// YAT SEMAPHORE - YAT SEMAPHORE - YAT SEMAPHORE - YAT SEMAPHORE - YAT SEMAPHO
// ----------------------------------------------------------------------------
#define YAT_SEMAPHORE_IMPLEMENTATION \
  Mutex m_mux; \
  Condition m_cond; \
  int m_value;

// ----------------------------------------------------------------------------
// YAT THREAD - YAT THREAD - YAT THREAD - YAT THREAD - YAT THREAD - YAT THREAD
// ----------------------------------------------------------------------------
//- YAT common thread entry point (non-OO OS interface to YAT interface)
#define YAT_THREAD_COMMON_ENTRY_POINT \
  void * yat_thread_common_entry_point (void *)

extern "C" YAT_THREAD_COMMON_ENTRY_POINT;

#define YAT_THREAD_IMPLEMENTATION \
  pthread_t m_posix_thread; \
  void spawn (void) throw (Exception); \
  static int yat_to_posix_priority (Priority); \
  friend YAT_THREAD_COMMON_ENTRY_POINT;

#endif //- _POSIX_THREADING_IMPL_
