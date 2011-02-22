/*!
 * \file    Address.cpp
 * \brief   YAT portable Address implementation
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

// ============================================================================
// DEPENDENCIES
// ============================================================================
#if ! defined (WIN32)
#	include <sys/socket.h>
# include <netinet/in.h>
# include <arpa/inet.h> 
# include <netdb.h>
#elif defined (WIN32_LEAN_AND_MEAN)
# include <winsock2.h>  
#endif
#include <yat/network/Address.h>

#if !defined (YAT_INLINE_IMPL)
# include <yat/network/Address.i>
#endif // YAT_INLINE_IMPL

namespace yat {

// ----------------------------------------------------------------------------
// Address::Address
// ----------------------------------------------------------------------------
Address::Address (const std::string& _host, size_t _port)
 : m_port (_port), m_ip_addr(_host), m_host_name(_host) 
{
  YAT_TRACE("Address::Address");
}

// ----------------------------------------------------------------------------
// Address::~Address
// ----------------------------------------------------------------------------
Address::~Address ()
{
  YAT_TRACE("Address::~Address");
}

// ----------------------------------------------------------------------------
// Address::Address
// ----------------------------------------------------------------------------
Address::Address (const Address & _addr)
{
  YAT_TRACE("Address::Address");

  *this = _addr;
}

// ----------------------------------------------------------------------------
// Address::operator=
// ----------------------------------------------------------------------------
Address& Address::operator= (const Address & _addr)
{
  YAT_TRACE("Address::operator=");

  //- avoid self copy
  if (this == &_addr)
    return *this;

  //- deep copy
  this->m_port = _addr.m_port;
  this->m_ip_addr = _addr.m_ip_addr;
  this->m_host_name = _addr.m_host_name;

  //- return self
  return *this;
}

// ----------------------------------------------------------------------------
// Address::ns_lookup
// ----------------------------------------------------------------------------
void Address::ns_lookup (const std::string& _host_ipaddr_or_name)
	  //- throw (Exception)
{
  YAT_TRACE("Address::ns_lookup");

  //- is _host_ipaddr_or_name an IP address or a host name?
  unsigned int ip_addr = ::inet_addr(_host_ipaddr_or_name.c_str());

  //- in case it's an IP address
  if (ip_addr != INADDR_NONE)
  {
    //- store it into the local member
    this->m_ip_addr = _host_ipaddr_or_name;
    //- get associated host name
    struct hostent * host = 
	      ::gethostbyaddr((char*)&ip_addr, sizeof(ip_addr), AF_INET);
    //- if host as a valid hostname then store it localy
    if (host) 
	    this->m_host_name = host->h_name;
    else
	    this->m_host_name = _host_ipaddr_or_name;
  } 
  //- in case it's a host name
  else 
  {
	  //- store it into the local member
	  this->m_host_name = _host_ipaddr_or_name;
	  //- get associated ip address
	  struct hostent * host = ::gethostbyname(_host_ipaddr_or_name.c_str());
	  //- got a valid ip addr?
	  if (! host) 
    {
      yat::OSStream oss;
      oss << "could not resolve IP address for host "
          << _host_ipaddr_or_name 
          << std::endl;
		  THROW_YAT_ERROR("INVALID_HOST", oss.str().c_str(), "Address::ns_lookup");
    }
	  //- store it into the local member
	  this->m_ip_addr = ::inet_ntoa(*((struct in_addr*)host->h_addr));
  }
}

} //- namespace yat
