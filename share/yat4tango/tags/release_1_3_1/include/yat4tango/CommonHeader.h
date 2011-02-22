/*!
 * \file
 * \brief    Common definition included in all YAT files
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
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

#include <tango.h>

#ifdef WIN32
#pragma warning( pop )
#endif

#include <yat/CommonHeader.h>
#include <yat4tango/Export.h>

#endif
