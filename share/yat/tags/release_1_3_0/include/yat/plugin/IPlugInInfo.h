/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_IPLUGININFO_H_
#define _YAT_IPLUGININFO_H_

#include <yat/NonCopyable.h>

namespace yat
{

  class YAT_DECL IPlugInInfo : private yat::NonCopyable
  {
  public:
    virtual ~IPlugInInfo();

    virtual std::string get_plugin_id (void) const = 0;

    virtual std::string get_interface_name (void) const = 0;

    virtual std::string get_version_number (void) const = 0;
    
  protected:
    IPlugInInfo();
  };

} // namespace

#endif
