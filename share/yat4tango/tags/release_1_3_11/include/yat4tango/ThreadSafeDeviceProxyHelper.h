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

//+=============================================================================
// = CONTEXT
//   YAT4tango lib
//
// File: 
// ThreadSafeDeviceProxyHelper.h:
//
// Description :
// This utility class helps to use command_inout,read_attributes and write_attribute(s) 
// on a ThreadSafeDeviceProxy , from a Tango C++ Client. The aim is :
// - to provide syntactic shortcuts in order to avoid the heavy manipulation of DeviceData 
//   objects used to exchange data between a C++ client and a server
// - to handle exception in an uniform way using the TangoExceptionHelper.h file
//
// Examples:
// - step 1: create a ThreadSafeDeviceProxyHelper object (upon receipt of the THREAD_INIT msg for instance)
//   
//   tsdp = new ThreadSafeThreadSafeDeviceProxyHelper("my/device/name", host_device);
//
// - step 2: use it just as you could do with a Tango::DeviceProxy
//
//   -> executing a TANGO commands:
//      -> note that  DEVVAR<X>STRINGARRAY argin or argout types are not supported - see below)
//      -> there are actually 4 methods:
//         - ThreadSafeDeviceProxyHelper::command (no argin nor argout)
//         - ThreadSafeDeviceProxyHelper::command_in (argin only)
//         - ThreadSafeDeviceProxyHelper::command_out (argout only)
//         - ThreadSafeDeviceProxyHelper::command_inout (argin and argout)
//      -> those 4 methods are templates so you don't care about data type (as far as it's supported)
//      -> command examples:
//         - execute the "Reset" command: no argin nor argout required
//           tsdp->command("Reset");
//         - execute the "GotoPosition" with argin = 12.3
//           tsdp->command_in("GotoPosition", 12.3);
//         - execute "ReadPosition" - argout will be put into read_value
//           tsdp->command_out("ReadPosition", read_value);
//         - execute "ReadDouble" - channel_id is the argin and channel_value is the argout.
//           tsdp->command_inout("ReadChannel", channel_id, channel_value);
//       -> how to execute a command with a DEVVAR<X>STRINGARRAY:
//          -> command with argin only:
//             void command_in (
//                              const std::string& cmd_name,           //- command name
//                              const std::vector<_IN>& _nv_in,        //- numerical part of the DEVVAR<X>STRINGARRAY
//                              const std::vector<std::string>& _sv_in //- string part of the DEVVAR<X>STRINGARRAY
//                             )
//          -> command with argout only:
//             void command_out (
//                               const std::string& cmd_name,      //- command name
//                               std::vector<_OUT>& _nv_out,       //- numerical part of the DEVVAR<X>STRINGARRAY
//                               std::vector<std::string>& _sv_out //- string part of the DEVVAR<X>STRINGARRAY
//                              )
//
//          -> command with argin and argout:
//             void command_inout (
//                                 const std::string& cmd_name,            //- command name
//                                 const std::vector<_IN>& _nv_in,         //- numerical part of the input DEVVAR<X>STRINGARRAY
//                                 const std::vector<std::string>& _sv_in, //- string part of the input DEVVAR<X>STRINGARRAY
//                                 std::vector<_OUT>& _nv_out,             //- numerical part of the ouput DEVVAR<X>STRINGARRAY
//                                 std::vector<std::string>& _sv_out       //- string part of the ouput DEVVAR<X>STRINGARRAY
//                                )
//
//   -> reding/writing a TANGO attribute:
//      -> read_attribute:
//         tsdp->read_attribute("AxisCurrentPosition" , axis_pos);
//      -> write_attribute:
//         tsdp->write_attribute("AxisCurrentPosition", 12.3);
//+=============================================================================

// ============================================================================
// WIN32 SPECIFIC
// ============================================================================
#if defined (WIN32)
# pragma warning(disable:4786)
#endif

#ifndef _THREAD_SAFE_DEVICE_PROXY_HELPER_H_
#define _THREAD_SAFE_DEVICE_PROXY_HELPER_H_

//=============================================================================
// DEPENDENCIES
//=============================================================================
#include <ThreadSafeDeviceProxy.h>
#include <TangoExceptionsHelper.h>

//=============================================================================
// MACRO
//=============================================================================
#define FULL_CMD_NAME(C) device_proxy_->dev_name() + "::" + C
#define FULL_ATTR_NAME(A) device_proxy_->dev_name() + "/" + A

//	Definition of macros to benefit from expansion of __FILE__ and __LINE__ keywords in Device caller source file
#define read_attribute(ATTR_NAME, VALUE) internal_read_attribute (ATTR_NAME, VALUE, __FILE__, __LINE__)
#define read_attribute_w(ATTR_NAME, VALUE) internal_read_attribute_w (ATTR_NAME, VALUE, __FILE__, __LINE__)
#define write_attribute(ATTR_NAME, VALUE) internal_write_attribute (ATTR_NAME, VALUE, __FILE__, __LINE__)
#define command(CMD_NAME) internal_command (CMD_NAME,  __FILE__, __LINE__)

// For VC++ 6 VA_ARG macro is not supported so ==>, we cannot override command_out functions
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#define command_out internal_command_out
#else	// For compilers that support variable number of arguments
#define command_out(CMD_NAME, OUT, ...) internal_command_out (CMD_NAME, OUT, ## __VA_ARGS__, __FILE__, __LINE__ )
#endif

// For VC++ 6 VA_ARG macro is not supported so ==>, we cannot override command_in functions
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#define command_in internal_command_in
#else	// For compilers that support variable number of arguments
#define command_in(CMD_NAME, IN, ...) internal_command_in (CMD_NAME, IN, ## __VA_ARGS__, __FILE__, __LINE__ )
#endif

// For VC++ 6 VA_ARG macro is not supported so ==>, we cannot override command_inout functions
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#define command_inout internal_command_inout
#else	// For compilers that support variable number of arguments
#define command_inout(CMD_NAME,  ...) internal_command_inout (CMD_NAME,  ## __VA_ARGS__, __FILE__, __LINE__ )
#endif

namespace yat4tango
{
	//=============================================================================
	// CLASS: HelperBase
	//=============================================================================
	class YAT4TANGO_EXPORT HelperBase : public Tango::LogAdapter
	{
	public:
		//---------------------------------------------------------------------------
		//  HelperBase::get_device_proxy
		//  returns the underlying device
		//---------------------------------------------------------------------------
		inline Tango::DeviceProxy& get_device_proxy (void)
		{
			return this->device_proxy_->unsafe_proxy();
		}
		//---------------------------------------------------------------------------
		//  HelperBase::operator->
		//  returns the underlying device
		//---------------------------------------------------------------------------
		inline Tango::DeviceProxy& operator-> (void)
		{
			return this->device_proxy_->unsafe_proxy();
		}
	protected:
		//---------------------------------------------------------------------------
		//  HelperBase::HelperBase  (ctor)
		//  device_name : The name of the target device.
		//  client_device : Reference to the client device (for logging purpose).
		//---------------------------------------------------------------------------
		HelperBase (const std::string& device_name, Tango::DeviceImpl *client_device = 0)
			throw (Tango::DevFailed)
			: Tango::LogAdapter(client_device), device_proxy_(0)
		{
			_DEV_TRY_REACTION
				(
				 //- try
				 device_proxy_ = new ThreadSafeDeviceProxy(const_cast<std::string&>(device_name)),
				 //- what do we tried
				 std::string("new ThreadSafeDeviceProxy on ") + device_name,
				 //- origin
				 "HelperBase::HelperBase",
				 //- reaction
				 if (device_proxy_) {delete device_proxy_; device_proxy_ = 0;}
				);
		}
		//---------------------------------------------------------------------------
		// HelperBase::~HelperBase (dtor)
		//---------------------------------------------------------------------------
		virtual ~HelperBase ()
		{
			if (device_proxy_)
			{
				delete device_proxy_;
				device_proxy_ = 0;
			}
		}
		//---------------------------------------------------------------------------
		//- the underlying device
		//---------------------------------------------------------------------------
		adtb::ThreadSafeDeviceProxy * device_proxy_;
	};
	
	//=============================================================================
	// CLASS: CommandInOutHelper
	//=============================================================================
	class YAT4TANGO_EXPORT CommandInOutHelper : public virtual HelperBase
	{
	public:
		//---------------------------------------------------------------------------
		//  CommandInOutHelper::CommandInOutHelper  (ctor)
		//  device_name : The name of the target device.
		//  client_device : Reference to the client device (for logging purpose).
		//---------------------------------------------------------------------------
		CommandInOutHelper (const std::string& device_name, Tango::DeviceImpl *client_device = 0)
			: HelperBase(device_name, client_device)
		{
			dd_out_.exceptions(Tango::DeviceData::isempty_flag | Tango::DeviceData::wrongtype_flag);
		}
		//---------------------------------------------------------------------------
		//  CommandInOutHelper::~CommandInOutHelper  (dtor)
		//---------------------------------------------------------------------------
		virtual ~CommandInOutHelper ()
		{
			//- noop dtor
		}
		//---------------------------------------------------------------------------
		//  CommandInOutHelper::command
		//  exec a DEV_VOID/DEV_VOID TANGO command on the underlying device
		//  cmd_name : The name of the TANGO command
		//---------------------------------------------------------------------------
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#undef command_inout	// Must avoid macro expansion 
#endif	
		void internal_command (const std::string& cmd_name,
			                     std::string file,
			                     int line)
			throw (Tango::DevFailed)
		{
			if (this->device_proxy_)
			{
				_DEV_TRY_FILE_LINE
					(
  					 //- try
  					 (device_proxy_->command_inout)(const_cast<std::string&>(cmd_name)),
  					 //- what do we tried
  					 std::string("command_inout on ") + FULL_CMD_NAME(cmd_name),
  					 //- origin
  					 "CommandInOutHelper::command",
  					 file,
  					 line
					);
			}
		}
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#define command_inout internal_command_inout
#endif
		//---------------------------------------------------------------------------
		//  CommandInOutHelper::command_inout
		//  exec a ARG_OUT/ARG_IN TANGO command on the underlying device
		//  cmd_name : the name of the TANGO command
		//  argin : input argument
		//  argout : output argument
		//---------------------------------------------------------------------------
		//  template arg _IN must be supported by DeviceData::operator<<
		//  template arg _OUT must be supported by DeviceData::operator>>
		//---------------------------------------------------------------------------
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#undef command_inout	// Must avoid macro expansion 
#endif
		template <class _IN, class _OUT>
			void internal_command_inout (const std::string& cmd_name, 
                                   const _IN& argin, 
                                   _OUT& argout, 
                                   std::string file = __FILE__, 
                                   int line= __LINE__)
			throw (Tango::DevFailed)
		{
			if (device_proxy_)
			{
				Tango::DeviceData dd_in;
				dd_in << const_cast<_IN&>(argin);
				_DEV_TRY_FILE_LINE
					(
  					//- try
  					dd_out_ = (device_proxy_->command_inout)(const_cast<std::string&>(cmd_name), dd_in),
  					//- what do we tried
  					std::string("command_inout on ") + FULL_CMD_NAME(cmd_name),
  					//- origin
  					"CommandInOutHelper::command_inout",
  					file,
  					line
					);
				_DEV_TRY_FILE_LINE
					(
  					//- try
  					dd_out_ >> argout,
  					//- what do we tried
  					std::string("DeviceData::operator>> on data returned by ") + FULL_CMD_NAME(cmd_name),
  					//- origin
  					"CommandInOutHelper::command_inout",
  					file,
  					line
					);
			}
		}
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#define command_inout internal_command_inout
#endif		
		//---------------------------------------------------------------------------
		//  CommandInOutHelper::command_inout
		//  exec a DEVVAR<X>STRINGARRAY/DEVVAR<X>STRINGARRAY command on the underlying device
		//  cmd_name : the name of the TANGO command
		//  _nv_in : numerical part of the input DEVVAR<X>STRINGARRAY
		//  _sv_in : string part of the input DEVVAR<X>STRINGARRAY
		//  _nv_out : numerical part of the ouput DEVVAR<X>STRINGARRAY
		//  _sv_out : string part of the ouput DEVVAR<X>STRINGARRAY
		//---------------------------------------------------------------------------
		//  template arg _IN must be supported by DeviceData::.insert
		//  template arg _OUT must be supported by DeviceData::.insert
		//---------------------------------------------------------------------------
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#undef command_inout	// Must avoid macro expansion 
#endif
		template <class _IN, class _OUT>
		void internal_command_inout (const std::string& cmd_name,
                              	 const std::vector<_IN>& _nv_in,
                              	 const std::vector<std::string>& _sv_in,
                              	 std::vector<_OUT>& _nv_out,
                              	 std::vector<std::string>& _sv_out,
                              	 std::string file= __FILE__,
                              	 int line= __LINE__)
			throw (Tango::DevFailed)
		{
			if (this->device_proxy_)
			{
				Tango::DeviceData dd_in;
				dd_in.insert(const_cast<std::vector<_IN>&>(_nv_in), 
					           const_cast<std::vector<std::string>&>(_sv_in));
				_DEV_TRY_FILE_LINE
					(
  					//- try
  					dd_out_ = (device_proxy_->command_inout)(const_cast<std::string&>(cmd_name), dd_in),
  					//- what do we tried
  					std::string("command_inout on ") + FULL_CMD_NAME(cmd_name),
  					//- origin
  					"CommandInOutHelper::command_inout",
  					file,
  					line
					);
				_DEV_TRY_FILE_LINE
					(
  					//- try
  					dd_out_.extract(_nv_out, _sv_out),
  					//- what do we tried
  					std::string("DeviceData::extract on data returned by ") + FULL_CMD_NAME(cmd_name),
  					//- origin
  					"CommandInOutHelper::command_inout",
  					file,
  					line
					);
			}
		}
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#define command_inout internal_command_inout
#endif
		//---------------------------------------------------------------------------
		//  CommandInOutHelper::command_inout
		//  Overloaded commands to  avoid usage of DevVarXX ARRAY for argout 
		//---------------------------------------------------------------------------
		template <class _IN>
			void internal_command_inout (const std::string& cmd_name, 
                                   const _IN& argin,
                                   Tango::DevVarDoubleStringArray* argout,
                                   std::string file = __FILE__,
                                   int line = __LINE__)
			throw (Tango::DevFailed)
		{
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#pragma message  (" TANGO WARNING ***** command_inout:Use only STL vector instead of DevVarDoubleStringArray *****")
#endif
			TangoSys_OMemStream o; 
			o << " [" << file << "::" << line << "]" << std::ends; 
			Tango::Except::throw_exception(static_cast<const char*>("TANGO_WRONG_DATA_ERROR"), 
				                             static_cast<const char*>("Use only STL vector instead of DevVarXXStringArray"),
				                             static_cast<const char*>(o.str().c_str()));
		}
		//---------------------------------------------------------------------------
		//  CommandInOutHelper::command_inout
		//  Overloaded commands to  avoid usage of DevVarXX ARRAY for argout 
		//---------------------------------------------------------------------------
		template <class _IN>
		void internal_command_inout (const std::string& cmd_name, 
                                 const _IN& argin, 
                                 Tango::DevVarLongStringArray* argout,
                                 std::string file = __FILE__, 
                                 int line = __LINE__)
		  throw (Tango::DevFailed)
		{
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#pragma message  (" TANGO WARNING ***** command_inout:Use only STL vector instead of DevVarLongStringArray *****")
#endif
			TangoSys_OMemStream o; 
			o << " [" << file << "::" << line << "]" << std::ends; 
			Tango::Except::throw_exception(static_cast<const char*>("TANGO_WRONG_DATA_ERROR"), 
				                             static_cast<const char*>("Use only STL vector instead of DevVarXXStringArray"),
				                             static_cast<const char*>(o.str().c_str()));
		}
		//---------------------------------------------------------------------------
		//  CommandInOutHelper::command_inout
		//  Overloaded commands to  avoid usage of DevVarXX ARRAY for argout 
		//---------------------------------------------------------------------------
		template <class _IN>
		void internal_command_inout (const std::string& cmd_name,
                                 const _IN& argin, 
                                 Tango::DevVarDoubleStringArray& argout,
                                 std::string file = __FILE__,
                                 int line = __LINE__)
			throw (Tango::DevFailed)
		{
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#pragma message  (" TANGO WARNING ***** command_inout:Use only STL vector instead of DevVarDoubleStringArray *****")
#endif
			TangoSys_OMemStream o; 
			o << " [" << file << "::" << line << "]" << std::ends; 
			Tango::Except::throw_exception(static_cast<const char*>("TANGO_WRONG_DATA_ERROR"), 
				                             static_cast<const char*>("Use only STL vector instead of DevVarXXStringArray"),
				                             static_cast<const char*>(o.str().c_str()));
		}
		
		//---------------------------------------------------------------------------
		//  CommandInOutHelper::command_inout
		//  Overloaded commands to  avoid usage of DevVarXX ARRAY for argout 
		//---------------------------------------------------------------------------
		template <class _IN>
		void internal_command_inout (const std::string& cmd_name, 
                                 const _IN& argin, 
                                 Tango::DevVarLongStringArray& argout,
                                 std::string file= __FILE__, 
                                 int line= __LINE__)
			throw (Tango::DevFailed)
		{
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#pragma message  (" TANGO WARNING ***** command_inout:Use only STL vector instead of DevVarLongStringArray *****")
#endif
			TangoSys_OMemStream o; 
			o << " [" << file << "::" << line << "]" << std::ends; 
			Tango::Except::throw_exception(static_cast<const char*>("TANGO_WRONG_DATA_ERROR"), 
			                             	 static_cast<const char*>("Use only STL vector instead of DevVarXXStringArray"),
				                             static_cast<const char*>(o.str().c_str()));
		}

		//---------------------------------------------------------------------------
		//  CommandInOutHelper::command_in
		//  exec a DEV_VOID/ARG_IN TANGO command on the underlying device
		//  cmd_name : the name of the TANGO command
		//  argin : input argument
		// dummy : used to have same number of parameter for the 2 command_in methods
		//---------------------------------------------------------------------------
		//  template arg _IN must be supported by DeviceData::operator<<
		//---------------------------------------------------------------------------
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#undef command_inout	// Must avoid macro expansion
#endif
		template <class _IN>
		void internal_command_in (const std::string& cmd_name,
                              const _IN& argin,
                              std::string file = __FILE__,
                              int line = __LINE__)
			throw (Tango::DevFailed)
		{
			if (this->device_proxy_)
			{
				Tango::DeviceData dd_in;
				dd_in << const_cast<_IN&>(argin);
				_DEV_TRY_FILE_LINE
					(
  					//- try
  					(device_proxy_->command_inout)(const_cast<std::string&>(cmd_name), dd_in),
  					//- what do we tried
  					std::string("command_inout on ") + FULL_CMD_NAME(cmd_name),
  					//- origin
  					"CommandInOutHelper::command_in",
  					file,
  					line
					);
			}
		}
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#define command_inout internal_command_inout
#endif
		//---------------------------------------------------------------------------
		//  CommandInOutHelper::command_in
		//  exec a DEV_VOID/DEVVAR<X>STRINGARRAY command on the underlying device
		//  cmd_name : the name of the TANGO command
		//  _nv_in   : numerical part of the input DEVVAR<X>STRINGARRAY
		//  _sv_in   : string part of the input DEVVAR<X>STRINGARRAY
		//---------------------------------------------------------------------------
		//  template arg _IN must be supported by DeviceData::.insert
		//---------------------------------------------------------------------------
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#undef command_inout	// Must avoid macro expansion 
#endif
		template <class _IN>
			void internal_command_in (const std::string& cmd_name, 
                          			const std::vector<_IN>& _nv_in, 
                          			const std::vector<std::string>& _sv_in, 
                                std::string file = __FILE__,
                                int line = __LINE__)
			throw (Tango::DevFailed)
		{
			if (this->device_proxy_)
			{
				Tango::DeviceData dd_in;
				dd_in.insert(const_cast<std::vector<_IN>&>(_nv_in), 
					           const_cast<std::vector<std::string>&>(_sv_in));
				_DEV_TRY_FILE_LINE
					(
  					//- try
  					(device_proxy_->command_inout)(const_cast<std::string&>(cmd_name), dd_in),
  					//- what do we tried
  					std::string("command_inout on ") + FULL_CMD_NAME(cmd_name),
  					//- origin
  					"CommandInOutHelper::command_in",
  					file,
  					line
					);
			}
		}
		
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#define command_inout internal_command_inout
#endif
		//---------------------------------------------------------------------------
		//  CommandInOutHelper::command_out
		//  exec a ARG_OUT/DEV_VOID TANGO command on the underlying device
		//  cmd_name : the name of the TANGO command
		//  argout : output argument 
		//---------------------------------------------------------------------------
		//  template arg _OUT must be supported by DeviceData::operator>>
		//---------------------------------------------------------------------------
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#undef command_inout	// Must avoid macro expansion 
#endif
		template <class _OUT>
			void internal_command_out (const std::string& cmd_name, 
                                 _OUT& argout,  
                                 std::string file = __FILE__, 
                                 int line = __LINE__)
			throw (Tango::DevFailed)
		{
			if (this->device_proxy_)
			{
				_DEV_TRY_FILE_LINE
					(
  					//- try
  					dd_out_ = (device_proxy_->command_inout)(const_cast<std::string&>(cmd_name)),
  					//- what do we tried
  					std::string("command_inout on ") + FULL_CMD_NAME(cmd_name),
  					//- origin
  					"CommandInOutHelper::command_out",
  					file,
  					line
					);
				_DEV_TRY_FILE_LINE
					(
  					//- try
  					dd_out_ >> argout,
  					//- what do we tried
  					std::string("DeviceData::operator>> on data returned by ") + FULL_CMD_NAME(cmd_name),
  					//- origin
  					"CommandInOutHelper::command_out",
  					file,
  					line
					);
			}
		}
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#define command_inout internal_command_inout
#endif
		
		//---------------------------------------------------------------------------
		//  CommandInOutHelper::command_out
		//  Overloaded commands to  avoid usage of DevVarDoubleStringArray ARRAY
		//---------------------------------------------------------------------------
		template <class _OUT>  
			void internal_command_out(_OUT dummy, 
                                Tango::DevVarDoubleStringArray* argout,
                                std::string file = __FILE__,
                                int line = __LINE__)
			throw (Tango::DevFailed)
		{
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#pragma message  (" TANGO WARNING ***** command_out:Use only STL vector instead of DevVarDoubleStringArray *****")
#endif
			TangoSys_OMemStream o; 
			o << " [" << file << "::" << line << "]" << std::ends;
			Tango::Except::throw_exception(static_cast<const char*>("TANGO_WRONG_DATA_ERROR"),
				                             static_cast<const char*>("Use only STL vector instead of DevVarXXStringArray"),
				                             static_cast<const char*>(o.str().c_str()));
		}
		//---------------------------------------------------------------------------
		//  CommandInOutHelper::command_out
		//  Overloaded commands to  avoid usage of DevVarLongStringArray ARRAY
		//---------------------------------------------------------------------------
		template <class _OUT>    
			void internal_command_out (_OUT dummy, 
                                 Tango::DevVarLongStringArray* argout,
                                 std::string file = __FILE__, 
                                 int line = __LINE__)
			throw (Tango::DevFailed)
		{
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#pragma message  (" TANGO WARNING ***** command_out:Use only STL vector instead of DevVarLongStringArray *****")
#endif
			TangoSys_OMemStream o; 
			o << " [" << file << "::" << line << "]" << std::ends; 
			Tango::Except::throw_exception(static_cast<const char*>("TANGO_WRONG_DATA_ERROR"), 
				                             static_cast<const char*>("Use only STL vector instead of DevVarXXStringArray"),
				                             static_cast<const char*>(o.str().c_str()));
		}
		//---------------------------------------------------------------------------
		//  CommandInOutHelper::command_out
		//  Overloaded commands to  avoid usage of DevVarDoubleStringArray ARRAY
		//---------------------------------------------------------------------------
		template <class _OUT> 
			void internal_command_out(_OUT dummy, 
                                Tango::DevVarDoubleStringArray& argout,
                                std::string file = __FILE__, 
                                int line = __LINE__)
			throw (Tango::DevFailed)
		{
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#pragma message  (" TANGO WARNING ***** command_out:Use only STL vector instead of DevVarDoubleStringArray *****")
#endif
			TangoSys_OMemStream o; 
			o << " [" << file << "::" << line << "]" << std::ends; 
			Tango::Except::throw_exception(static_cast<const char*>("TANGO_WRONG_DATA_ERROR"), 
				                             static_cast<const char*>("Use only STL vector instead of DevVarXXStringArray"),
				                             static_cast<const char*>(o.str().c_str()));
		}
		//---------------------------------------------------------------------------
		//  CommandInOutHelper::command_out
		//  Overloaded commands to  avoid usage of DevVarLongStringArray ARRAY
		//---------------------------------------------------------------------------
		template <class _OUT> 
			void internal_command_out (_OUT dummy, 
                                 Tango::DevVarLongStringArray& argout,
                                 std::string file = __FILE__, 
                                 int line = __LINE__)
			throw (Tango::DevFailed)
		{
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#pragma message  (" TANGO WARNING ***** command_out:Use only STL vector instead of DevVarLongStringArray *****")
#endif
			TangoSys_OMemStream o;
			o << " [" << file << "::" << line << "]" << std::ends; 
			Tango::Except::throw_exception(static_cast<const char*>("TANGO_WRONG_DATA_ERROR"), 
				                             static_cast<const char*>("Use only STL vector instead of DevVarXXStringArray"),
				                             static_cast<const char*>(o.str().c_str()));
		}
		//---------------------------------------------------------------------------
		//  CommandInOutHelper::command_in
		//  exec a DEV_VOID/DEVVAR<X>STRINGARRAY command on the underlying device
		//  cmd_name : the name of the TANGO command
		//  _nv_out : numerical part of the output DEVVAR<X>STRINGARRAY
		//  _sv_out : string part of the output DEVVAR<X>STRINGARRAY
		//---------------------------------------------------------------------------
		//  template arg _OUT must be supported by DeviceData::.extract
		//---------------------------------------------------------------------------
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#undef command_inout	// Must avoid macro expansion 
#endif
		template <class _OUT>
		void internal_command_out (const std::string& cmd_name,
                          		 std::vector<_OUT>& _nv_out,
                          		 std::vector<std::string>& _sv_out,
                          		 std::string file = __FILE__,
                          		 int line = __LINE__)
		  throw (Tango::DevFailed)
		{
			if (this->device_proxy_)
			{
				_DEV_TRY_FILE_LINE
					(
  					//- try
  					dd_out_ = (device_proxy_->command_inout)(const_cast<std::string&>(cmd_name)),
  					//- what do we tried
  					std::string("command_inout on ") + FULL_CMD_NAME(cmd_name),
  					//- origin
  					"CommandInOutHelper::command_out",
  					file,
  					line
					);
				_DEV_TRY_FILE_LINE
					(
  					//- try
  					dd_out_.extract(_nv_out, _sv_out),
  					//- what do we tried
  					std::string("DeviceData::extract on data returned by ") + FULL_CMD_NAME(cmd_name),
  					//- origin
  					"CommandInOutHelper::command_out" ,
  					file,
  					line
					);
			}
		}
#if (defined(_MSC_VER) && _MSC_VER < 1300)
#define command_inout internal_command_inout
#endif

private:
	//- placed here as a workaround due to CORBA::any_var limitations
	Tango::DeviceData dd_out_;
};


//=============================================================================
// CLASS: AttributeHelper
//=============================================================================
class YAT4TANGO_EXPORT AttributeHelper : public virtual HelperBase
{
public:
	//---------------------------------------------------------------------------
	//  AttributeHelper::AttributeHelper  (ctor)
	//  device_name : name of the target device
	//  client_device : reference to the client device (for logging purpose)
	//---------------------------------------------------------------------------
	AttributeHelper (const std::string& device_name, Tango::DeviceImpl *client_device = 0)
		: HelperBase(device_name, client_device)
	{
		da_out_.exceptions(Tango::DeviceAttribute::isempty_flag | Tango::DeviceAttribute::wrongtype_flag);
	}
	//---------------------------------------------------------------------------
	//  AttributeHelper::~AttributeHelper (dtor)
	//---------------------------------------------------------------------------
	virtual ~AttributeHelper ()
	{
		//- noop dtor
	}

	//---------------------------------------------------------------------------
	//  AttributeHelper::get_device_attribute
	//---------------------------------------------------------------------------
	Tango::DeviceAttribute get_device_attribute () 
	{
		return da_out_;
	}

	//---------------------------------------------------------------------------
	//  AttributeHelper::write_attribute
	//  writes the specified attribute
	//  attr_name : name of the TANGO attribute to be written
	//  attr_value : the attribute value
	//---------------------------------------------------------------------------
	//  template arg _VAL must be supported by DeviceAttribute::operator<<
	//---------------------------------------------------------------------------
	template <class _VAL>
	void internal_write_attribute (const std::string& attr_name, 
                                 const _VAL& attr_value,
                                 std::string file = __FILE__,
                                 int line = __LINE__)
	  throw (Tango::DevFailed)
	{
		if (this->device_proxy_)
		{
			Tango::DeviceAttribute da;
			da.set_name(const_cast<std::string&>(attr_name));
			da << const_cast<_VAL&>(attr_value);
			_DEV_TRY_FILE_LINE
				(
  				//- try
  				(device_proxy_->write_attribute)(da),
  				//- what do we tried
  				std::string("write_attribute on ") + FULL_ATTR_NAME(attr_name),
  				//- origin
  				"AttributeHelper::write_attribute",
  				file,
  				line
				);
		}
	}
	//---------------------------------------------------------------------------
	//  AttributeHelper::read_attribute
	//  reads the specified attribute
	//  attr_name : the name of the TANGO attribute to be read
	//  attr_value : the attribute value
	//---------------------------------------------------------------------------
	//  template arg _VAL must be supported by DeviceAttribute::operator>>
	//---------------------------------------------------------------------------
	template <class _VAL>
	void internal_read_attribute (const std::string& attr_name,
                                _VAL& attr_value,
                                std::string file = __FILE__,
                                int line = __LINE__)
		throw (Tango::DevFailed)
	{
		if (this->device_proxy_)
		{
			_DEV_TRY_FILE_LINE
				(
  				//- try
  				da_out_ = (device_proxy_->read_attribute)(const_cast<std::string&>(attr_name)),
  				//- what do we tried
  				std::string("read_attribute on ") + FULL_ATTR_NAME(attr_name),
  				//- origin
  				"AttributeHelper::read_attribute", 
  				file,
  				line
				);
			_DEV_TRY_FILE_LINE
				(
  				//- try
  				da_out_ >> attr_value,
  				//- what do we tried
  				std::string("DeviceAttribute::operator>> on data returned by ") + FULL_ATTR_NAME(attr_name),
  				//- origin
  				"AttributeHelper::read_attribute", 
  				file,
  				line
				);
		}
	}

	//---------------------------------------------------------------------------
	//  AttributeHelper::read_attribute_w
	//  reads the specified attribute and get its write value
	//  attr_name : the name of the TANGO attribute to be read
	//  w_attr_value : the write attribute value
	//---------------------------------------------------------------------------
	//  template arg _VAL must be supported by DeviceAttribute::operator>>
	//---------------------------------------------------------------------------
	template <class _VAL>
		void internal_read_attribute_w (const std::string& attr_name, 
                                    _VAL& w_attr_value,
                                    std::string file = __FILE__,
                                    int line = __LINE__)
		throw (Tango::DevFailed)
	{
		if (this->device_proxy_)
		{
			_DEV_TRY_FILE_LINE
				(
  				//- try
  				da_out_ = (device_proxy_->read_attribute)(const_cast<std::string&>(attr_name)),
  				//- what do we tried
  				std::string("read_attribute on ") + FULL_ATTR_NAME(attr_name),
  				//- origin
  				"AttributeHelper::read_attribute_w", 
  				file,
  				line
				);
			//- create an AttributeProxy to get the type of the attribute
			_DEV_TRY_FILE_LINE
				(
  				//- try
  				attr_proxy_ = new Tango::AttributeProxy(FULL_ATTR_NAME(attr_name)),
  				//- what do we tried
  				std::string("new Tango::AttributeProxy : ") + FULL_ATTR_NAME(attr_name),
  				//- origin
  				"AttributeHelper::read_attribute_w", 
  				file,
  				line
				);
			//- Switch on attribute type (to be completed with all tango types!)
			switch(attr_proxy_->get_config().data_type)
			{
		
			case 2://short
				{
					w_attr_value = da_out_.ShortSeq[1];
					break;
				}	
			case 3://long
				{
					w_attr_value = da_out_.LongSeq[1];
					break;
				}
			case 5://double
				{
					w_attr_value = da_out_.DoubleSeq[1];
					break;
				}
			//case 8:string ...
			}
			//- Delete the attribute proxy
			if(attr_proxy_)
			{
				delete attr_proxy_;
				attr_proxy_ = 0;
			}
		}
	}
	
private:
	//- placed here as a workaround due to CORBA::any_var limitations
	Tango::DeviceAttribute da_out_;
	Tango::AttributeProxy* attr_proxy_;
};

//=============================================================================
// CLASS: ThreadSafeDeviceProxyHelper
//=============================================================================
class YAT4TANGO_EXPORT ThreadSafeDeviceProxyHelper : public CommandInOutHelper, public AttributeHelper
{
public:
	//---------------------------------------------------------------------------
	//  ThreadSafeDeviceProxyHelper::ThreadSafeDeviceProxyHelper  (ctor)
	//  device_name : name of the target device
	//  client_device : reference to the client device (for logging purpose)
	//---------------------------------------------------------------------------
	ThreadSafeDeviceProxyHelper (const std::string& target_device_name, Tango::DeviceImpl *host_device = 0)
		: HelperBase(target_device_name, host_device),
		  CommandInOutHelper(target_device_name, host_device),
		  AttributeHelper(target_device_name, host_device)
	{
		//- noop ctor
	}
	//---------------------------------------------------------------------------
	//  ThreadSafeDeviceProxyHelper::~ThreadSafeDeviceProxyHelper (dtor)
	//---------------------------------------------------------------------------
	virtual ~ThreadSafeDeviceProxyHelper ()
	{
		//- noop dtor
	}
};

} //- namespace yat4tango

#endif // _THREAD_SAFE_DEVICE_PROXY_HELPER_H_
