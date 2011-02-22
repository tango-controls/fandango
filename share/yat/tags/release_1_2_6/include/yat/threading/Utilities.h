/*!
 * \file    Utilities.h
 * \brief   Header file of the YAT portable threading utilities.
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

// ----------------------------------------------------------------------------
// almost complete rewrite/extension of omniThread portable threading impl.
// see http://omniorb.sourceforge.net for more omniORB details
// ----------------------------------------------------------------------------

#ifndef _YAT_THREADING_UTILS_H_
#define _YAT_THREADING_UTILS_H_

// ----------------------------------------------------------------------------
// DEPENDENCIES
// ----------------------------------------------------------------------------
#include <yat/threading/Implementation.h>

// ----------------------------------------------------------------------------
// CONSTs
// ----------------------------------------------------------------------------
#define YAT_INVALID_THREAD_UID 0xffffffff

namespace yat {

// ----------------------------------------------------------------------------
//! A dedicated type for thread identifier
// ----------------------------------------------------------------------------
typedef unsigned long ThreadUID;

// ----------------------------------------------------------------------------
//! The YAT threading utilities
// ----------------------------------------------------------------------------
class YAT_DECL ThreadingUtilities
{
public:
 	//! Returns the calling thread identifier.
  static ThreadUID self (void);

	//! Causes the caller to sleep for the given time.
  static void sleep (unsigned long secs, unsigned long nanosecs = 0);

	//! Calculates an absolute time in seconds and nanoseconds, suitable for
	//! use in timed_waits, which is the current time plus the given relative 
  //! offset.
  static void get_time (unsigned long & abs_sec,
                        unsigned long & abs_nsec,
			                  unsigned long offset_sec = 0,
                        unsigned long offset_nsec = 0);

	//! Calculates an absolute time in seconds and nanoseconds, suitable for
	//! use in timed_waits, which is the current time plus the given relative 
  //! offset.
  static void get_time (Timespec & abs_time, unsigned long offset_msecs);

private:

#if defined (YAT_WIN32)
  //- internal impl
  static void ThreadingUtilities::get_time_now (unsigned long & abs_sec_, 
                                                unsigned long & abs_nano_sec_);
#endif  
};

} // namespace yat 

#endif //- _YAT_THREADING_UTILS_H_
