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

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat4tango/DynamicAttr.h>

namespace yat4tango
{
  template<> const long DynamicAttr<Tango::DevBoolean>::tango_type = Tango::DEV_BOOLEAN;

  template<> const long DynamicAttr<Tango::DevUChar>::tango_type = Tango::DEV_UCHAR;

  template<> const long DynamicAttr<Tango::DevShort>::tango_type = Tango::DEV_SHORT;

  template<> const long DynamicAttr<Tango::DevUShort>::tango_type = Tango::DEV_USHORT;

  template<> const long DynamicAttr<Tango::DevLong>::tango_type = Tango::DEV_LONG;

  template<> const long DynamicAttr<Tango::DevULong>::tango_type = Tango::DEV_ULONG;

  template<> const long DynamicAttr<Tango::DevFloat>::tango_type = Tango::DEV_FLOAT;

  template<> const long DynamicAttr<Tango::DevDouble>::tango_type = Tango::DEV_DOUBLE;

  template<> const Tango::DevBoolean DynamicAttr<Tango::DevBoolean>::dummy_value =
    std::numeric_limits<Tango::DevBoolean>::quiet_NaN();

  template<> const Tango::DevUChar   DynamicAttr<Tango::DevUChar>::dummy_value =
    std::numeric_limits<Tango::DevUChar>  ::quiet_NaN();

  template<> const Tango::DevShort   DynamicAttr<Tango::DevShort>::dummy_value =
    std::numeric_limits<Tango::DevShort>  ::quiet_NaN();

  template<> const Tango::DevUShort  DynamicAttr<Tango::DevUShort>::dummy_value =
    std::numeric_limits<Tango::DevUShort> ::quiet_NaN();

  template<> const Tango::DevLong    DynamicAttr<Tango::DevLong>::dummy_value =
    std::numeric_limits<Tango::DevLong>   ::quiet_NaN();

  template<> const Tango::DevULong    DynamicAttr<Tango::DevULong>::dummy_value =
    std::numeric_limits<Tango::DevULong>   ::quiet_NaN();

  template<> const Tango::DevFloat   DynamicAttr<Tango::DevFloat>::dummy_value =
    std::numeric_limits<Tango::DevFloat>  ::quiet_NaN();

  template<> const Tango::DevDouble  DynamicAttr<Tango::DevDouble>::dummy_value =
    std::numeric_limits<Tango::DevDouble> ::quiet_NaN();
}

