/*!
 * \file
 * \brief    
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
 */

namespace yat {

// ----------------------------------------------------------------------------
// Condition::wait
// ----------------------------------------------------------------------------
YAT_INLINE void Condition::wait (void)
{
  this->timed_wait(0);
}

} // namespace yat
