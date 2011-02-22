//----------------------------------------------------------------------------
// YAT4Tango LIBRARY
//----------------------------------------------------------------------------
//
// Copyright (C) 2006-2009  The Tango Community
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
