//----------------------------------------------------------------------------
// YAT4Tango LIBRARY
//----------------------------------------------------------------------------
//
// Copyright (C) 2006-2009  The Tango Community
//
// The YAT4Tango library is free software; you can redistribute it and/or 
// modify it under the terms of the GNU General Public License as published 
// by the Free Software Foundation; either version 2 of the License, or (at 
// your option) any later version.
//
// The YAT4Tango library is distributed in the hope that it will be useful,
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
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT4TANGO_COMMON_H_
#define _YAT4TANGO_COMMON_H_


// ============================================================================
// DEPENDENCIES
// ============================================================================
#ifdef WIN32
#pragma warning( push )
#pragma warning( disable: 4786 ) // 
#pragma warning( disable: 4267 ) // 'var' : conversion from 'size_t' to 'type', possible loss of data 
#pragma warning( disable: 4311 ) // 'variable' : pointer truncation from 'type' to 'type' 
#pragma warning( disable: 4312 ) // 'operation' : conversion from 'type1' to 'type2' of greater size 
#endif

#ifdef WIN32
#pragma warning( pop )
#endif

#include <yat/CommonHeader.h>
#include <yat4tango/Export.h>

#include <tango.h>

#endif
