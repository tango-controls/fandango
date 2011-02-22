/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_IPLUGINOBJECT_WITH_ATTR_H_
#define _YAT_IPLUGINOBJECT_WITH_ATTR_H_

#include <yat/plugin/IPlugInObject.h>
#include <yat/plugin/PlugInTypes.h>

namespace yat
{

  class YAT_DECL IPlugInObjectWithAttr : public yat::IPlugInObject
  {
  public:
    virtual void enumerate_attributes( yat::PlugInAttrInfoList& list) const
      throw (yat::Exception) = 0;

    virtual void enumerate_properties( yat::PlugInPropInfos& prop_infos ) const
      throw (yat::Exception) = 0;
    
    virtual void set_properties( yat::PlugInPropValues& prop_values )
      throw (yat::Exception) = 0;
  };

} // namespace

#endif
