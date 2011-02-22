/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

//=============================================================================
// DEPENDENCIES
//=============================================================================
#include <yat4tango/ThreadSafeDeviceProxy.h>

#if ! defined (YAT_INLINE_IMPL)
#  include "yat4tango/ThreadSafeDeviceProxy.i"
#endif

namespace yat4tango
{

//=============================================================================
// ThreadSafeDeviceProxy::ThreadSafeDeviceProxy 
//=============================================================================
ThreadSafeDeviceProxy::ThreadSafeDeviceProxy (const std::string& dev_name)
    throw (Tango::DevFailed)
 : dp_(const_cast<std::string&>(dev_name))  
{
  //- noop ctor
}

//=============================================================================
// ThreadSafeDeviceProxy::ThreadSafeDeviceProxy 
//=============================================================================
ThreadSafeDeviceProxy::ThreadSafeDeviceProxy (const char * dev_name)
    throw (Tango::DevFailed)
 : dp_(dev_name)  
{
  //- noop ctor
}

//=============================================================================
// ThreadSafeDeviceProxy::~ThreadSafeDeviceProxy 
//=============================================================================
ThreadSafeDeviceProxy::~ThreadSafeDeviceProxy (void)
{
  //- noop dtor
}

} // namespace
