/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_CONFIG_WIN32_H_
#define _YAT_CONFIG_WIN32_H_


#define YAT_WIN32

/**
 *  Disable some annoying warnings
 */
//- 'identifier' : identifier was truncated to 'number' characters
#pragma warning(disable:4786) 
//- 'identifier' : class 'type' needs to have dll-interface to be used by clients of class 'type2' 
#pragma warning(disable:4251) 
//- non – DLL-interface classkey 'identifier' used as base for DLL-interface classkey 'identifier' 
#pragma warning(disable:4275) 
//- C++ exception specification ignored except to indicate a function is not __declspec(nothrow)
#pragma warning(disable:4290)
//- 'function': was declared deprecated
#pragma warning(disable:4996)
//- 'function': possible loss of data
#pragma warning(disable:4267)
//- 'function': forcing value to bool 'true' or 'false' (performance warning)
#pragma warning(disable:4800)

#ifndef _WIN32_WINNT
//- the following macro must be set sa as ::SignalObjectAndWait() to be defined
#define _WIN32_WINNT 0x400
#endif

#include <windows.h>

/**
 *  <sstream> library related stuffs
 */
#define YAT_HAS_SSTREAM

/**
 *  Shared library related stuffs
 */
# if defined(YAT_DLL)
#   define YAT_DECL_EXPORT __declspec(dllexport)
#   define YAT_DECL_IMPORT __declspec(dllimport)
#   if defined (YAT_BUILD)
#     define YAT_DECL YAT_DECL_EXPORT
#   else
#     define YAT_DECL YAT_DECL_IMPORT
#   endif
# else
#   define YAT_DECL_EXPORT
#   define YAT_DECL_IMPORT
#   define YAT_DECL
# endif

/**
 *  Endianness related stuffs
 */
# if (_M_IX86 > 400)
#  define YAT_HAS_PENTIUM 1
#  define YAT_LITTLE_ENDIAN_PLATFORM 1
# else
#  error "no support for this processor"
# endif

# if !defined(_MSC_VER)
#  error "no support for this WIN32 compiler - MSVC++ compiler required"
# elif (_MSC_VER < 1200)
#  error "microsoft visual C++ >= 6.0 required"
# else
#  define YAT_HAS_STATIC_OBJ_MANAGER 0
# endif

#endif
