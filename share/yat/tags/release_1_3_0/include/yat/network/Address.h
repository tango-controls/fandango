/*!
 * \file    Address.h
 * \brief   Header file of the YAT network address class.
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_ADDRESS_H_
#define _YAT_ADDRESS_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <string>
#include <yat/CommonHeader.h>

namespace yat { 
	
// ----------------------------------------------------------------------------
//! The YAT Address class
// ----------------------------------------------------------------------------
class YAT_DECL Address
{
  //! This is the yat network Address class.

public:
  //! Construct a peer address.
  //!
  //! \param host The host name or IP address.
  //! \param port The associated port number.
  //!
  //! \remarks May throw an exception
  Address (const std::string& host, size_t port);

  //! Construct a peer address by copy.
  //!
  //! \param addr The address to be cloned.
  //!
  //! \remarks May throw an exception
  Address (const Address& addr);

  //! Copy a peer address.
  //!
  //! \param addr The address to be copied.
  Address & operator= (const Address& addr);

  //! Destructor. 
  virtual ~Address(void);
  
  //! Return host name.
  const std::string& get_host_name (void) const;

  //! Return IP address.
  const std::string& get_ip_address (void) const;

  //! Return port number.
  size_t get_port_number (void) const;
			
protected:
  //! Resolve host name <-> ip_address.
  //!
  //! \remarks May throw an exception
  void ns_lookup (const std::string& host)
	  throw (Exception);

  //! port number.
  size_t m_port;
  //! IP address.
  std::string m_ip_addr;
  //! host name.
  std::string m_host_name;
};

} // namespace yat 

#if defined (YAT_INLINE_IMPL)
# include <yat/network/Address.i>
#endif

#endif //- _YAT_ADDRESS_H_

