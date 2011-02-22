/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_SOCK_EX_H_
#define _YAT_SOCK_EX_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat/Exception.h>

namespace yat 
{

// ============================================================================
//! Socket error code
// ============================================================================
//!  
//! detailed description to be written
//!
// ============================================================================
enum SocketError 
{
  //- No error
  SoErr_NoError, 
  //- The receive buffer pointer(s) point outside the processes address space
  SoErr_BadMemAddress,
  //- Address is already in use (bind & connect).
  SoErr_AddressInUse, 
  //- Address not available on machine (bind & connect).
  SoErr_AddressNotAvailable, 
  //- Invalid socket descriptor (socket).
  SoErr_BadDescriptor, 
  //- Message signature is invalid.
  SoErr_BadMessage,
  //- Connection was closed (or broken) by other party.
  SoErr_ConnectionClosed, 
  //- Connection refused by server.
  SoErr_ConnectionRefused, 
  //- Datagram too long to send atomically.
  SoErr_DatagramTooLong, 
  //- Invalid option for socket protocol.
  SoErr_InvalidOption, 
  //- %Socket is already connected.
  SoErr_IsConnected, 
  //- %Socket is not connected.
  SoErr_NotConnected,
  //- Operation is not supported for this socket.
  SoErr_OpNotSupported, 
  //- User does not have acces to privileged ports (bind).
  SoErr_PrivilegedPort, 
  //- Time out was reached for operation (receive & send).
  SoErr_TimeOut, 
  //- Current operation is blocking (non-blocking socket)
  SoErr_WouldBlock,
  //- Op. in progress 
  SoErr_InProgress,
  //- Op. interrupted by OS event (signal) 
  SoErr_OSInterrupt,
  //- Memory allocation failed.
  SoErr_OutOfMemory, 
  //- Any other OS specific error.
  SoErr_Other
};

// ============================================================================
//! The SocketException class
// ============================================================================
//!  
//! detailed description to be written
//!
// ============================================================================
class YAT_DECL SocketException : public Exception
{
public:
  //! Ctor
  SocketException ( const char *reason,
                    const char *desc,
                    const char *origin,
                    int err_code = -1,
                    int severity = yat::ERR);
  //! Ctor
  SocketException ( const std::string& reason,
                    const std::string& desc,
                    const std::string& origin, 
                    int err_code = -1, 
                    int severity = yat::ERR);
  //! Dtor
  virtual ~SocketException (void);
  
  //! Returns the YAT error code
  int code (void) const;
  
  //! Returns true if <_code> equals the exception error code, returns false otherwise.
  bool is_a (int _code) const;

  //! Returns the error text.
  std::string text (void) const;
  
  //! Dump.
  virtual void dump (void) const;
    
  //! Given a yat SocketError code, return its associated text 
  static std::string get_error_text (int _yat_err_code);

  //! Convert from native to YAT SocketError code
  static SocketError native_to_yat_error (int _os_err_code);
  
  //! Convert from YAT to native SocketError code
  static int yat_to_native_error (SocketError _yat_err_code);
  
private:
  //! The native (i.e. platform specific error code)
  int m_yat_err_code;
};

} // namespace

#endif //- _YAT_SOCK_EX_H_
