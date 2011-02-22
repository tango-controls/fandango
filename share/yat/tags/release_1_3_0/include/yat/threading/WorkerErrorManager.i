/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

namespace yat
{

YAT_INLINE
bool
WorkerErrorManager::has_error() const
{
  return( this->has_error_ );
}

YAT_INLINE
const WorkerError&
WorkerErrorManager::get_error() const
{
  return( this->last_error_ );
}

} //- namespace
