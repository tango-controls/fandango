/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_COMMON_H_
#define _YAT_COMMON_H_

#if (defined (_DEBUG) || defined (DEBUG))
# define YAT_DEBUG
# include <assert.h>
#endif

#include <yat/Portability.h>
#include <yat/Inline.h>
#include <yat/LogHelper.h>
#include <yat/Timer.h>
#include <yat/Exception.h>

namespace yat 
{

// ============================================================================
// CONSTs
// ============================================================================
#define kDEFAULT_MSG_TMO_MSECS 2000

//-----------------------------------------------------------------------------
// MACROS
//-----------------------------------------------------------------------------
#define SAFE_DELETE_PTR(P) if (P) { delete P; P = 0; }
//-----------------------------------------------------------------------------
#define SAFE_DELETE_ARRAY(P) if (P) { delete[] P; P = 0; }
//-----------------------------------------------------------------------------
#define SAFE_RELEASE(P) if (P) { P->release(); P = 0; }
//-----------------------------------------------------------------------------
#define _CPTC(X) static_cast<const char*>(X)

//-----------------------------------------------------------------------------
// ASSERTION
//-----------------------------------------------------------------------------
#if defined (YAT_DEBUG)
# define DEBUG_ASSERT(EXP) assert(EXP)
#else
# define DEBUG_ASSERT(EXP)
#endif

}

#endif
