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
#include <yat4tango/DynamicAttrHelper.h>

#if !defined (YAT_INLINE_IMPL)
# include "yat4tango/DynamicAttrHelper.i"
#endif // __INLINE_IMPL__


namespace yat4tango
{

  // ============================================================================
  // DynamicAttrHelper::ctor
  // ============================================================================
  DynamicAttrHelper::DynamicAttrHelper(Tango::DeviceImpl * _host_device)
    : host_device_(_host_device)
  {
  };
  
  // ============================================================================
  // DynamicAttrHelper::dtor
  // ============================================================================
  DynamicAttrHelper::~DynamicAttrHelper()
  {
    this->remove_attributes();
  };

  // ============================================================================
  // DynamicAttrHelper::add_attribute
  // ============================================================================
  void DynamicAttrHelper::add_attribute(Tango::Attr* _attr)
		throw (Tango::DevFailed)
  {
    YAT_TRACE("DynamicAttrHelper::add_attribute");

    //- check attribute does not already exist
    DynAttrIt it = this->rep_.find(_attr->get_name());
    if (it != this->rep_.end())
    {
	    THROW_DEVFAILED("OPERATION_NOT_ALLOWED",
	                    "The attribute already exists",
                      "DynamicAttrHelper::add_attribute");
    }


    //- add it to the device
    try
    {
      this->host_device_->add_attribute( _attr );
    }
    catch(Tango::DevFailed& ex)
    {
	    RETHROW_DEVFAILED(ex,
                        "INTERNAL_ERROR",
	                      "The attribute could not be added to the device",
                        "DynamicAttrHelper::add_attribute");
    }
    catch(...)
    {
	    THROW_DEVFAILED( "UNKNOWN_ERROR",
	                     "Unknown error when trying to add attribute to the device",
                       "DynamicAttrHelper::add_attribute");
    }
    
    //- ok, everything went fine :
    //- insert the attribute into the list
    std::pair<DynAttrIt, bool> insertion_result;
    insertion_result = this->rep_.insert( DynAttrEntry(_attr->get_name(), _attr) );

    if (insertion_result.second == false)
    {
	    THROW_DEVFAILED("OPERATION_NOT_ALLOWED",
	                    "The attribute could not be inserted into the attribute map",
                      "DynamicAttrHelper::add_attribute");
    } 

  }

  // ============================================================================
  // DynamicAttrHelper::remove_attribute
  // ============================================================================
  void DynamicAttrHelper::remove_attribute(const std::string& _name)
		throw (Tango::DevFailed)
  {
    YAT_TRACE("DynamicAttrHelper::remove_attribute");

    //- check if attribute exists
    DynAttrIt it = this->rep_.find(_name);
    if (it == this->rep_.end())
    {
	    THROW_DEVFAILED("OPERATION_NOT_ALLOWED",
	                    "The attribute does not exist",
                      "DynamicAttrHelper::remove_attribute");
    }

    //- remove it from the device
    try
    {
      this->host_device_->remove_attribute( (*it).second, true );
    }
    catch(Tango::DevFailed& ex)
    {
	    RETHROW_DEVFAILED(ex,
                        "INTERNAL_ERROR",
	                      "The attribute could not be removed from the device",
                        "DynamicAttrHelper::remove_attribute");
    }
    catch(...)
    {
	    THROW_DEVFAILED("UNKNOWN_ERROR",
	                    "Could not remove attribute from the device",
                      "DynamicAttrHelper::remove_attribute");
    }

    //- remove from db
    Tango::DeviceData argin;
    std::vector<std::string> v(2);
    v[0] = this->host_device_->name();
    v[1] = _name;
    argin << v;

    Tango::Database * db = this->host_device_->get_db_device()->get_dbase();

    try
    {
      Tango::DeviceData argout = db->command_inout("DbDeleteDeviceAttribute", argin);
    }
    catch(Tango::DevFailed& ex)
    {
	    RETHROW_DEVFAILED(ex,
                        "INTERNAL_ERROR",
	                      "Unable to delete attribute from the database",
                        "DynamicAttrHelper::remove_attribute");
    }
    catch(...)
    {
	    THROW_DEVFAILED("UNKNOWN_ERROR",
	                    "Unable to delete attribute from the database",
                      "DynamicAttrHelper::remove_attribute");
    }

    //- remove from the internal map
    this->rep_.erase(it);

  };



  // ============================================================================
  // DynamicAttrHelper::remove_attributes
  // ============================================================================
  void DynamicAttrHelper::remove_attributes()
		throw (Tango::DevFailed)
  {
    YAT_TRACE("DynamicAttrHelper::remove_attributes");

    DynAttrIt it;

    Tango::DeviceData argin;
    std::vector<std::string> v(2);
    v[0] = this->host_device_->name();

    for (it  = this->rep_.begin(); it != this->rep_.end(); ++it)
    {

      //- remove it from the device
      try
      {
        this->host_device_->remove_attribute( (*it).second, true );
      }
      catch(Tango::DevFailed& ex)
      {
	      RETHROW_DEVFAILED(ex,
                          "INTERNAL_ERROR",
	                        "The attribute could not be removed from the device",
                          "DynamicAttrHelper::remove_attribute");
      }
      catch(...)
      {
	      THROW_DEVFAILED("UNKNOWN_ERROR",
	                      "Could not remove attribute from the device",
                        "DynamicAttrHelper::remove_attribute");
      }



      //- remove from db
      v[1] = (*it).first;
      argin << v;
      Tango::Database * db = this->host_device_->get_db_device()->get_dbase();

      try
      {
        Tango::DeviceData argout = db->command_inout("DbDeleteDeviceAttribute", argin);
      }
      catch(Tango::DevFailed& ex)
      {
	      RETHROW_DEVFAILED(ex,
                          "INTERNAL_ERROR",
	                        "Unable to delete attribute from the database",
                          "DynamicAttrHelper::remove_attribute");
      }
      catch(...)
      {
	      THROW_DEVFAILED("UNKNOWN_ERROR",
	                      "Unable to delete attribute from the database",
                        "DynamicAttrHelper::remove_attribute");
      }
    }


    //- then clear the map
    this->rep_.clear();

  }

} // namespace

