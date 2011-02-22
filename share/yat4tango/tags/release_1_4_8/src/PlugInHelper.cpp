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

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat4tango/PlugInHelper.h>
#include <yat4tango/PlugInAttr.h>

//=============================================================================
// INLINED CODE
//=============================================================================
#if !defined (YAT_INLINE_IMPL)
# include "yat4tango/PlugInHelper.i"
#endif // __INLINE_IMPL__


namespace yat4tango
{

  PlugInHelper::PlugInHelper(Tango::DeviceImpl * _host_device)
    : host_device_(_host_device),
      dyn_attr_h_(_host_device)
  {
  }

  PlugInHelper::~PlugInHelper()
  {
  }

  void PlugInHelper::register_plugin( yat::IPlugInObjectWithAttr* object )
  {
    this->register_properties( object );
    this->register_attributes( object );
  }

  void PlugInHelper::register_properties( yat::IPlugInObjectWithAttr* object )
  {
    //- get the list of properties that the plug-in wants
    yat::PlugInPropInfos prop_infos;
    try
    {
      object->enumerate_properties(prop_infos);
    }
    catch(yat::Exception& ex)
    {
      RETHROW_YAT_ERROR(ex,
                        "SOFTWARE_FAILURE",
                        "Error while enumerating plugin properties",
                        "PlugInHelper::register_properties");
    }
    catch(...)
    {
      THROW_YAT_ERROR("UNKNOWN_ERROR",
                      "Error while enumerating plugin properties",
                      "PlugInHelper::register_properties");
    }

    if ( prop_infos.empty() )
    {
      return;
    }

    //- create the corresponding Tango::DbData
    yat::PlugInPropInfos::const_iterator in_it;
    Tango::DbData property_query;
    std::insert_iterator<Tango::DbData> out_it(property_query, property_query.begin());
    for (in_it = prop_infos.begin(); in_it != prop_infos.end(); ++in_it)
    {
      *out_it = Tango::DbDatum( (*in_it).first );
    }
    
    //- fill in the Tango::DbData
    try
    {
      this->host_device_->get_db_device()->get_property(property_query);
    }
    catch(Tango::DevFailed& df)
    {
      TangoYATException ex(df);
      RETHROW_YAT_ERROR(ex,
                        "SOFTWARE_FAILURE",
                        "Error while enumerating plugin properties",
                        "PlugInHelper::register_properties");
    }
    catch(...)
    {
      THROW_YAT_ERROR("UNKNOWN_ERROR",
                      "Error while enumerating plugin properties",
                      "PlugInHelper::register_properties");
    }



    //- extract the value from the Tango::DbData and copy them to a yat::PlugInPropValues
    yat::PlugInPropValues prop_values;
    Tango::DbData::iterator property_query_it;
    try
    {
      for ( property_query_it = property_query.begin();
            property_query_it != property_query.end();
            ++property_query_it )
      {
        std::string prop_name = (*property_query_it).name;

#       define YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( TYPEID, TYPE )                      \
        case TYPEID:                                                                \
          {                                                                         \
            if ( !(*property_query_it).is_empty() )                                 \
            {                                                                       \
              TYPE value;                                                           \
              (*property_query_it) >> value;                                        \
              prop_values[prop_name] = value;                                       \
            }                                                                       \
          }                                                                         \
          break;

        switch (prop_infos[prop_name])
        {
#if defined(__64BITS_PLATFORM__)
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::BOOLEAN ,       bool);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::UINT8 ,         yat_uint8_t);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::INT16 ,         yat_int16_t);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::UINT16 ,        yat_uint16_t);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::INT32 ,         yat_int32_t);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::UINT32 ,        yat_uint32_t);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::FLOAT ,         float);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::DOUBLE ,        double);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::STRING ,        std::string);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::STRING_VECTOR , std::vector<std::string>);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::INT16_VECTOR ,  std::vector<yat_int16_t>);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::UINT16_VECTOR , std::vector<yat_uint16_t>);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::INT32_VECTOR ,  std::vector<yat_int32_t>);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::UINT32_VECTOR , std::vector<yat_uint32_t>);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::FLOAT_VECTOR ,  std::vector<float>);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::DOUBLE_VECTOR , std::vector<double>);
          default: THROW_DEVFAILED("SOFTWARE_FAILURE","Unsupported property type","PlugInHelper::register_plugin");
#else
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::BOOLEAN ,       bool);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::UINT8 ,         unsigned char);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::INT16 ,         short);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::UINT16 ,        unsigned short);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::INT32 ,         long);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::UINT32 ,        unsigned long);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::FLOAT ,         float);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::DOUBLE ,        double);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::STRING ,        std::string);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::STRING_VECTOR , std::vector<std::string>);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::INT16_VECTOR ,  std::vector<short>);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::UINT16_VECTOR , std::vector<unsigned short>);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::INT32_VECTOR ,  std::vector<long>);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::UINT32_VECTOR , std::vector<unsigned long>);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::FLOAT_VECTOR ,  std::vector<float>);
          YAT4TANGO_PUSH_PLUGIN_PROP_TYPE( yat::PlugInPropType::DOUBLE_VECTOR , std::vector<double>);
          default: THROW_DEVFAILED("SOFTWARE_FAILURE","Unsupported property type","PlugInHelper::register_plugin");
#endif
        }
      }
    }
    catch(yat::Exception& ex)
    {
      RETHROW_YAT_ERROR(ex,
                        "SOFTWARE_FAILURE",
                        "Error while getting properties from database",
                        "PlugInHelper::register_properties");
    }
    catch(Tango::DevFailed& df)
    {
      TangoYATException ex(df);
      RETHROW_YAT_ERROR(ex,
                        "SOFTWARE_FAILURE",
                        "Error while getting properties from database",
                        "PlugInHelper::register_properties");
    }
    catch(...)
    {
      THROW_YAT_ERROR("UNKNOWN_ERROR",
                      "Error while getting properties from database",
                      "PlugInHelper::register_properties");
    }

    //- send the list filled with the values to the plugin
    try
    {
      object->set_properties( prop_values );
    }
    catch(yat::Exception& ex)
    {
      RETHROW_YAT_ERROR(ex,
                        "SOFTWARE_FAILURE",
                        "Error while setting properties of plugin",
                        "PlugInHelper::register_properties");
    }
    catch(...)
    {
      THROW_YAT_ERROR("UNKNOWN_ERROR",
                      "Error while setting properties of plugin",
                      "PlugInHelper::register_properties");
    }
  }


  void PlugInHelper::register_attributes( yat::IPlugInObjectWithAttr* object )
  {

    yat::PlugInAttrInfoList attr_list;
    try
    {
      object->enumerate_attributes( attr_list );
    }
    catch(yat::Exception& ex)
    {
      RETHROW_YAT_ERROR(ex,
                        "SOFTWARE_FAILURE",
                        "Error while enumerating plugin attributes",
                        "PlugInHelper::register_attributes");
    }
    catch(...)
    {
      THROW_YAT_ERROR("UNKNOWN_ERROR",
                      "Error while enumerating plugin attributes",
                      "PlugInHelper::register_attributes");
    }


    if (attr_list.empty())
    {
      return;
    }

    yat::PlugInAttrInfoList::iterator it;
    for (it = attr_list.begin(); it != attr_list.end(); it++)
    {
      switch ( (*it).data_type )
      {
#if defined(__64BITS_PLATFORM__)
      case yat::PlugInDataType::BOOLEAN:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<bool>(*it) );
        break;
      case yat::PlugInDataType::UINT8:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<uint8_t>(*it) );
        break;
      case yat::PlugInDataType::INT16:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<int16_t>(*it) );
        break;
      case yat::PlugInDataType::UINT16:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<uint16_t>(*it) );
        break;
      case yat::PlugInDataType::INT32:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<int32_t>(*it) );
        break;
      case yat::PlugInDataType::UINT32:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<uint32_t>(*it) );
        break;
      case yat::PlugInDataType::FLOAT:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<float>(*it) );
        break;
      case yat::PlugInDataType::DOUBLE:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<double>(*it) );
        break;
      case yat::PlugInDataType::STRING:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<std::string>(*it) );
        break;
#else
      case yat::PlugInDataType::BOOLEAN:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<bool>(*it) );
        break;
      case yat::PlugInDataType::UINT8:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<unsigned char>(*it) );
        break;
      case yat::PlugInDataType::INT16:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<short>(*it) );
        break;
      case yat::PlugInDataType::UINT16:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<unsigned short>(*it) );
        break;
      case yat::PlugInDataType::INT32:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<long>(*it) );
        break;
      case yat::PlugInDataType::UINT32:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<unsigned long>(*it) );
        break;
      case yat::PlugInDataType::FLOAT:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<float>(*it) );
        break;
      case yat::PlugInDataType::DOUBLE:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<double>(*it) );
        break;
      case yat::PlugInDataType::STRING:
        this->dyn_attr_h_.add_attribute( new PlugInAttr<std::string>(*it) );
        break;
#endif
      }
    }
  }
}
