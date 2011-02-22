/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
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

  inline log4tango::Logger * get_logger (void) 
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
