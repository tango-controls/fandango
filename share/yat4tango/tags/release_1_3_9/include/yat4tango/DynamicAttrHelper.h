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

#ifndef _YAT4TANGO_DYNAMIC_ATTR_HELPER_H_
#define _YAT4TANGO_DYNAMIC_ATTR_HELPER_H_


#include <yat4tango/CommonHeader.h>
#include <yat4tango/ExceptionHelper.h>


namespace yat4tango
{

typedef std::map <std::string, Tango::Attr*> DynAttrRepository;
typedef DynAttrRepository::value_type        DynAttrEntry;
typedef DynAttrRepository::iterator          DynAttrIt;
typedef DynAttrRepository::const_iterator    DynAttrCIt;

// ============================================================================
//
// class: DynamicAttrHelper
//
// ============================================================================
class YAT4TANGO_DECL DynamicAttrHelper
{
public:
  /**
   * Constructor. 
   * @param  _host_device the device handled by the instance
   */
  DynamicAttrHelper(Tango::DeviceImpl * _host_device);
  
  /**
   * Destructor
   */
  ~DynamicAttrHelper();

  /**
   * add_attribute
   * @param attr a Tango::Attr* to be registered
   */
  void add_attribute(Tango::Attr* attr)
		throw (Tango::DevFailed);

  /**
   * remove_attribute
   * @param name the attribute name
   */
  void remove_attribute(const std::string& name)
		throw (Tango::DevFailed);

  /**
   * remove_attribute
   *
   * Removes all the dynamic attributes registered
   */
  void remove_attributes()
		throw (Tango::DevFailed);

  /**
   * get_attribute (Tango::Attr version)
   * @param _name the attribute name
   * @param _a a reference to a Tango::Attr* where the pointer to the desired attribute is stored
   */
  Tango::Attr* get_attribute(const std::string& _name)
		throw (Tango::DevFailed)
  {
    DynAttrIt it = this->rep_.find(_name);
	  if (it == this->rep_.end())
	  {
	    THROW_DEVFAILED("OPERATION_NOT_ALLOWED",
	                    "Attribute does not exist",
                      "DynamicAttrHelper::get_scalar_attribute");
	  }
	  return (*it).second;
  };

  DynAttrCIt begin() const;
  DynAttrIt  begin();
  DynAttrCIt end() const;
  DynAttrIt  end();
  size_t     size() const;
  bool       empty() const;

private:
  Tango::DeviceImpl * host_device_;
  DynAttrRepository   rep_;

  DynamicAttrHelper(const DynamicAttrHelper&);
  DynamicAttrHelper& operator = (const DynamicAttrHelper&);
};


} // namespace

//=============================================================================
// INLINED CODE
//=============================================================================
#if defined (YAT_INLINE_IMPL)
# include "yat4tango/DynamicAttrHelper.i"
#endif // __INLINE_IMPL__

#endif
