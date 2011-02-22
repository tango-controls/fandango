/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _DYNAMIC_ATTR_H_
#define _DYNAMIC_ATTR_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <limits>
#include <yat4tango/CommonHeader.h>
#include <yat/DataBuffer.h>

namespace yat4tango
{


// ============================================================================
//
// static class: DynamicAttr
//
// ============================================================================
template <typename T>
class YAT_DECL DynamicAttr
{
public:
  /**
   * the Tango identifier of the data type (DEV_BOOLEAN, DEV_DOUBLE...)
   */
  static const long tango_type;

  /**
   * a dummy value of the type used to fill the attribute value at construction
   */
  static const T    dummy_value;
};

// ============================================================================
//
// class: DynamicScalarAttr
//
// ============================================================================
template <typename T>
class YAT_DECL DynamicScalarAttr : public Tango::Attr
{
public:
	//- ctor ---------------------------------
	DynamicScalarAttr (const std::string& _name,
                     Tango::AttrWriteType _w_type);

	//- dtor ---------------------------------
	virtual ~DynamicScalarAttr (void);

  //- read ---------------------------------
	virtual void read(Tango::DeviceImpl *dev, Tango::Attribute &att);

  //- write --------------------------------
	virtual void write(Tango::DeviceImpl *dev, Tango::WAttribute &att);

  //- is_allowed ---------------------------
  virtual bool is_allowed (Tango::DeviceImpl *dev, Tango::AttReqType ty);

  T content;
  T w_content;
  bool allowed;
};

// ============================================================================
//
// class: DynamicSpectrumAttr
//
// ============================================================================
template <typename T>
class YAT_DECL DynamicSpectrumAttr : public Tango::SpectrumAttr
{
public:
	//- ctor ---------------------------------
	DynamicSpectrumAttr (const std::string& _name,
                       Tango::AttrWriteType _w_type,
                       long max_x);

	//- dtor ---------------------------------
	virtual ~DynamicSpectrumAttr (void);

  //- read ---------------------------------
	virtual void read(Tango::DeviceImpl *dev, Tango::Attribute &att);

  //- write --------------------------------
	virtual void write(Tango::DeviceImpl *dev, Tango::WAttribute &att);

  //- is_allowed ---------------------------
  virtual bool is_allowed (Tango::DeviceImpl *dev, Tango::AttReqType ty);


  yat::Buffer<T> content;
  yat::Buffer<T> w_content;
  bool allowed;
};


// ============================================================================
//
// class: DynamicImageAttr
//
// ============================================================================
template <typename T>
class YAT_DECL DynamicImageAttr : public Tango::ImageAttr
{
public:
	//- ctor ---------------------------------
	DynamicImageAttr (const std::string& _name,
                    Tango::AttrWriteType _w_type,
                    long max_x,
                    long max_y);

	//- dtor ---------------------------------
	virtual ~DynamicImageAttr (void);

  //- read ---------------------------------
	virtual void read(Tango::DeviceImpl *dev, Tango::Attribute &att);

  //- write --------------------------------
	virtual void write(Tango::DeviceImpl *dev, Tango::WAttribute &att);

  //- is_allowed ---------------------------
  virtual bool is_allowed (Tango::DeviceImpl *dev, Tango::AttReqType ty);


  yat::ImageBuffer<T> content;
  yat::ImageBuffer<T> w_content;
  bool allowed;
};

} // namespace

#include <yat4tango/DynamicAttr.tpp>

#endif
