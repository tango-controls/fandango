/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_IPLUGINFACTORY_H_
#define _YAT_IPLUGINFACTORY_H_

#include <yat/plugin/IPlugInObject.h>

namespace yat
{

typedef std::vector<std::string> PlugInObjectParams;

/**
  *  \brief Abtract interface for a Plugin factory
  */
class YAT_DECL IPlugInFactory
{
  friend class PlugInManager;

public:
  /**
    *  \brief Creates a plugin object
    *  \param[in,out] object a reference to a IPlugInObject pointer that will hold the adress of the created object
    *  \param[in] params a set of parameters to customize the object creation if necessary
    */
  virtual void create(IPlugInObject*& object,
                      const PlugInObjectParams& params = PlugInObjectParams()) = 0;
protected:
  IPlugInFactory();
  virtual ~IPlugInFactory();

private:
  IPlugInFactory(const IPlugInFactory&);
  IPlugInFactory& operator=(const IPlugInFactory&);
};

} // namespace

#endif
