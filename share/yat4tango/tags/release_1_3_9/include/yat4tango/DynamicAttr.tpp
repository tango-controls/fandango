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
// A copy of the GPL version 2 is available below. 
//
// Contact:
//      Nicolas Leclercq
//      Synchrotron SOLEIL
//------------------------------------------------------------------------------

/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

// ============================================================================
// DEPENDENCIES
// ============================================================================
#ifndef _DYNAMIC_ATTR_TPP_
#define _DYNAMIC_ATTR_TPP_

#include "DynamicAttr.h"

namespace yat4tango
{
  // ======================================================================
  // DynamicScalarAttr::DynamicScalarAttr
  // ======================================================================
  template <typename T>
  DynamicScalarAttr<T>::DynamicScalarAttr (const std::string& _name,
    Tango::AttrWriteType _w_type)
    : Tango::Attr (_name.c_str() ,
    DynamicAttr<T>::tango_type,
    _w_type),
    content(DynamicAttr<T>::dummy_value),
    w_content(DynamicAttr<T>::dummy_value),
    allowed(true)
  {
    //- DEBUG_TRACE("DynamicScalarAttr::DynamicScalarAttr");
    YAT_LOG(" creating attribute : " << this->get_name());
  }

  // ======================================================================
  // DynamicScalarAttr::~DynamicScalarAttr
  // ======================================================================
  template <typename T>
  DynamicScalarAttr<T>::~DynamicScalarAttr (void)
  {
    //- DEBUG_TRACE("DynamicScalarAttr::~DynamicScalarAttr");
    YAT_LOG(" deleting attribute : " << this->get_name());
  }


  // ============================================================================
  // DynamicScalarAttr::read
  // ============================================================================
  template <typename T>
  void DynamicScalarAttr<T>::read (Tango::DeviceImpl *, Tango::Attribute &att)
  {
    //- DEBUG_TRACE("DynamicScalarAttr::read");

    YAT_LOG("reading attribute : " << this->get_name() << " : " << this->content);
    att.set_value(&this->content);
  }

  // ============================================================================
  // DynamicScalarAttr::write
  // ============================================================================
  template <typename T>
  void DynamicScalarAttr<T>::write (Tango::DeviceImpl *, Tango::WAttribute &att)
  {
    //- DEBUG_TRACE("DynamicScalarAttr::write");
    T write_value;    
    att.get_write_value(write_value);
    this->w_content = write_value;
  }

  // ============================================================================
  // DynamicScalarAttr::is_allowed
  // ============================================================================
  template <typename T>
  bool DynamicScalarAttr<T>::is_allowed (Tango::DeviceImpl *, Tango::AttReqType)
  {
    return this->allowed;
  }





  // ============================================================================
  // DynamicSpectrumAttr::DynamicSpectrumAttr
  // ============================================================================
  template <typename T>
  DynamicSpectrumAttr<T>::DynamicSpectrumAttr (const std::string& _name,
    Tango::AttrWriteType _w_type,
    long max_x)
    : Tango::SpectrumAttr (_name.c_str() ,
    DynamicAttr<T>::tango_type,
    _w_type,
    max_x),
    content(1),
    w_content(0),
    allowed(true)
  {
    //- DEBUG_TRACE("DynamicSpectrumAttr::DynamicSpectrumAttr");
    YAT_LOG(" creating attribute : " << this->get_name());

    content[0] = DynamicAttr<T>::dummy_value;
  }

  // ============================================================================
  // DynamicSpectrumAttr::~DynamicSpectrumAttr
  // ============================================================================
  template <typename T>
  DynamicSpectrumAttr<T>::~DynamicSpectrumAttr()
  {
    //- DEBUG_TRACE("DynamicSpectrumAttr::~DynamicSpectrumAttr");
    YAT_LOG(" deleting attribute : " << this->get_name());
  }

  // ============================================================================
  // DynamicSpectrumAttr::read
  // ============================================================================
  template <typename T>
  void DynamicSpectrumAttr<T>::read (Tango::DeviceImpl *, Tango::Attribute &att)
  {
    //- DEBUG_TRACE("DynamicSpectrumAttr::read");
    YAT_LOG("reading attribute : " << this->get_name() << " : [ 0x" << std::hex << reinterpret_cast<long>(this->content.base()) << std::dec << " , " << this->content.length() << " ]");
    att.set_value(this->content.base(), this->content.length());
  }

  // ============================================================================
  // DynamicSpectrumAttr::write
  // ============================================================================
  template <typename T>
  void DynamicSpectrumAttr<T>::write (Tango::DeviceImpl *, Tango::WAttribute &att)
  {
    //- DEBUG_TRACE("DynamicSpectrumAttr::write");

    this->w_content.length( att.get_write_value_length() );

    const T* p = 0;
    att.get_write_value(p);
    this->w_content = p;

  }

  // ============================================================================
  // DynamicSpectrumAttr::is_allowed
  // ============================================================================
  template <typename T>
  bool DynamicSpectrumAttr<T>::is_allowed (Tango::DeviceImpl *, Tango::AttReqType)
  {
    return this->allowed;
  }

  // ============================================================================
  // DynamicImageAttr::DynamicImageAttr
  // ============================================================================
  template <typename T>
  DynamicImageAttr<T>::DynamicImageAttr (const std::string& _name,
    Tango::AttrWriteType _w_type,
    long max_x,
    long max_y)
    : Tango::ImageAttr (_name.c_str() ,
    DynamicAttr<T>::tango_type,
    _w_type,
    max_x,
    max_y),
    content(1,1),
    w_content(0,0),
    allowed(true)
  {
    //- DEBUG_TRACE("DynamicImageAttr::DynamicImageAttr");
    YAT_LOG(" creating attribute : " << this->get_name());
    this->content[0] = DynamicAttr<T>::dummy_value;
  }

  // ============================================================================
  // DynamicImageAttr::~DynamicImageAttr
  // ============================================================================
  template <typename T>
  DynamicImageAttr<T>::~DynamicImageAttr()
  {
    //- DEBUG_TRACE("DynamicImageAttr::~DynamicImageAttr");
    YAT_LOG(" deleting attribute : " << this->get_name());
  }

  // ============================================================================
  // DynamicImageAttr::read
  // ============================================================================
  template <typename T>
  void DynamicImageAttr<T>::read (Tango::DeviceImpl *, Tango::Attribute &att)
  {
    //- DEBUG_TRACE("DynamicImageAttr::read");
    YAT_LOG("reading attribute : " << this->get_name() << " : [ 0x" << std::hex << reinterpret_cast<long>(this->content.base()) << std::dec << " , " << this->content.width() << " , " << this->content.height() << " ]");
    att.set_value(this->content.base(), this->content.width(), this->content.height());
  }


  // ============================================================================
  // DynamicImageAttr::write
  // ============================================================================
  template <typename T>
  void DynamicImageAttr<T>::write (Tango::DeviceImpl *, Tango::WAttribute &att)
  {
    //- DEBUG_TRACE("DynamicImageAttr::write");

    this->w_content.set_dimensions(att.get_w_dim_x(), att.get_w_dim_y());

    const T* p = 0;
    att.get_write_value(p);
    this->w_content = p;

  }

  // ============================================================================
  // DynamicImageAttr::is_allowed
  // ============================================================================
  template <typename T>
  bool DynamicImageAttr<T>::is_allowed (Tango::DeviceImpl *, Tango::AttReqType)
  {
    return this->allowed;
  }


} // namespace



#endif
