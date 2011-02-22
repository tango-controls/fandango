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
#include <yat4tango/DynamicAttr.h>

namespace yat4tango
{
  template<> const long DynamicAttr<Tango::DevBoolean>::tango_type = Tango::DEV_BOOLEAN;

  template<> const long DynamicAttr<Tango::DevUChar>::tango_type = Tango::DEV_UCHAR;

  template<> const long DynamicAttr<Tango::DevShort>::tango_type = Tango::DEV_SHORT;

  template<> const long DynamicAttr<Tango::DevUShort>::tango_type = Tango::DEV_USHORT;

  template<> const long DynamicAttr<Tango::DevLong>::tango_type = Tango::DEV_LONG;

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

  template<> const Tango::DevFloat   DynamicAttr<Tango::DevFloat>::dummy_value =
    std::numeric_limits<Tango::DevFloat>  ::quiet_NaN();

  template<> const Tango::DevDouble  DynamicAttr<Tango::DevDouble>::dummy_value =
    std::numeric_limits<Tango::DevDouble> ::quiet_NaN();
}

