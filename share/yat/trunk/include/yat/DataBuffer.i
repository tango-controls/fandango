/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

namespace yat
{

// ============================================================================
// Buffer::clear
// ============================================================================
template <class T>
YAT_INLINE void Buffer<T>::clear (void)
{
  ::memset(this->base_, 0,  this->capacity_ * sizeof(T));
}

// ============================================================================
// Buffer::elem_size
// ============================================================================
template <class T>
YAT_INLINE size_t Buffer<T>::elem_size (void) const
{
  return sizeof(T);
}

// ============================================================================
// Buffer::length
// ============================================================================
template <class T>
YAT_INLINE size_t Buffer<T>::length (void) const
{
  return this->length_;
}

// ============================================================================
// Buffer::force_length
// ============================================================================
template <class T>
YAT_INLINE void Buffer<T>::force_length (size_t _new_length)
{
  if (_new_length > this->capacity_)
    this->length_ = this->capacity_;
  else
    this->length_ = _new_length;
}

// ============================================================================
// Buffer::capacity
// ============================================================================
template <class T>
YAT_INLINE size_t Buffer<T>::capacity (void) const
{
  return this->capacity_;
}

// ============================================================================
// Buffer::empty
// ============================================================================
template <class T>
YAT_INLINE bool Buffer<T>::empty (void) const
{
  return this->length_ == 0;
}

// ============================================================================
// Buffer::base
// ============================================================================
template <class T>
YAT_INLINE T * Buffer<T>::base (void) const
{
  return this->base_;
}

// ============================================================================
// Buffer::operator[]
// ============================================================================
template <class T>
YAT_INLINE T& Buffer<T>::operator[] (size_t _indx)
{
  /* !! no bound error check !!*/
  return this->base_[_indx];
}

// ============================================================================
// Buffer::operator[] const
// ============================================================================
template <class T>
YAT_INLINE const T& Buffer<T>::operator[] (size_t _indx) const
{
  /* !! no bound error check !!*/
  return this->base_[_indx];
}

// ============================================================================
// Buffer::size
// ============================================================================
template <class T>
YAT_INLINE size_t Buffer<T>::size (void) const
{
	return this->length_ * sizeof(T);
}

// ============================================================================
// Buffer::fill
// ============================================================================
template <class T>
YAT_INLINE void Buffer<T>::fill (const T& _val)
{
  *this = _val;
}

// ============================================================================
// Buffer::operator=
// ============================================================================
template <class T>
YAT_INLINE Buffer<T>& Buffer<T>::operator= (const Buffer<T>& src)
{
  if (&src == this)
    return *this;
    
  if (this->capacity_ < src.length_)
    this->capacity(src.length_);
    
  ::memcpy(this->base_, src.base_, src.length_ * sizeof(T));
  
  this->length_ = src.length_;
  
  return *this;
}

// ============================================================================
// Buffer::operator=
// ============================================================================
template <class T>
YAT_INLINE Buffer<T>& Buffer<T>::operator= (const T* _src)
{
  if (_src == this->base_)
    return *this;
    
  ::memcpy(this->base_, _src, this->capacity_ * sizeof(T));
  
  this->length_ = this->capacity_;   
  
  return *this;
}

// ============================================================================
// Buffer::operator=
// ============================================================================
template <class T>
YAT_INLINE Buffer<T>& Buffer<T>::operator= (const T& _val)
{
  for (size_t i = 0; i < this->capacity_; i++)
     *(this->base_ + i) = _val;
  
  this->length_ = this->capacity_;   
 
  return *this;
}

// ======================================================================
// ImageBuffer::width
// ======================================================================
template <class T>
YAT_INLINE size_t ImageBuffer<T>::width (void) const
{
  return this->width_;
}

// ======================================================================
// ImageBuffer::height
// ======================================================================
template <class T> YAT_INLINE size_t ImageBuffer<T>::height (void) const
{
  return this->height_;
}

// ======================================================================
// ImageBuffer::set_dimensions
// ======================================================================
template <class T>
YAT_INLINE void ImageBuffer<T>::set_dimensions (size_t _width, size_t _height)
{
  this->capacity(_width * _height);
  this->force_length(_width * _height);
  this->width_  = _width;
  this->height_ = _height;
}

// ======================================================================
// ImageBuffer::operator=
// ======================================================================
template <class T>
YAT_INLINE ImageBuffer<T> & ImageBuffer<T>::operator= (const ImageBuffer<T> &_src)
{
  if (&_src == this)
    return *this;
    
  this->Buffer<T>::operator =(_src);
  
  this->width_  = _src.width_;
  this->height_ = _src.height_;
  
  return *this;
}

// ======================================================================
// ImageBuffer::operator=
// ======================================================================
template <class T>
YAT_INLINE ImageBuffer<T> & ImageBuffer<T>::operator= (const T *base)
{
  Buffer<T>::operator=(base);
  
  return *this;
}

// ======================================================================
// ImageBuffer::operator=
// ======================================================================
template <class T>
YAT_INLINE ImageBuffer<T> & ImageBuffer<T>::operator= (const T &val)
{
  this->fill(val);
  
  return *this;
}

} // namespace
