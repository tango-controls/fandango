//----------------------------------------------------------------------------
// YAT LIBRARY
//----------------------------------------------------------------------------
//
// Copyright (C) 2006-2009  The Tango Community
//
// Part of the code comes from the ACE Framework
// see http://www.cs.wustl.edu/~schmidt/ACE.html for more about ACE
//
// The thread native implementation has been initially inspired by omniThread
// - the threading support library that comes with omniORB. 
// see http://omniorb.sourceforge.net/ for more about omniORB.
//
// Contributors form the TANGO community:
// Ramon Sunes (ALBA) 
//
// The YAT library is free software; you can redistribute it and/or modify it 
// under the terms of the GNU General Public License as published by the Free 
// Software Foundation; either version 2 of the License, or (at your option) 
// any later version.
//
// The YAT library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
// Public License for more details.
//
// A copy of the GPL version 2 is available below. 
//
// Contact:
//      Nicolas Leclercq
//      Synchrotron SOLEIL
//------------------------------------------------------------------------------
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
