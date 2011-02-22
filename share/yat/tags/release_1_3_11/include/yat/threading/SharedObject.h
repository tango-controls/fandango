/*!
 * \file    SharedObject.h
 * \brief   Header file of the YAT shared object class.
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_SHARED_OBJECT_H_
#define _YAT_SHARED_OBJECT_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat/CommonHeader.h>
#include <yat/threading/Mutex.h>

namespace yat
{

// ============================================================================
//! A reference counted object abstraction.
// ============================================================================
//!
//! Base class for any reference counted object (i.e. shared) object.
//!
// ============================================================================
class YAT_DECL SharedObject
{
public:

  SharedObject (void);
  // Constructor.

  virtual ~SharedObject (void);
  // Destructor.

  SharedObject * duplicate (void);
  // Return a "shallow" copy. Increment the reference count by 1
  // to avoid deep copies.

  int release (bool commit_suicide = true);
  // Decrease the shared reference count by 1.  If the reference count
  // equals 0 and <commit_suicide> is true, then delete <this> and return 0.
  // Return 1 otherwise. Behavior is undefinedif reference count < 0.

  int reference_count (void) const;
  // Returns the current reference count.

  void lock (void);
  // Locks the underlying Mutex

  void unlock (void);
  // Unlocks the underlying Mutex

  Mutex & mutex (void);
  // Returns the underlying synch. object

protected:
  // a mutex to protect the data against race conditions
  Mutex lock_;

private:
  // internal release implementation
  SharedObject * release_i (void);

  //- reference count for (used to avoid deep copies)
  int reference_count_;

  // = Disallow these operations.
  //--------------------------------------------
  SharedObject & operator= (const SharedObject &);
  SharedObject (const SharedObject &);
};

} // namespace

#if defined (YAT_INLINE_IMPL)
# include <yat/threading/SharedObject.i>
#endif  // YAT_INLINE_IMPL

#endif  // _SHARED_OBJECT_H_
