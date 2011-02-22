/*!
 * \file
 * \brief    
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
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
