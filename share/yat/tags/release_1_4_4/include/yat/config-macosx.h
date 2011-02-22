/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_CONFIG_MACOSX_H_
#define _YAT_CONFIG_MACOSX_H_

#define YAT_MACOSX

/**
 *  Shared library related stuffs
 */
#define YAT_DECL_EXPORT
#define YAT_DECL_IMPORT
#define YAT_DECL

/**
 *  pthread related stuffs
 */
#define YAT_HAS_PTHREAD_YIELD 0

/**
 *  <sstream> library related stuffs
 */
#undef YAT_HAS_SSTREAM
#if __GNUC__ >= 3
# if __GNUC__ == 3
#   if __GNUC_MINOR__ >= 2
#     define YAT_HAS_SSTREAM
#   endif
# else
#   define YAT_HAS_SSTREAM
# endif
#endif

/**
 *  Endianness related stuff
 */
#if defined(i386)  || defined(__i386__) || defined(x86_64)  || defined(__x86_64__) 
#  define YAT_HAS_PENTIUM 1
#  define YAT_LITTLE_ENDIAN_PLATFORM 1
#else
#  error "no support for this processor"
#endif

# if !defined(__GNUC__) && !defined(__GNUG__)
#  error "no support for this compiler - GCC compiler required"
# else
#  define YAT_HAS_STATIC_OBJ_MANAGER 0
# endif 

#endif
