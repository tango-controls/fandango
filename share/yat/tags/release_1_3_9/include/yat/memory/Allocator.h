/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_ALLOCATOR_H_
#define _YAT_ALLOCATOR_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <list>
#include <yat/CommonHeader.h>

namespace yat 
{

// ============================================================================
//! The NewAllocator class 
// ============================================================================
//!  
// ============================================================================
template <typename T> 
class NewAllocator
{
public:
  //- Ctor
  NewAllocator ();

  //- Dtor
  virtual ~NewAllocator ();
  
  //- memory allocation - can't allocate more than sizeof(T)
  virtual T * malloc ();

  //- memory release - <p> must have beeb allocated by <this> CachedAllocator
  virtual void free (T * p);
};

/*
// ============================================================================
//! The CachedAllocator class  
// ============================================================================
//! Implements an unbounded memory pool of T with selectable locking strategy 
//! ok but for "cachable" classes only!
// ============================================================================
#define CACHABLE_CLASS_DECL(CLASS_NAME, LOCKING_STRATEGY)
  typedef CachedAllocator<CLASS_NAME, LOCKING_STRATEGY> CLASS_NAME#Cache; \
  static CLASS_NAME#::Cache m_cache; \
  void * operator new (size_t); \
  void operator delete (void *); \
  static void pre_alloc (size_t _nobjs); \
  static void release_pre_alloc (void);
#endif
  //-TODO: not usable for the moment - to be finished...
*/

// ============================================================================
//! The CachedAllocator class  
// ============================================================================
//! Implements an unbounded memory pool of T with selectable locking strategy 
//! ok... for "cachable" classes only!
// ============================================================================
template <typename T, typename L = yat::NullMutex> 
class CachedAllocator : public NewAllocator<T>
{
  //- memory pool (or cache) implementation
  typedef std::list<T*> Cache; 

public: 
  //- Ctor - preallocates <nb_preallocated_objs> 
  CachedAllocator (size_t nb_preallocated_objs = 0);

  //- Dtor
  virtual ~CachedAllocator();
  
  //- memory allocation - can't allocate more than sizeof(T)
  virtual T * malloc ();

  //- memory release - <p> must have beeb allocated by <this> CachedAllocator
  virtual void free (T * p);

protected:
  //- locking (i.e. thread safety) strategy
  L m_lock;

  //- the memory cache (i.e. memory pool) 
  Cache m_cache;
};

} // namespace

#if defined (YAT_INLINE_IMPL)
# include <yat/memory/Allocator.i>
#endif // YAT_INLINE_IMPL

#include <yat/memory/Allocator.tpp>

#endif // _YAT_ALLOCATOR_H_


