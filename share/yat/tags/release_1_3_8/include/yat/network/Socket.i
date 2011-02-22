/*!
 * \file    Socket.i
 * \brief   Inlined code of the YAT network socket class.
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

namespace yat
{

// ----------------------------------------------------------------------------
// Socket::operator>>
// ----------------------------------------------------------------------------
YAT_INLINE size_t Socket::operator>> (Socket::Data & ib)
    //- throw (SocketException)
{
  return this->receive(ib);
}

// ----------------------------------------------------------------------------
// Socket::operator>>
// ----------------------------------------------------------------------------
YAT_INLINE size_t Socket::operator>> (std::string & data_str)
    //- throw (SocketException)
{
  return this->receive(data_str);
}

// ----------------------------------------------------------------------------
// Socket::send
// ---------------------------------------------------------------------------- 
YAT_INLINE void Socket::operator<< (const Socket::Data & ob)
  //- throw (SocketException) 
{
  this->send(ob);
}

// ----------------------------------------------------------------------------
// Socket::send
// ---------------------------------------------------------------------------- 
YAT_INLINE void Socket::operator<< (const std::string& os)
  //- throw (SocketException)
{
  this->send(os);
}

} // namespace
