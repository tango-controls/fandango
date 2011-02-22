//----------------------------------------------------------------------------
// YAT4Tango LIBRARY
//----------------------------------------------------------------------------
//
// Copyright (C) 2006-2010  The Tango Community
//
// The YAT4Tango library is free software; you can redistribute it and/or 
// modify it under the terms of the GNU General Public License as published 
// by the Free Software Foundation; either version 2 of the License, or (at 
// your option) any later version.
//
// The YAT4Tango library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
// Public License for more details.
//
// See COPYING file for license details  
//
// Contact:
//      Nicolas Leclercq
//      Synchrotron SOLEIL
//------------------------------------------------------------------------------
/*!
 * \authors N.Leclercq, J.Malik - Synchrotron SOLEIL
 */

#ifndef _YAT4TANGO_LOGHELPER_H_
#define _YAT4TANGO_LOGHELPER_H_

// ============================================================================
// WIN32 SPECIFIC
// ============================================================================
#if defined (WIN32)
# pragma warning(disable:4786)
#endif

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include "yat4tango/CommonHeader.h"

namespace yat4tango
{

class YAT4TANGO_DECL TangoLogAdapter
{
  
public:

  TangoLogAdapter (Tango::DeviceImpl * _host)
    : logger_ (0)
  {
    this->host(_host);
  }

  virtual ~TangoLogAdapter () 
  {
    //- noop dtor
  } ;

  inline log4tango::Logger * get_logger () 
  {
    return logger_;
  }

  inline void host (Tango::DeviceImpl * _host) 
  {
    if (_host)
      logger_ = _host->get_logger();
    else
      logger_ = 0;
  }

private:
  log4tango::Logger* logger_;
};

} //- namespace yat4tango 

#endif //- _YAT4TANGO_LOGHELPER_H_
