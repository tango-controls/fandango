/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_GENERIC_CONTAINER_H_
#define _YAT_GENERIC_CONTAINER_H_

#include <yat/CommonHeader.h>

namespace yat 
{

// ============================================================================
//	class: Container
// ============================================================================
class YAT_DECL Container
{
public:
  Container ()
  {
    //- noop
  };

  virtual ~Container () 
  {
    //- noop
  };
};

// ============================================================================
//	template class: GenericContainer - class T must have a copy ctor
// ============================================================================
template <typename T> 
class GenericContainer : public Container
{
public:

  GenericContainer (T* _msg_data) : ptr_(_msg_data)
  {

  };

  GenericContainer (const T& _data) : ptr_(0)
  {
    try
    {
      ptr_ = new T(_data);
      if (ptr_ == 0)
        throw std::bad_alloc();
    }
    catch (const std::bad_alloc&)
    {
      ptr_ = 0;
      THROW_YAT_ERROR("OUT_OF_MEMORY",
                      "template class allocation failed",
                      "GenericContainer:GenericContainer");
    }
  };

  virtual ~GenericContainer ()
  {
    SAFE_DELETE_PTR(this->ptr_);
  };

  //- returns content and optionaly transfers ownership to caller
  T * content (bool transfer_ownership = true)
  {
    T * tmp = this->ptr_;
    if (transfer_ownership)
      this->ptr_ = 0;
    return tmp;
  };

private:
  //- actual container content
  T * ptr_;
};


// ============================================================================
//	template function
// ============================================================================
template <typename T> T * extract_data (Container * _c, 
                                        bool _transfer_ownership = true)
    throw (Exception)
{
  GenericContainer<T> * gc = 0;

  try
  {
    gc = dynamic_cast<GenericContainer<T>*>(_c);
    if (gc == 0)
  	{
      THROW_YAT_ERROR("RUNTIME_ERROR",
                      "could not extract data from Container [unexpected content]",
                      "dettach_data");
  	}
  }
  catch (const std::bad_cast&)
  {
    THROW_YAT_ERROR("RUNTIME_ERROR",
                    "could not extract data from Container [unexpected content]",
                    "dettach_data");
  }

  return gc->content(_transfer_ownership);
}

} // namespace yat

#endif



