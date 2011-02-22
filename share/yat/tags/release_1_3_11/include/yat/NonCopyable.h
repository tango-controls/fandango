/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_NONCOPYABLE_H_
#define _YAT_NONCOPYABLE_H_

//=============================================================================
// DEPENDENCIES
//=============================================================================
#include <yat/CommonHeader.h>

namespace yat 
{

// ============================================================================
// NonCopiable class
// ============================================================================
class NonCopyable
{
protected:
  NonCopyable () {}
 ~NonCopyable () {}
private:
  NonCopyable ( const NonCopyable& );
  const NonCopyable& operator= ( const NonCopyable& );
};
  
} //- namespace

#endif // _YAT_NONCOPYABLE_H_
