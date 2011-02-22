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
 
namespace yat4tango
{

//=============================================================================
// ThreadSafeDeviceProxy::state
//=============================================================================
YAT_INLINE const std::string ThreadSafeDeviceProxy::status (void)
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.status();
}

//=============================================================================
// ThreadSafeDeviceProxy::dev_name
//=============================================================================
YAT_INLINE std::string ThreadSafeDeviceProxy::dev_name (void)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.dev_name();
}

//=============================================================================
// ThreadSafeDeviceProxy::state
//=============================================================================
YAT_INLINE Tango::DevState ThreadSafeDeviceProxy::state (void)
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.state();
}

//=============================================================================
// ThreadSafeDeviceProxy::ping
//=============================================================================
YAT_INLINE int ThreadSafeDeviceProxy::ping (void)
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.ping();
}

//=============================================================================
// ThreadSafeDeviceProxy::command_query
//=============================================================================
YAT_INLINE Tango::CommandInfo ThreadSafeDeviceProxy::command_query (const std::string& cmd_name)
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.command_query(cmd_name);
}

//=============================================================================
// ThreadSafeDeviceProxy::command_list_query
//=============================================================================
YAT_INLINE Tango::CommandInfoList* ThreadSafeDeviceProxy::command_list_query (void)
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.command_list_query();
}

//=============================================================================
// ThreadSafeDeviceProxy::attribute_query
//=============================================================================
YAT_INLINE Tango::AttributeInfoEx ThreadSafeDeviceProxy::attribute_query (const std::string& name)
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.attribute_query(name);
}

//=============================================================================
// ThreadSafeDeviceProxy::attribute_list_query
//=============================================================================
YAT_INLINE Tango::AttributeInfoList* ThreadSafeDeviceProxy::attribute_list_query (void)
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.attribute_list_query();
}

//=============================================================================
// ThreadSafeDeviceProxy::read_attribute
//=============================================================================
YAT_INLINE Tango::DeviceAttribute ThreadSafeDeviceProxy::read_attribute (const std::string& attr_name)
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.read_attribute(const_cast<std::string&>(attr_name));
}

//=============================================================================
// ThreadSafeDeviceProxy::read_attribute
//=============================================================================
YAT_INLINE Tango::DeviceAttribute ThreadSafeDeviceProxy::read_attribute (const char *attr_name)
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.read_attribute(attr_name);
}

//=============================================================================
// ThreadSafeDeviceProxy::read_attribute_asynch
//=============================================================================
YAT_INLINE void ThreadSafeDeviceProxy::read_attribute_asynch (const char *attr_name, Tango::CallBack &cb)
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  this->dp_.read_attribute_asynch(attr_name,cb);
}

//=============================================================================
// ThreadSafeDeviceProxy::read_attribute_asynch
//=============================================================================
YAT_INLINE long ThreadSafeDeviceProxy::read_attribute_asynch (const char *attr_name)
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.read_attribute_asynch(attr_name);
}

//=============================================================================
// ThreadSafeDeviceProxy:read_attributes
//=============================================================================
YAT_INLINE std::vector<Tango::DeviceAttribute>*
ThreadSafeDeviceProxy::read_attributes (const std::vector<std::string>& attr_names)
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.read_attributes(const_cast<std::vector<std::string>&>(attr_names));
}

//=============================================================================
// ThreadSafeDeviceProxy:read_attributes_asynch
//=============================================================================
YAT_INLINE void
ThreadSafeDeviceProxy::read_attributes_asynch (const std::vector<std::string>& attr_names, Tango::CallBack &cb)
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);  
  this->dp_.read_attributes_asynch(const_cast<std::vector<std::string>&>(attr_names), cb);
}

//=============================================================================
// ThreadSafeDeviceProxy:read_attributes_asynch
//=============================================================================
YAT_INLINE long
ThreadSafeDeviceProxy::read_attributes_asynch (const std::vector<std::string>& attr_names)
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);  
  return this->dp_.read_attributes_asynch(const_cast<std::vector<std::string>&>(attr_names));
}


//=============================================================================
// ThreadSafeDeviceProxy::write_attribute
//=============================================================================
YAT_INLINE void
ThreadSafeDeviceProxy::write_attribute (const Tango::DeviceAttribute& attr_value) 
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  this->dp_.write_attribute(const_cast<Tango::DeviceAttribute&>(attr_value));
}

//=============================================================================
// ThreadSafeDeviceProxy::write_attribute_asynch
//=============================================================================
YAT_INLINE void
ThreadSafeDeviceProxy::write_attribute_asynch (const Tango::DeviceAttribute& attr_value, Tango::CallBack &cb) 
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  this->dp_.write_attribute_asynch(const_cast<Tango::DeviceAttribute&>(attr_value), cb);
}

//=============================================================================
// ThreadSafeDeviceProxy::write_attribute_asynch
//=============================================================================
YAT_INLINE long
ThreadSafeDeviceProxy::write_attribute_asynch (const Tango::DeviceAttribute& attr_value) 
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.write_attribute_asynch(const_cast<Tango::DeviceAttribute&>(attr_value));
}

//=============================================================================
// ThreadSafeDeviceProxy::write_attributes
//=============================================================================
YAT_INLINE void
ThreadSafeDeviceProxy::write_attributes (const std::vector<Tango::DeviceAttribute>& attr_values) 
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  this->dp_.write_attributes(const_cast<std::vector<Tango::DeviceAttribute>&>(attr_values));
}

//=============================================================================
// ThreadSafeDeviceProxy::write_attributes_asynch
//=============================================================================
YAT_INLINE void
ThreadSafeDeviceProxy::write_attributes_asynch (const std::vector<Tango::DeviceAttribute>& attr_values, Tango::CallBack &cb) 
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  this->dp_.write_attributes_asynch(const_cast<std::vector<Tango::DeviceAttribute>&>(attr_values), cb);
}

//=============================================================================
// ThreadSafeDeviceProxy::write_attributes_asynch
//=============================================================================
YAT_INLINE long
ThreadSafeDeviceProxy::write_attributes_asynch (const std::vector<Tango::DeviceAttribute>& attr_values) 
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.write_attributes_asynch(const_cast<std::vector<Tango::DeviceAttribute>&>(attr_values));
}


//=============================================================================
// ThreadSafeDeviceProxy::command_inout
//=============================================================================
YAT_INLINE Tango::DeviceData
ThreadSafeDeviceProxy::command_inout (const std::string& cmd_name) 
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.command_inout(const_cast<std::string&>(cmd_name));
}

//=============================================================================
// ThreadSafeDeviceProxy::command_inout
//=============================================================================
YAT_INLINE Tango::DeviceData
ThreadSafeDeviceProxy::command_inout (const char * cmd_name) 
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.command_inout(cmd_name);
}

//=============================================================================
// ThreadSafeDeviceProxy::command_inout
//=============================================================================
YAT_INLINE Tango::DeviceData
ThreadSafeDeviceProxy::command_inout (const std::string& cmd_name, 
                                      const Tango::DeviceData &d) 
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.command_inout(const_cast<std::string&>(cmd_name),
                                 const_cast<Tango::DeviceData &>(d));
}

//=============================================================================
// ThreadSafeDeviceProxy::command_inout
//=============================================================================
YAT_INLINE Tango::DeviceData
ThreadSafeDeviceProxy::command_inout (const char * cmd_name, 
                                      const Tango::DeviceData &d) 
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.command_inout(cmd_name,
                                 const_cast<Tango::DeviceData &>(d));
}

//=============================================================================
// ThreadSafeDeviceProxy::command_inout
//=============================================================================
YAT_INLINE int
ThreadSafeDeviceProxy::subscribe_event(const std::string &attr_name, 
                                       Tango::EventType event, 
                                       Tango::CallBack *cb, 
                                       const vector<string> &filters) 
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.subscribe_event(attr_name, event, cb, filters);
}


//=============================================================================
// ThreadSafeDeviceProxy::unsubscribe_event
//=============================================================================
YAT_INLINE void
ThreadSafeDeviceProxy::unsubscribe_event (int event_id)
  throw (Tango::DevFailed)
{
  yat::AutoMutex<> guard(this->lock_);
  this->dp_.unsubscribe_event(event_id);
}

//=============================================================================
// ThreadSafeDeviceProxy::set_timeout_millis
//=============================================================================
YAT_INLINE void
ThreadSafeDeviceProxy::set_timeout_millis (int tmo_ms)
{
  yat::AutoMutex<> guard(this->lock_);
  this->dp_.set_timeout_millis(tmo_ms);
}

//=============================================================================
// ThreadSafeDeviceProxy::get_timeout_millis
//=============================================================================
YAT_INLINE int
ThreadSafeDeviceProxy::get_timeout_millis (void)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.get_timeout_millis();
}

//=============================================================================
// ThreadSafeDeviceProxy::get_timeout_millis
//=============================================================================
YAT_INLINE std::vector<std::string> *
ThreadSafeDeviceProxy::black_box (int n)
{
  yat::AutoMutex<> guard(this->lock_);
  return this->dp_.black_box (n);
}

//=============================================================================
// ThreadSafeDeviceProxy::unsafe_proxy
//=============================================================================
YAT_INLINE Tango::DeviceProxy&
ThreadSafeDeviceProxy::unsafe_proxy (void)
{
  return this->dp_;
}

} // namespace
