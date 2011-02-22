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

#ifndef _DYNAMIC_ATTR_H_
#define _DYNAMIC_ATTR_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <limits>
#include <yat4tango/CommonHeader.h>
#include <yat/memory/DataBuffer.h>

namespace yat4tango
{


// ============================================================================
//
// static class: DynamicAttr
//
// ============================================================================
template <typename T>
class YAT_DECL DynamicAttr
{
public:
  /**
   * the Tango identifier of the data type (DEV_BOOLEAN, DEV_DOUBLE...)
   */
  static const long tango_type;

  /**
   * a dummy value of the type used to fill the attribute value at construction
   */
  static const T    dummy_value;
};

// ============================================================================
//
// class: DynamicScalarAttr
//
// ============================================================================
template <typename T>
class YAT_DECL DynamicScalarAttr : public Tango::Attr
{
public:
	//- ctor ---------------------------------
	DynamicScalarAttr (const std::string& _name,
                     Tango::AttrWriteType _w_type);

	//- dtor ---------------------------------
	virtual ~DynamicScalarAttr ();

  //- read ---------------------------------
	virtual void read(Tango::DeviceImpl *dev, Tango::Attribute &att);

  //- write --------------------------------
	virtual void write(Tango::DeviceImpl *dev, Tango::WAttribute &att);

  //- is_allowed ---------------------------
  virtual bool is_allowed (Tango::DeviceImpl *dev, Tango::AttReqType ty);

  T content;
  T w_content;
  bool allowed;
};

// ============================================================================
//
// class: DynamicSpectrumAttr
//
// ============================================================================
template <typename T>
class YAT_DECL DynamicSpectrumAttr : public Tango::SpectrumAttr
{
public:
	//- ctor ---------------------------------
	DynamicSpectrumAttr (const std::string& _name,
                       Tango::AttrWriteType _w_type,
                       long max_x);

	//- dtor ---------------------------------
	virtual ~DynamicSpectrumAttr ();

  //- read ---------------------------------
	virtual void read(Tango::DeviceImpl *dev, Tango::Attribute &att);

  //- write --------------------------------
	virtual void write(Tango::DeviceImpl *dev, Tango::WAttribute &att);

  //- is_allowed ---------------------------
  virtual bool is_allowed (Tango::DeviceImpl *dev, Tango::AttReqType ty);


  yat::Buffer<T> content;
  yat::Buffer<T> w_content;
  bool allowed;
};


// ============================================================================
//
// class: DynamicImageAttr
//
// ============================================================================
template <typename T>
class YAT_DECL DynamicImageAttr : public Tango::ImageAttr
{
public:
	//- ctor ---------------------------------
	DynamicImageAttr (const std::string& _name,
                    Tango::AttrWriteType _w_type,
                    long max_x,
                    long max_y);

	//- dtor ---------------------------------
	virtual ~DynamicImageAttr ();

  //- read ---------------------------------
	virtual void read(Tango::DeviceImpl *dev, Tango::Attribute &att);

  //- write --------------------------------
	virtual void write(Tango::DeviceImpl *dev, Tango::WAttribute &att);

  //- is_allowed ---------------------------
  virtual bool is_allowed (Tango::DeviceImpl *dev, Tango::AttReqType ty);


  yat::ImageBuffer<T> content;
  yat::ImageBuffer<T> w_content;
  bool allowed;
};

} // namespace

#include <yat4tango/DynamicAttr.tpp>

#endif
