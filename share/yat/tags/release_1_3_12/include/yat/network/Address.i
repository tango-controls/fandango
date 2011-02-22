//----------------------------------------------------------------------------
// YAT LIBRARY
//----------------------------------------------------------------------------
//
// Copyright (C) 2006-2009  The Tango Community
//
// Part of the code comes from the ACE Framework
// see http://www.cs.wustl.edu/~schmidt/ACE.html for more about ACE
//
// The thread native implementation has been initially inspired by omniThread
// - the threading support library that comes with omniORB. 
// see http://omniorb.sourceforge.net/ for more about omniORB.
//
// Contributors form the TANGO community:
// Ramon Sunes (ALBA) 
//
// The YAT library is free software; you can redistribute it and/or modify it 
// under the terms of the GNU General Public License as published by the Free 
// Software Foundation; either version 2 of the License, or (at your option) 
// any later version.
//
// The YAT library is distributed in the hope that it will be useful,
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
 * \file    Address.i
 * \brief   Inlined code of the YAT network address class.
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

namespace yat
{

// ============================================================================
// Address::get_host_name
// ============================================================================
YAT_INLINE const std::string & Address::get_host_name (void) const
{
  YAT_TRACE("Address::get_host_name");

  return this->m_host_name;
} 

// ============================================================================
// Address::get_ip_address
// ============================================================================
YAT_INLINE const std::string & Address::get_ip_address (void) const
{
  YAT_TRACE("Address::get_ip_address");

  return this->m_ip_addr;
} 

// ============================================================================
// Address::get_port_number
// ============================================================================
YAT_INLINE size_t Address::get_port_number (void) const
{
  YAT_TRACE("Address::get_port_number");

  return this->m_port;
} 

} // namespace
