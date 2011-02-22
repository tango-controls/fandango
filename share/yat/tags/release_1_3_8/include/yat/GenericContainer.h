/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_GENERIC_CONTAINER_H_
#define _YAT_GENERIC_CONTAINER_H_

#include <typeinfo>
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

  //- default ctor
  GenericContainer () 
    : ptr_(0), own_(false) 
  {
    //- noop
  }

  //- ctor - no copy
  //- just point to <_data> - <_ownership> will tell us...
  GenericContainer (T* _data, bool _ownership = true) 
    : ptr_(0), own_(_ownership) 
  {
    *this = _data;
  }

  //- ctor - copy - ownership set to true
  GenericContainer (const T& _data) 
    : ptr_(0), own_(false)
  {
    *this = _data;
  }

  //- copy ctor  - copy - ownership set to true
  GenericContainer (const GenericContainer<T>& _src) 
    : ptr_(0), own_(false)
  {
    *this = _src;
  }

  //- dtor - delete dat according to ownership flag
  virtual ~GenericContainer ()
  {
    if (own_)
      delete this->ptr_;
  }

  //- changes content - make a copy and set ownership to true
  const GenericContainer& operator= (const GenericContainer<T>& _src)
  {
    if (&_src == this)
      return;
    if (own_)
      delete this->ptr_;
    try
    {
      this->ptr_ = new (std::nothrow) T(_src.content());
      if (this->ptr_ == 0)
        throw std::bad_alloc();
    }
    catch (const std::bad_alloc&)
    {
      this->ptr_ = 0;
      own_ = false;
      THROW_YAT_ERROR("OUT_OF_MEMORY",
                      "memory allocation failed",
                      "GenericContainer:operator=");
    }
    own_ = true;
  }

  //- changes content - make a copy and set ownership to true
  const GenericContainer& operator= (const T& _src)
  {
    if (own_)
      delete this->ptr_;
    try
    {
      this->ptr_ = new (std::nothrow) T(_src);
      if (this->ptr_ == 0)
        throw std::bad_alloc();
    }
    catch (const std::bad_alloc&)
    {
      this->ptr_ = 0;
      own_ = false;
      THROW_YAT_ERROR("OUT_OF_MEMORY",
                      "memory allocation failed",
                      "GenericContainer:operator=");
    }
    own_ = true;
  }

  //- changes content but does not change ownership
  const GenericContainer& operator= (T* _data)
  {
    if (_data == ptr_)
      return;
    if (own_)
      delete this->ptr_;
    this->ptr_ = _data;
  }

  //- changes content and set ownership
  void content (T* _data, bool _ownership = true)
  {
    *this = _data;
    own_ = _ownership;
  }

  //- changes content (makes a copy)
  void content (T& _data)
  {
    *this = _data;
    own_ = true;
  }

  //- returns content 
  //- optionally transfers data ownership to the caller
  T * content (bool transfer_ownership)
  {
    T * tmp = this->ptr_;
    if (transfer_ownership)
    {
      this->own_ = false;
      this->ptr_ = 0;
    }
    return tmp;
  }

  //- returns content
  T & content ()
  {
    return  *(this->ptr_);
  }

  //- does this container have ownership of the underlying data?
  bool ownership () const
  {
    return this->own_;
  }
  
  //- changes data ownership
  void ownership (bool own)
  {
    this->own_ = own;
  }

private:
  //- actual container content
  T * ptr_;
  //- data ownership 
  bool own_;
};

/*
// ============================================================================
//	extract_data: standalone template function
// ============================================================================
template <typename T> T * extract_data (Container * _c, 
                                        bool _transfer_ownership = true)
    //- throw (Exception)
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
*/
} // namespace yat

#endif



