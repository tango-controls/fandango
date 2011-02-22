/*!
 * \file    ClientSocket.cpp
 * \brief   YAT portable Address implementation
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat/network/ClientSocket.h>

#if !defined (YAT_INLINE_IMPL)
# include <yat/network/ClientSocket.i>
#endif // YAT_INLINE_IMPL


namespace yat {

// ----------------------------------------------------------------------------
// ClientSocket::ClientSocket
// ----------------------------------------------------------------------------
ClientSocket::ClientSocket (Socket::Protocol _p) 
  : Socket(_p)
{
  YAT_TRACE("ClientSocket::ClientSocket");
}

// ----------------------------------------------------------------------------
// ClientSocket::~ClientSocket
// ----------------------------------------------------------------------------
ClientSocket::~ClientSocket ()
{
  YAT_TRACE("ClientSocket::~ClientSocket");

  this->close();
}

// ----------------------------------------------------------------------------
// ClientSocket::bind
// ----------------------------------------------------------------------------
void ClientSocket::bind (size_t _p)
    throw (SocketException)
{
  YAT_TRACE("ClientSocket::bind");

  this->Socket::bind(_p);
}

// ----------------------------------------------------------------------------
// ClientSocket::connect
// ----------------------------------------------------------------------------
void ClientSocket::connect (const Address & _addr)
    throw (SocketException)
{
  YAT_TRACE("ClientSocket::connect");

  this->Socket::connect(_addr);
}

// ----------------------------------------------------------------------------
// ClientSocket::disconnect
// ----------------------------------------------------------------------------
void ClientSocket::disconnect ()
    throw (SocketException)
{
  YAT_TRACE("ClientSocket::disconnect");

  this->close();
}

// ----------------------------------------------------------------------------
// ClientSocket::can_read_without_blocking
// ----------------------------------------------------------------------------
bool ClientSocket::can_read_without_blocking ()
    throw (SocketException)
{
  YAT_TRACE("ClientSocket::can_read_without_blocking");

  return this->select(0);
}

// ----------------------------------------------------------------------------
// ClientSocket::wait_input_data
// ----------------------------------------------------------------------------
bool ClientSocket::wait_input_data (size_t _tmo, bool _throw)
    throw (SocketException)
{
  YAT_TRACE("ClientSocket::wait_input_data");
 
  if (! this->select(_tmo))
  {
    if (! _throw)
      return false;

    throw yat::SocketException("SOCKET_ERROR", 
                               SocketException::get_error_text(SoErr_TimeOut), 
                               "ClientSocket::wait_input_data", 
                               SocketException::yat_to_native_error(SoErr_TimeOut)); 
  } 
  
  return true;
}


} //- namespace yat

