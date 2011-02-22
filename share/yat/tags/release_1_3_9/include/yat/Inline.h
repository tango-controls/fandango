/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_INLINE_H_
#define _YAT_INLINE_H_

#include <yat/CommonHeader.h>

#if !defined(YAT_DEBUG)
# define YAT_INLINE_IMPL
#endif

#if defined(YAT_INLINE_IMPL)
# define YAT_INLINE inline
#else
# define YAT_INLINE
#endif

#endif // __INLINE_H_
