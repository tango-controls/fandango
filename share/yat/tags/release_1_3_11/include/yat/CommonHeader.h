/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_COMMON_H_
#define _YAT_COMMON_H_

// ============================================================================
// IMPL OPTION - THIS ENABLES/DISABLES THE CACHE ON THE MESSAGE CLASS 
// ============================================================================
// DEFINE THE FOLLOWING IS YOU WANT TO TEST THE CACHED ALLOCATOR ON THE MESSAGE 
// CLASS. FIRST TESTS SHOW THAT THE GAIN IS NOT SIGNIFICANT ENOUGH FOR THE CACHE
// TO BE USED. MOREOVER, THE CACHED ALLOCATOR USAGE IS QUITE TRICKY SINCE NEW AND 
// DELETE OPERATORS MUST BE OVERLOADED FOR THE CLASS TO BE "CACHABLE" (SEE WHAT 
// HAS BEEN DONE IN THE YAT MESSAGE TASK). ANYWAY WE NOW HAVE A CACHED-ALL0CATOR 
// IN YAT! 
// ============================================================================
// #define _USE_MSG_CACHE_

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
#define SAFE_DELETE_PTR(P) if (P) { delete P; P = 0; } else (void)0
//-----------------------------------------------------------------------------
#define SAFE_DELETE_ARRAY(P) if (P) { delete[] P; P = 0; } else (void)0
//-----------------------------------------------------------------------------
#define SAFE_RELEASE(P) if (P) { P->release(); P = 0; } else (void)0
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
