/*!
 * \file
 * \brief    
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
 */

#ifndef _WIN_NT_THREADING_IMPL_
#define _WIN_NT_THREADING_IMPL_

// ----------------------------------------------------------------------------
// SOME PLATEFORM SPECIFIC CONSTs
// ----------------------------------------------------------------------------
#define WIN_NT_NULL NULL

// ----------------------------------------------------------------------------
// YAT MUTEX - YAT MUTEX - YAT MUTEX - YAT MUTEX - YAT MUTEX - YAT MUTEX - YAT
// ----------------------------------------------------------------------------
#define YAT_MUTEX_IMPLEMENTATION \
  HANDLE m_nt_mux; \
  friend class Condition;

// ----------------------------------------------------------------------------
// YAT SEMAPHORE - YAT SEMAPHORE - YAT SEMAPHORE - YAT SEMAPHORE - YAT SEMAPHO
// ----------------------------------------------------------------------------
#define YAT_SEMAPHORE_IMPLEMENTATION \
  HANDLE m_nt_sem;

// ----------------------------------------------------------------------------
// YAT CONDITION - YAT CONDITION - YAT CONDITION - YAT CONDITION - YAT CONDITI
// ----------------------------------------------------------------------------
#define YAT_CONDITION_IMPLEMENTATION \
  int m_waiters_count; \
  CRITICAL_SECTION m_waiters_count_lock; \
  HANDLE m_nt_sem; \
  HANDLE m_waiters_done; \
  bool m_was_broadcast;

// ----------------------------------------------------------------------------
// YAT THREAD - YAT THREAD - YAT THREAD - YAT THREAD - YAT THREAD - YAT THREAD
// ----------------------------------------------------------------------------
//- YAT common thread entry point (non-OO OS interface to YAT interface)
#define YAT_THREAD_COMMON_ENTRY_POINT \
  unsigned __stdcall yat_thread_common_entry_point (void *)

extern "C" YAT_THREAD_COMMON_ENTRY_POINT;

#define YAT_THREAD_IMPLEMENTATION \
  HANDLE m_nt_thread_handle; \
  void spawn (void); \
  static int yat_to_nt_priority (Priority); \
  friend YAT_THREAD_COMMON_ENTRY_POINT;

#endif  // _WIN_NT_THREADING_IMPL_
