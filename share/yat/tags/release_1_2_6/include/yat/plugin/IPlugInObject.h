/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_IPLUGINOBJECT_H_
#define _YAT_IPLUGINOBJECT_H_

#include <yat/NonCopyable.h>

namespace yat
{

  class YAT_DECL IPlugInObject : private yat::NonCopyable
  {
  public:
    virtual ~IPlugInObject();

  protected:
    IPlugInObject();
  };

} // namespace

#endif
