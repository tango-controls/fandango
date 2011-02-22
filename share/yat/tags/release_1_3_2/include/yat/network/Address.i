/*!
 * \file    Address.i
 * \brief   Inlined code of the YAT network address class.
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

namespace yat
{

// ============================================================================
// Address::get_host_name
// ============================================================================
YAT_INLINE const std::string & Address::get_host_name (void) const
{
  YAT_TRACE("Address::get_host_name");

  return this->m_host_name;
} 

// ============================================================================
// Address::get_ip_address
// ============================================================================
YAT_INLINE const std::string & Address::get_ip_address (void) const
{
  YAT_TRACE("Address::get_ip_address");

  return this->m_ip_addr;
} 

// ============================================================================
// Address::get_port_number
// ============================================================================
YAT_INLINE size_t Address::get_port_number (void) const
{
  YAT_TRACE("Address::get_port_number");

  return this->m_port;
} 

} // namespace
