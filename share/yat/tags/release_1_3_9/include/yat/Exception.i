/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

namespace yat 
{

// ============================================================================
// Exception::error_list
// ============================================================================
YAT_INLINE
const ErrorList &  Exception::error_list () const
{
  return this->errors;
}

} // namespace


