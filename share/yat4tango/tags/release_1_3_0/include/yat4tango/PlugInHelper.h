/*!
 * \file
 * \brief    
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
 */

#ifndef _YAT4TANGO_PLUGIN_HELPER_H_
#define _YAT4TANGO_PLUGIN_HELPER_H_

#include <yat4tango/CommonHeader.h>
#include <yat4tango/DynamicAttrHelper.h>
#include <yat/plugin/IPlugInObjectWithAttr.h>

namespace yat4tango
{

  class YAT4TANGO_DECL PlugInHelper
  {
  public:
    PlugInHelper(Tango::DeviceImpl * _host_device);
    
    ~PlugInHelper();

    /**
     * Enumerate then send properties to the object,
     * Register the dynamic attributes associated to it
     */
    void register_plugin( yat::IPlugInObjectWithAttr* object );

  private:
    void register_properties( yat::IPlugInObjectWithAttr* object );

    void register_attributes( yat::IPlugInObjectWithAttr* object );

    Tango::DeviceImpl* host_device_;
    DynamicAttrHelper  dyn_attr_h_;
  };



} // namespace

//=============================================================================
// INLINED CODE
//=============================================================================
#if defined (YAT_INLINE_IMPL)
# include "yat4tango/PlugInHelper.i"
#endif // __INLINE_IMPL__

#endif
