/*!
 * \file
 * \brief    
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
 */

#ifndef _YAT4TANGO_TS_DEV_PROXY_H_
#define _YAT4TANGO_TS_DEV_PROXY_H_


#include <yat4tango/CommonHeader.h>

namespace yat4tango
{

//=============================================================================
// Class ThreadSafeDeviceProxy
//=============================================================================
class YAT4TANGO_DECL ThreadSafeDeviceProxy
{
public:

  ThreadSafeDeviceProxy (const std::string& dev_name) 
    throw (Tango::DevFailed);

	ThreadSafeDeviceProxy (const char * dev_name) 
    throw (Tango::DevFailed);

  virtual ~ThreadSafeDeviceProxy ();

  const std::string status (void) 
    throw (Tango::DevFailed);

	Tango::DevState state (void)
    throw (Tango::DevFailed);

  int ping (void) 
    throw (Tango::DevFailed);

  Tango::CommandInfo command_query (const std::string&) 
    throw (Tango::DevFailed);

  Tango::CommandInfoList* command_list_query (void) 
    throw (Tango::DevFailed);

  Tango::AttributeInfoEx attribute_query (const std::string&)
    throw (Tango::DevFailed);

  Tango::AttributeInfoList* attribute_list_query (void) 
    throw (Tango::DevFailed);


  Tango::DeviceAttribute read_attribute (const std::string& attr_name) 
    throw (Tango::DevFailed);

	Tango::DeviceAttribute read_attribute (const char *attr_name) 
    throw (Tango::DevFailed);
	
  void read_attribute_asynch (const char *attr_name, Tango::CallBack &cb) 
    throw (Tango::DevFailed);
  
  long read_attribute_asynch (const char *attr_name) 
    throw (Tango::DevFailed);


  std::vector<Tango::DeviceAttribute>* read_attributes (const std::vector<std::string>& attr_names) 
    throw (Tango::DevFailed);
  
  void read_attributes_asynch (const std::vector<std::string>& attr_names, Tango::CallBack &cb) 
    throw (Tango::DevFailed);
  
  long read_attributes_asynch (const std::vector<std::string>& attr_names) 
    throw (Tango::DevFailed);


	void write_attribute (const Tango::DeviceAttribute& attr_value) 
    throw (Tango::DevFailed);

	void write_attribute_asynch (const Tango::DeviceAttribute& attr_value, Tango::CallBack &cb) 
    throw (Tango::DevFailed);
	
  long write_attribute_asynch (const Tango::DeviceAttribute& attr_value) 
    throw (Tango::DevFailed);


	void write_attributes (const std::vector<Tango::DeviceAttribute>& attr_values) 
    throw (Tango::DevFailed);
	
  void write_attributes_asynch (const std::vector<Tango::DeviceAttribute>& attr_values, Tango::CallBack &cb) 
    throw (Tango::DevFailed);
  
  long write_attributes_asynch (const std::vector<Tango::DeviceAttribute>& attr_values) 
    throw (Tango::DevFailed);

  Tango::DeviceData command_inout (const std::string& cmd_name) 
    throw (Tango::DevFailed);

	Tango::DeviceData command_inout (const char * cmd_name) 
    throw (Tango::DevFailed);

  Tango::DeviceData command_inout (const std::string& cmd_name, const Tango::DeviceData &d) 
    throw (Tango::DevFailed);

	Tango::DeviceData command_inout (const char *cmd_name, const Tango::DeviceData &d) 
    throw (Tango::DevFailed);

  int subscribe_event(const string &attr_name, 
                      Tango::EventType event, 
                      Tango::CallBack *cb, 
                      const std::vector<std::string> &filters) 
    throw (Tango::DevFailed);

	void unsubscribe_event(int event_id) 
    throw (Tango::DevFailed);

  void set_timeout_millis (int tmo_ms);

  int get_timeout_millis (void);

  std::vector<std::string> * black_box (int n);

  Tango::DeviceProxy& unsafe_proxy (void);
  
  std::string dev_name (void);

private:

  Tango::DeviceProxy  dp_;

  omni_mutex lock_;

  // = Disallow these operations (except for friends).
  //---------------------------------------------------------
  ThreadSafeDeviceProxy (const ThreadSafeDeviceProxy&);
  void operator= (const ThreadSafeDeviceProxy&); 
};

} // namespace 

#if defined (YAT_INLINE_IMPL)
  #include "ThreadSafeDeviceProxy.i"
#endif 

#endif // _TS_DEV_PROXY_H_
