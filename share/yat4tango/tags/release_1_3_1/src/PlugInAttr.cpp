// ============================================================================
//
// = CONTEXT
//    TANGO Project - ImgBeamAnalyzer DeviceServer - Data class
//
// = File
//    Data.cpp
//
// = AUTHOR
//    Julien Malik
//
// ============================================================================

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat4tango/PlugInAttr.h>

namespace yat4tango
{

  Tango::AttrWriteType TangoWriteType::operator()(int plugin_write_type)
  {
    switch (plugin_write_type)
    {
    case yat::PlugInAttrWriteType::READ       : return Tango::READ;
    case yat::PlugInAttrWriteType::WRITE      : return Tango::WRITE;
    case yat::PlugInAttrWriteType::READ_WRITE : return Tango::READ_WRITE;
    default: THROW_DEVFAILED("SOFTWARE_FAILURE",
                             "Unsupported write type",
                             "write_type");
    }
    return Tango::READ; // keep compiler happy
  };



  PlugInAttr<std::string>::PlugInAttr(yat::PlugInAttrInfo info)
    : Tango::Attr(info.name.c_str(),
                  TangoType<std::string>::Value,
                  TangoWriteType()(info.write_type)),
      info_(info)
  {
    Tango::UserDefaultAttrProp	prop;
    prop.set_label        (info.label.c_str());
    prop.set_unit         (info.unit.c_str());
    prop.set_standard_unit(info.unit.c_str());
    prop.set_display_unit (info.unit.c_str());
    prop.set_description  (info.desc.c_str());
    prop.set_format       (info.display_format.c_str());
    this->set_default_properties(prop);
  }

  PlugInAttr<std::string>::~PlugInAttr(void)
  {
  }

  void PlugInAttr<std::string>::read(Tango::DeviceImpl *, Tango::Attribute &att)
  {
    //- retrieve the value from the plugin :
    try
    {
      this->info_.get_cb( this->read_value );
      if (this->read_value.empty())
        THROW_DEVFAILED("NO_VALUE",
                        "No value has been assigned to the container",
                        "PlugInAttr<std::string>::read");
    }
    catch( yat::Exception& ex )
    {
      yat4tango::YATDevFailed df(ex);
      RETHROW_DEVFAILED(df,
                        "SOFTWARE_FAILURE",
                        "Error while reading a plugin attribute",
                        "PlugInAttr<std::string>::read");
    }
    catch( ... )
    {
      THROW_DEVFAILED("UNKNWON_ERROR",
                      "Unknwon error while reading a plugin attribute",
                      "PlugInAttr<std::string>::read");
    }

    this->read_ptr = const_cast<char*>( (yat::any_cast<std::string>(&this->read_value))->c_str() );
    att.set_value( &this->read_ptr );
  }

  void PlugInAttr<std::string>::write(Tango::DeviceImpl *, Tango::WAttribute &att)
  {
    char* write_value;
    att.get_write_value(write_value);
    std::string write_value_string(write_value);
    yat::Any container(write_value_string);

    try
    {
      this->info_.set_cb(container);
    }
    catch( yat::Exception& ex )
    {
      yat4tango::YATDevFailed df(ex);
      RETHROW_DEVFAILED(df,
                        "SOFTWARE_FAILURE",
                        "Error while writing a plugin attribute",
                        "PlugInAttr<std::string>::write");
    }
    catch( ... )
    {
      THROW_DEVFAILED("UNKNWON_ERROR",
                      "Unknwon error while writing a plugin attribute",
                      "PlugInAttr<std::string>::write");
    }
  }

  bool PlugInAttr<std::string>::is_allowed (Tango::DeviceImpl *, Tango::AttReqType)
  {
    return (true);
  }


}
