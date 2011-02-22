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
 * \authors N.Leclercq, J.Malik - Synchrotron SOLEIL
 */

namespace yat4tango
{

// ============================================================================
// DynamicAttrHelper::begin
// ============================================================================
YAT_INLINE
DynAttrCIt
DynamicAttrHelper::begin() const
{
  return this->rep_.begin();
};

// ============================================================================
// DynamicAttrHelper::begin
// ============================================================================
YAT_INLINE
DynAttrIt
DynamicAttrHelper::begin()
{
  return this->rep_.begin();
};

// ============================================================================
// DynamicAttrHelper::end
// ============================================================================
YAT_INLINE
DynAttrCIt
DynamicAttrHelper::end() const
{
  return this->rep_.end();
};

// ============================================================================
// DynamicAttrHelper::end
// ============================================================================
YAT_INLINE
DynAttrIt
DynamicAttrHelper::end()
{
  return this->rep_.end();
};

// ============================================================================
// DynamicAttrHelper::size
// ============================================================================
YAT_INLINE
size_t
DynamicAttrHelper::size() const
{
  return this->rep_.size();
};

// ============================================================================
// DynamicAttrHelper::empty
// ============================================================================
YAT_INLINE
bool
DynamicAttrHelper::empty() const
{
  return this->rep_.empty();
};


} //- namespace
