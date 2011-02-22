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

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat4tango/MonitoredDevice.h>

namespace yat4tango
{

// ======================================================================
// MonitoredDevice::MonitoredDevice
// ======================================================================
MonitoredDevice::MonitoredDevice (const std::string & devName, Tango::DeviceImpl * host)
	:	Tango::LogAdapter(host), _devName(devName), _dp(0), _monitoredAttributeKeyGen(0)
{
	//- noop
}

// ======================================================================
// MonitoredDevice::~MonitoredDevice
// ======================================================================
MonitoredDevice::~MonitoredDevice ()
{
  this->disconnect();
  
  
}
    
// ======================================================================
// MonitoredDevice::connect
// ======================================================================
void MonitoredDevice::connect ()
  	throw (Tango::DevFailed)
{
  //- close any exisitng connection to the device
  this->disconnect();
    
  //- instanciate the proxy
  this->_dp = new (std::nothrow) Tango::DeviceProxy(this->_devName);
  if (! this->_dp)
  {
    ERROR_STREAM << "MonitoredDevice::connect::failed to connect to " << this->_devName << std::endl;
    THROW_DEVFAILED("MEMORY_ERROR",
                    "Tango::DeviceProxy instanciation failed",
                    "MonitoredDevice::connect");
  }
}

// ======================================================================
// MonitoredDevice::disconnect
// ======================================================================
void MonitoredDevice::disconnect ()
{
  delete this->_dp;
  this->_dp = 0;
}

// ======================================================================
// MonitoredDevice::add_monitored_attribute
// ======================================================================
MonitoredAttributeKey MonitoredDevice::add_monitored_attribute (const std::string &  attr_name)
  throw (Tango::DevFailed)
{
  MonitoredAttributesKeysIt it = _monitoredAttributesKeys.find(attr_name);
  if (it != this->_monitoredAttributesKeys.end())
  	return it->second;
  
  MonitoredAttributeKey k = this->_monitoredAttributeKeyGen++;
  
  std::pair<MonitoredAttributesKeysIt, bool> kir;
  kir = this->_monitoredAttributesKeys.insert(MonitoredAttributesKeys::value_type(attr_name, k));
  if (! kir.second) 
  {
    THROW_DEVFAILED("INTERNAL_ERROR",
                    "failed to add MonitoredAttribute [std::map::insert failed]",
			              " MonitoredDevice::add_monitored_attribute");
  }
  
  MonitoredAttribute * ma = new (std::nothrow) MonitoredAttribute;
  if (! ma)
  {
    MonitoredAttributesKeysIt it = this->_monitoredAttributesKeys.find(attr_name);
  	this->_monitoredAttributesKeys.erase(it);
    THROW_DEVFAILED("MEMORY_ERROR",
                    "failed to add MonitoredAttribute [MonitoredAttribute instanciation failed]",
			              " MonitoredDevice::add_monitored_attribute");
  }
  
  std::pair<MonitoredAttributesIt, bool> air;
  air = this->_monitoredAttributes.insert(MonitoredAttributes::value_type(k, ma));
  if (! air.second) 
  {
    MonitoredAttributesKeysIt it = this->_monitoredAttributesKeys.find(attr_name);
  	this->_monitoredAttributesKeys.erase(it);
    THROW_DEVFAILED("INTERNAL_ERROR",
                    "failed to add MonitoredAttribute [std::map::insert failed]",
			              " MonitoredDevice::add_monitored_attribute");
  }
  
  _monitoredAttributesNames.push_back(attr_name);
  
  return k;
}

// ======================================================================
// MonitoredDevice::add_monitored_attributes
// ======================================================================
MonitoredAttributeKeyList MonitoredDevice::add_monitored_attributes (const std::vector<std::string> &  attr_names)
  throw (Tango::DevFailed)
{
  MonitoredAttributeKeyList keys;

  for (size_t a = 0; a < attr_names.size(); a++)
    keys.push_back(this->add_monitored_attribute(attr_names[a]));
  
  return keys;
}

// ======================================================================
// MonitoredDevice::get_monitored_attribute
// ======================================================================
MonitoredAttribute & MonitoredDevice::get_monitored_attribute (const std::string & attr_name)
  throw (Tango::DevFailed)
{
  MonitoredAttributesKeysIt kit = this->_monitoredAttributesKeys.find(attr_name);
  if (kit == this->_monitoredAttributesKeys.end())
  {
    yat::OSStream s;
    s << "no such monitored attribute [attr. <" << attr_name << "> could not be found]";
    THROW_DEVFAILED("DEVICE_ERROR",
                    s.str().c_str(),
			              " MonitoredDevice::get_monitored_attribute");
  }
  
  return this->get_monitored_attribute(kit->second);
}
   
// ======================================================================
// MonitoredDevice::get_monitored_attribute
// ======================================================================
MonitoredAttribute & MonitoredDevice::get_monitored_attribute (MonitoredAttributeKey attr_key)
  throw (Tango::DevFailed)
{
  MonitoredAttributesIt ait = this->_monitoredAttributes.find(attr_key);
  if (ait == this->_monitoredAttributes.end())
  {
    yat::OSStream s;
    s << "no such monitored attribute [key <" << attr_key << "> could not be found]";
    THROW_DEVFAILED("DEVICE_ERROR",
                    s.str().c_str(),
			              " MonitoredDevice::get_monitored_attribute");
  }
  
  return *(ait->second);
}
    
// ======================================================================
// MonitoredDevice::poll_attributes
// ======================================================================
void MonitoredDevice::poll_attributes ()
{
  if (this->_monitoredAttributesNames.empty())
  	return;
    
  std::vector<Tango::DeviceAttribute> * dev_attrs = 0;
  
  try
  {
    if (! this->_dp)
  	 this->connect();

    //- read attributes on device
    dev_attrs = this->_dp->read_attributes(_monitoredAttributesNames);

    //- set value on each monitored attribute
    MonitoredAttributesIt it = _monitoredAttributes.begin();
    MonitoredAttributesIt end = _monitoredAttributes.end();
    for (size_t i = 0; it != end; ++it, i++)
      (it->second)->set_value((*dev_attrs)[i]);
  }
  catch (Tango::DevFailed& df)
  {
    try 
    {
      RETHROW_DEVFAILED(df,
                        "DEVICE_ERROR",
                        "Tango exception caught while trying to read monitored attributes",
                        "MonitoredDevice::poll_attributes");
    }
    catch (const Tango::DevFailed& extented_df) 
    {
    	//- set error on each monitored attribute
      MonitoredAttributesIt it = _monitoredAttributes.begin();
    	MonitoredAttributesIt end = _monitoredAttributes.end();
    	for(size_t i = 0; it != end; ++it, i++)
      	(it->second)->set_error(extented_df);
    }
  }
  catch (...)
  {
    try 
    {
      THROW_DEVFAILED("UNKNOWN_ERROR",
                      "unknown exception caught while trying to read monitored attributes",
                      "MonitoredDevice::poll_attributes");
    }
    catch (const Tango::DevFailed& df) 
    {
    	//- set error on each monitored attribute
      MonitoredAttributesIt it = _monitoredAttributes.begin();
    	MonitoredAttributesIt end = _monitoredAttributes.end();
    	for(size_t i = 0; it != end; ++it, i++)
      	(it->second)->set_error(df);
    }
  }
  
  //- release memory
  if (dev_attrs)
  	delete dev_attrs;
}

// ======================================================================
// MonitoredDevice::device_name
// ======================================================================
const std::string& MonitoredDevice::device_name () const
{ 
  return this->_devName; 
}

}	//- end namespace
