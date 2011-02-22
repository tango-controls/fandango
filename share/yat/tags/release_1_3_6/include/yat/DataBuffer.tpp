/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _DATA_BUFFER_TPP_
#define _DATA_BUFFER_TPP_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat/DataBuffer.h>

#if !defined (YAT_INLINE_IMPL)
# include <yat/DataBuffer.i>
#endif // YAT_INLINE_IMPL

namespace yat 
{

// ===========================================================================
// Buffer::Buffer
// ============================================================================
template <typename T>
Buffer<T>::Buffer (size_t _capacity, bool _clear)
 : base_(0), capacity_(0), length_(0)
{
  //- allocate the buffer 
  this->capacity(_capacity);
  
  //- reset content 
  if (_clear)
    this->clear();
}

// ============================================================================
// Buffer::Buffer
// ============================================================================
template <typename T>
Buffer<T>::Buffer (size_t _length, T* _base) 
 : base_(0), capacity_(0), length_(0)
{
  //- allocate the buffer 
  this->capacity(_length);
    
  ::memcpy(this->base_, _base, _length * sizeof(T));
 
  this->length_ = _length;
}

// ============================================================================
// Buffer::Buffer
// ============================================================================
template <typename T> 
Buffer<T>::Buffer (const Buffer<T>& _src)
 : base_(0), capacity_(0), length_(0)
{
  //- allocate the buffer 
  this->capacity(_src.capacity());
  
  //- copy from source to destination using <Buffer::operator=>.
  *this = _src;
}

// ============================================================================
// Buffer::~Buffer
// ============================================================================
template <typename T> 
Buffer<T>::~Buffer(void)
{
  SAFE_DELETE_ARRAY(this->base_);
  this->capacity_ = 0;
  this->length_ = 0;
}

// ============================================================================
// Buffer::capacity
// ============================================================================
template <typename T> 
void Buffer<T>::capacity (size_t _new_capacity, bool _keep_content)
{
  //- special case: do (almost) nothing
  if (this->capacity_ == _new_capacity)
  {
    if (! _keep_content)
       this->length_ = 0;
    return;
  }

  //- special case: null capacity
  if (_new_capacity == 0)
  {
    SAFE_DELETE_ARRAY(this->base_); 
    this->capacity_ = 0;
    this->length_ = 0;
    return;
  }

  //- allocate the buffer
  T* new_base = 0;
  try
  {
    new_base = new T[_new_capacity];
    if (new_base == 0)
      throw std::bad_alloc();
  }
  catch (std::bad_alloc&)
  {
    THROW_YAT_ERROR("OUT_OF_MEMORY", "memory allocation failed", "Buffer<T>::capacity");
  }
  catch (...)
  {
    THROW_YAT_ERROR("UNKNOWN_ERROR", "memory allocation failed", "Buffer<T>::capacity");
  }

  //- do we have to maintain the buffer content
  if (_keep_content && this->length_)
  {
    size_t copy_length = (this->length_ > _new_capacity) ? _new_capacity : this->length_;
    
    ::memcpy(new_base, this->base_, copy_length * sizeof(T));
    
    this->length_ = copy_length;
  }
  else
  {
    this->length_ = 0;
  }
  
  SAFE_DELETE_ARRAY(this->base_); 
  
  this->base_ = new_base;

  this->capacity_ = _new_capacity;
}

// ============================================================================
// Class : ImageBuffer
// ============================================================================
// ======================================================================
// ImageBuffer::ImageBuffer
// ======================================================================
template <typename T>
ImageBuffer<T>::ImageBuffer (size_t _width, size_t _height)
: Buffer<T>(_width * _height, true),
  width_(_width),
  height_(_height)
{
  this->force_length(_width * _height);
}

// ======================================================================
// ImageBuffer::ImageBuffer
// ======================================================================
template <typename T>
ImageBuffer<T>::ImageBuffer (size_t _width, size_t _height, T *base) 
: Buffer<T>(_width * _height, base),
  width_(_width),
  height_(_height)
{
}

// ======================================================================
// ImageBuffer::ImageBuffer
// ======================================================================
template <typename T>
ImageBuffer<T>::ImageBuffer (const ImageBuffer<T>& im)
: Buffer<T>(im),
  width_(im.width_),
  height_(im.height_)
{
}

// ======================================================================
// ImageBuffer::~ImageBuffer
// ======================================================================
template <typename T>
ImageBuffer<T>::~ImageBuffer (void)
{
 //- noop dtor
}

// ======================================================================
// ImageBuffer<T>::resize
// ======================================================================
template <typename T>
void ImageBuffer<T>::resize (size_t new_width, size_t new_height)
{
#ifndef min
#  define min(a,b) ( ((a) < (b)) ? (a) : (b) )
#  define YAT_DEFINED_MIN
#endif

  T* new_base = new T[new_width * new_height];
  size_t h;
  for (h = 0; h < min(height_, new_height); h++)
  {
    std::copy( this->base_ + h * width_,
               this->base_ + h * width_ + min(width_, new_width),
               new_base + h * new_width );
    if (new_width > width_)
    {
      std::fill( new_base + h * new_width + width_,
                 new_base + h * new_width + new_width,
                 T() );
    }
  }
  if (new_height > height_)
  {
    std::fill( new_base + height_ * new_width,
               new_base + new_height * new_width,
               T() );
  }

  SAFE_DELETE_ARRAY(this->base_);
  this->base_ = new_base;
  this->capacity_ = new_width * new_height;
  this->length_ = new_width * new_height;
  this->width_ = new_width;
  this->height_ = new_height;
  
#ifdef YAT_DEFINED_MIN
#  undef min
#  undef YAT_DEFINED_MIN
#endif
}

// ============================================================================
// Class : SharedBuffer
// ============================================================================
// ===========================================================================
// SharedBuffer::SharedBuffer
// ============================================================================
template <typename T>
SharedBuffer<T>::SharedBuffer (size_t _capacity)
  : Buffer<T>(_capacity), SharedObject()
{
 //- noop ctor
}

// ============================================================================
// SharedBuffer::SharedBuffer
// ============================================================================
template <typename T>
SharedBuffer<T>::SharedBuffer(size_t _length, T* _base)
  : Buffer<T>(_length, _base), SharedObject()
{
 //- noop ctor
}

// ============================================================================
// Buffer::Buffer
// ============================================================================
template <typename T> 
SharedBuffer<T>::SharedBuffer(const Buffer<T>& _src)
  : Buffer<T>(_src), SharedObject()
{
 //- noop ctor
}

// ============================================================================
// Buffer::~Buffer
// ============================================================================
template <typename T> 
SharedBuffer<T>::~SharedBuffer(void)
{
 //- noop ctor
}

// ============================================================================
// Class : CircularBuffer
// ============================================================================
// ============================================================================
// Buffer::CircularBuffer
// ============================================================================
template <typename T, typename L>
CircularBuffer<T,L>::CircularBuffer(void)
  : wp_(0), 
    frozen_(false),
    data_ (0),
    ordered_data_ (0),
    num_cycles_ (0)
{
  //- noop
}

// ============================================================================
// Buffer::CircularBuffer
// ============================================================================
template <typename T, typename L>
CircularBuffer<T,L>::CircularBuffer(size_t _capacity)
  : wp_(0), 
    frozen_(false),
    data_ (0),
    ordered_data_ (0),
    num_cycles_ (0)
{
  this->capacity(_capacity);
}

// ============================================================================
// CircularBuffer::~CircularBuffer
// ============================================================================
template <typename T, typename L>
CircularBuffer<T,L>::~CircularBuffer (void)
{
  //- noop dtor
}

// ============================================================================
// CircularBuffer::freeze
// ============================================================================
template <typename T, typename L>
void CircularBuffer<T,L>::freeze (void)
{
  yat::AutoMutex<L> guard(this->lock_);
  this->frozen_ = true;
}

// ============================================================================
// CircularBuffer::unfreeze
// ============================================================================
template <typename T, typename L>
void CircularBuffer<T,L>::unfreeze (void)
{
  yat::AutoMutex<L> guard(this->lock_);
  this->frozen_ = false;
}

// ============================================================================
// CircularBuffer::clear
// ============================================================================
template <typename T, typename L>
void CircularBuffer<T,L>::clear (void)
{
  yat::AutoMutex<L> guard(this->lock_);
  this->wp_ = this->data_.base();
  this->data_.clear();
  this->num_cycles_ = 0;
  this->ordered_data_.clear();
}

// ============================================================================
// Buffer::capacity
// ============================================================================
template <typename T, typename L> 
void CircularBuffer<T,L>::capacity (size_t _capacity)
{
  yat::AutoMutex<L> guard(this->lock_);
  
  //- set buffer length.
  this->data_.capacity(_capacity);
  this->data_.force_length(_capacity);
  this->data_.clear();
  
  //- update write pointer
  this->wp_ = this->data_.base();
  
  //- (re)allocate ordered data buffer
  this->ordered_data_.capacity(_capacity);
  this->ordered_data_.force_length(_capacity);
  this->ordered_data_.clear();
  
  //- reset num of cycles
  this->num_cycles_ = 0;
}

// ============================================================================
// CircularBuffer::fill
// ============================================================================
template <typename T, typename L> 
void CircularBuffer<T,L>::fill(const T& _val)
{
  yat::AutoMutex<L> guard(this->lock_);
  this->data_.fill(_val);
}

// ============================================================================
// CircularBuffer::push
// ============================================================================
template <typename T, typename L>
void CircularBuffer<T,L>::push(T _data)
{ 
  yat::AutoMutex<L> guard(this->lock_);
  
  //- check preallocation
  if (! this->data_.capacity()) 
  {
    THROW_YAT_ERROR("PROGRAMMING_ERROR", 
                    "Circular buffer was not initialized properly", 
                    "CircularBuffer<T,L>::push");
  } 
  
  //- if frozen then ignore the data
  if (this->frozen_)
    return;

  *this->wp_ = _data;

  //- update write pointer 
  this->wp_++;
  
  //- modulo 
  if (static_cast<size_t>(this->wp_ - this->data_.base()) >= this->data_.capacity())
  {
  	this->num_cycles_++;
  	this->wp_ =  this->data_.base();
  }
}

// ============================================================================
// CircularBuffer::ordered_data
// ============================================================================
template <typename T, typename L> 
const Buffer<T> & CircularBuffer<T,L>::ordered_data (void)
{
  yat::AutoMutex<L> guard(this->lock_);
  
  //- check preallocation
  if (this->ordered_data_.capacity() != this->data_.capacity())
  {
    THROW_YAT_ERROR("INTERNAL_ERROR", "Unexpected buffer size", "CircularBuffer::ordered_data");
  }
  
  //- clear ordered data buffer
  this->ordered_data_.clear();
  
  long newer_data_count = this->wp_ - this->data_.base(); 
  long older_data_count = this->data_.length() - newer_data_count;

  //- reorder the data
  if (newer_data_count >= 0 && this->num_cycles_)
  {
  	//- reorder the data: copy older data first
    ::memcpy(this->ordered_data_.base(), this->wp_, older_data_count * sizeof(T));
    //- reorder the data: copy newer data
    ::memcpy(this->ordered_data_.base() + older_data_count,  this->data_.base(),  newer_data_count * sizeof(T));
  }
  else
  {
    ::memcpy(this->ordered_data_.base(),  this->data_.base(), this->data_.size());
  }

  //- return the reordered data
  return this->ordered_data_;
}

} // namespace 

#endif // _DATA_BUFFER_CPP_

