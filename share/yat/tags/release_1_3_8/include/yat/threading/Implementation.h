/*!
 * \file    Implementation.h
 * \brief   Platform specific code selection for threading impl.
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_THREADING_IMPL_H_
#define _YAT_THREADING_IMPL_H_

// ----------------------------------------------------------------------------
// Include the platform specific header file
// ----------------------------------------------------------------------------
#include <yat/CommonHeader.h>
#if defined (YAT_WIN32)
# include <yat/threading/impl/WinNtThreadingImpl.h>
#else
# include <yat/threading/impl/PosixThreadingImpl.h>
#endif

// ----------------------------------------------------------------------------
// MISC DEFINEs
// ----------------------------------------------------------------------------
#define kINFINITE_WAIT  0
#define DUMP_THREAD_UID std::hex << yat::ThreadingUtilities::self() << std::dec 

#endif //- _YAT_THREADING_IMPL_H_
