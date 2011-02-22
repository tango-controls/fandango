//----------------------------------------------------------------------------
// YAT4Tango LIBRARY
//----------------------------------------------------------------------------
//
// Copyright (C) 2006-2010  The Tango Community
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
// See COPYING file for license details  
//
// Contact:
//      Nicolas Leclercq
//      Synchrotron SOLEIL
//------------------------------------------------------------------------------
/*!
 * \authors N.Leclercq, J.Malik - Synchrotron SOLEIL
 */

#ifndef _YAT4TANGO_EXPORT_H_
#define _YAT4TANGO_EXPORT_H_

#include <yat/CommonHeader.h>

/* 
 * Use the YAT macros to define the export/import symbols
 *
 * This means YAT and YAT4TANGO are supposed to be built the same way :
 * - either YAT and YAT4TANGO both as shared libraries
 * - either YAT and YAT4TANGO both as static libraries
 */ 

#   if defined (YAT4TANGO_BUILD)
#     define YAT4TANGO_DECL YAT_DECL_EXPORT
#   else
#     define YAT4TANGO_DECL YAT_DECL_IMPORT
#   endif

#endif
