/*!
 * \file
 * \brief    
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
 */
#ifndef _YAT4TANGO_PLUGINATTR_TPP_
#define _YAT4TANGO_PLUGINATTR_TPP_



// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat4tango/PlugInAttr.h>

#if !defined (YAT_INLINE_IMPL)
# include "yat4tango/PlugInAttr.i"
#endif // __INLINE_IMPL___


namespace yat4tango
{
  //- fwd decl
  //long tango_type(int data_type);
  //Tango::AttrWriteType write_type(int write_type);

  template <typename T>
  PlugInAttr<T>::PlugInAttr(yat::PlugInAttrInfo info)
    : Tango::Attr(info.name.c_str(),
                  TangoType<T>::Value,
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

  template <typename T>
  PlugInAttr<T>::~PlugInAttr(void)
  {
  }

  template <typename T>
  void PlugInAttr<T>::read(Tango::DeviceImpl *, Tango::Attribute &att)
  {
    //- retrieve the value from the plugin :
    try
    {
      this->info_.get_cb( this->read_value );
      if (this->read_value.empty())
        THROW_DEVFAILED("NO_VALUE",
                        "No value has been assigned to the container",
                        "PlugInAttr<T>::read");
    }
    catch( yat::Exception& ex )
    {
      yat4tango::YATDevFailed df(ex);
      RETHROW_DEVFAILED(df,
                        "SOFTWARE_FAILURE",
                        "Error while reading a plugin attribute",
                        "PlugInAttr<T>::read");
    }
    catch( ... )
    {
      THROW_DEVFAILED("UNKNWON_ERROR",
                      "Unknwon error while reading a plugin attribute",
                      "PlugInAttr<T>::read");
    }

    //- assign it to the Tango::Attribute
    att.set_value( yat::any_cast<T>(&this->read_value) );
  }



  template <typename T>
  void PlugInAttr<T>::write(Tango::DeviceImpl *, Tango::WAttribute &att)
  {
    T write_value;
    att.get_write_value(write_value);

    yat::Any container(write_value);

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
                        "PlugInAttr<T>::read");
    }
    catch( ... )
    {
      THROW_DEVFAILED("UNKNWON_ERROR",
                      "Unknwon error while writing a plugin attribute",
                      "PlugInAttr<T>::read");
    }
  }

  template <typename T>
  bool PlugInAttr<T>::is_allowed (Tango::DeviceImpl *, Tango::AttReqType)
  {
    return (true);
  }






}

#endif
