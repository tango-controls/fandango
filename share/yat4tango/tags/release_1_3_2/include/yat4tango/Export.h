/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
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
