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

#ifndef _YAT4TANGO_PLUGINATTR_H_
#define _YAT4TANGO_PLUGINATTR_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat4tango/CommonHeader.h>
#include <yat4tango/ExceptionHelper.h>
#include <yat/plugin/PlugInTypes.h>

namespace yat4tango
{

#ifdef YAT_WIN32
#  pragma warning (push)
#  pragma warning (disable : 4275)
#endif


  template <class T>
  class PlugInAttr : public Tango::Attr
  {
  public:
    PlugInAttr(yat::PlugInAttrInfo info);

    virtual ~PlugInAttr(void);

  public:

    //- read ---------------------------------
	  virtual void read(Tango::DeviceImpl *dev, Tango::Attribute &att);

    //- write --------------------------------
	  virtual void write(Tango::DeviceImpl *dev, Tango::WAttribute &att);

    //- is_allowed ---------------------------
    virtual bool is_allowed (Tango::DeviceImpl *dev, Tango::AttReqType ty);

  private:
    yat::PlugInAttrInfo info_;
    yat::Any read_value;
  };


  template <>
  class PlugInAttr<std::string> : public Tango::Attr
  {
  public:
    PlugInAttr(yat::PlugInAttrInfo info);

    virtual ~PlugInAttr(void);

  public:

    //- read ---------------------------------
	  virtual void read(Tango::DeviceImpl *dev, Tango::Attribute &att);

    //- write --------------------------------
	  virtual void write(Tango::DeviceImpl *dev, Tango::WAttribute &att);

    //- is_allowed ---------------------------
    virtual bool is_allowed (Tango::DeviceImpl *dev, Tango::AttReqType ty);

  private:
    yat::PlugInAttrInfo info_;
    yat::Any read_value;
    char*    read_ptr;
  };


  /*
   * This class converts (at compile time !) a supported plugin type 
   * to its Tango equivalent descriptor
   */
  template <typename T>
  struct TangoType
  {
    enum { Value };
  };

# define MAP_TO_TANGO_TYPE( plugin_type, tango_type )          \
  template <> struct TangoType<plugin_type>                    \
  {                                                            \
    enum { Value = tango_type };                               \
  };

  MAP_TO_TANGO_TYPE(bool, Tango::DEV_BOOLEAN)
  MAP_TO_TANGO_TYPE(uint8_t, Tango::DEV_UCHAR)
  MAP_TO_TANGO_TYPE(int16_t, Tango::DEV_SHORT)
  MAP_TO_TANGO_TYPE(uint16_t, Tango::DEV_USHORT)
  MAP_TO_TANGO_TYPE(int32_t, Tango::DEV_LONG)
  MAP_TO_TANGO_TYPE(float, Tango::DEV_FLOAT)
  MAP_TO_TANGO_TYPE(double, Tango::DEV_DOUBLE)
  MAP_TO_TANGO_TYPE(std::string, Tango::DEV_STRING)

  struct YAT4TANGO_DECL TangoWriteType
  {
    Tango::AttrWriteType operator()( int plugin_write_type );
  };



#ifdef YAT_WIN32
#  pragma warning (pop)
#endif


} // namespace

#if defined (YAT_INLINE_IMPL)
# include "PlugInAttr.i"
#endif // __INLINE_IMPL___

#include <yat4tango/PlugInAttr.tpp>

#endif
