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
#include <yat4tango/MonitoredAttribute.h>

namespace yat4tango
{

// ======================================================================
// MonitoredAttribute::MonitoredAttribute
// ======================================================================
//template <class T>
MonitoredAttribute::MonitoredAttribute ()
	:	_has_error(false)
{

}

// ======================================================================
// MonitoredAttribute::~MonitoredAttribute
// ======================================================================
MonitoredAttribute::~MonitoredAttribute ()
{

}

// ======================================================================
// MonitoredAttribute::set_value
// ======================================================================
void MonitoredAttribute::set_value (const Tango::DeviceAttribute& value)
{
  yat::AutoMutex<yat::Mutex> guard(_lock);
  this->_val = value;
  this->_has_error = false;
  this->_error.errors.length(0);
}

// ======================================================================
// MonitoredAttribute::set_error
// ======================================================================
void MonitoredAttribute::set_error (const Tango::DevFailed& df)
{
	yat::AutoMutex<yat::Mutex> guard(_lock);
	this->_error = df;
	this->_has_error = true;
}

}	//- namespace


