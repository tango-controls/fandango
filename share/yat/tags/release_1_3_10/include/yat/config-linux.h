/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_CONFIG_LINUX_H_
#define _YAT_CONFIG_LINUX_H_

#define YAT_LINUX

/**
 *  Shared library related stuff
 */
#define YAT_DECL_EXPORT
#define YAT_DECL_IMPORT
#define YAT_DECL

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
 *  pthread related stuffs
 */
#define YAT_HAS_PTHREAD_YIELD 1

/**
 *  Endianness related stuffs
 */
# if defined(i386) || defined(__i386__) || defined(__amd64__)
#  define YAT_HAS_PENTIUM 1
#  define YAT_LITTLE_ENDIAN_PLATFORM 1
# else
#  error "no support for this processor"
# endif

# if !defined(__GNUG__)
#  error "no support for this compiler - GCC compiler required"
# else
#  define YAT_HAS_STATIC_OBJ_MANAGER 0
# endif 

#endif
