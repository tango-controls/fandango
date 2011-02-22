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
 * \authors N. Leclercq & X. Elattaoui - Synchrotron SOLEIL
 */
 
#ifndef _MONITORED_DEVICE_H_
#define _MONITORED_DEVICE_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat4tango/CommonHeader.h>
#include <yat4tango/MonitoredAttribute.h>

namespace yat4tango
{

// ============================================================================
// TYPEDEFs
// ============================================================================
//- Monitored attribute key (or identifier)
typedef unsigned long MonitoredAttributeKey;
  
//- Monitored attributes keys
typedef std::vector<MonitoredAttributeKey> MonitoredAttributeKeyList;
  
// ============================================================================
// class: MonitoredDevice
// ============================================================================
class MonitoredDevice : public Tango::LogAdapter
{
public:
  //! Ctor
	MonitoredDevice (const std::string & dev_name, Tango::DeviceImpl * host = 0);

  //! Dtor
	virtual ~MonitoredDevice ();

  //! Adds the specified attribute to the MonitoredAttributes list
  //! Registration order is conserve till this MonitoredDevice is deleted
	MonitoredAttributeKey add_monitored_attribute (const std::string &  attr_name)
  	throw (Tango::DevFailed);
    
  //! Adds the specified attributes to the MonitoredAttributes list
  //! Registration order is conserve till this MonitoredDevice is deleted
	MonitoredAttributeKeyList add_monitored_attributes (const std::vector<std::string> &  attr_names)
  	throw (Tango::DevFailed);
    
  //! Returns a MonitoredAttribute by name
	MonitoredAttribute & get_monitored_attribute (const std::string & attr_name)
  	throw (Tango::DevFailed);
    
  //! Returns a MonitoredAttribute by key
	MonitoredAttribute & get_monitored_attribute (MonitoredAttributeKey attr_key)
  	throw (Tango::DevFailed);

	//! Read monitored attributes value 
	void poll_attributes ();
    
  //! Returns the monitored device name
  const std::string& device_name () const;
  
private:
  //- connects to the device (instanciates the Tango::DeviceProxy)
  void connect ()
  	throw (Tango::DevFailed); 
  
  //- closes connection to the device (releases the Tango::DeviceProxy)
  void disconnect (); 

  //- monitored device name
	std::string	_devName;
  
  //- monitored device proxy
  Tango::DeviceProxy * _dp;
  
	//- Internal cooking...
  MonitoredAttributeKey _monitoredAttributeKeyGen;
  
	//- Internal cooking...
  typedef std::vector<std::string> MonitoredAttributesNames;
	MonitoredAttributesNames _monitoredAttributesNames;
  
	//- Internal cooking...
  typedef std::map<MonitoredAttributeKey, MonitoredAttribute*> MonitoredAttributes;
  typedef MonitoredAttributes::iterator MonitoredAttributesIt;
	MonitoredAttributes _monitoredAttributes;
  
	//- Internal cooking...
  typedef std::map<const std::string, MonitoredAttributeKey> MonitoredAttributesKeys;
  typedef MonitoredAttributesKeys::iterator MonitoredAttributesKeysIt;
  MonitoredAttributesKeys _monitoredAttributesKeys;
};

}	//- namespace


#endif //-	_MONITORED_DEVICE_H_
