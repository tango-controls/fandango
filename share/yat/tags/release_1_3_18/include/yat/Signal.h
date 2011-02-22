/*!
 * \file    
 * \brief   
 * \author  Ramon Sune - ALBA Synchrotron
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#pragma once

#include <list>
#include <yat/Callback.h>
#include <yat/threading/Mutex.h>

/// @file
/// Here we define yat::Signal. This is, a class to which different callbacks
/// can be registered and then will all be run when it is are triggered.
/// It is usefull to implement observers: we will call run() on the signal
/// object without knowing who and how many are interested in this.
/// In UnsafeSignal the list of observers is not mutex protected.
/// The callbacks are defined as yat::Callback objects.

namespace yat 
{

template <typename ParamType_, typename LockType_ = yat::NullMutex> 
class Signal
{
public:
  YAT_DEFINE_CALLBACK(Slot, ParamType_);

protected:
  mutable LockType_ lock_;
  std::list<Slot> observers_;

  bool _run(ParamType_ param, std::list<Slot> & observers)
  {
    typename std::list<Slot>::iterator 
                i(observers.begin()),
                e(observers.end());
    bool everythingOk = true;
    for (; i!=e; ++i) {
      try {
        (*i)(param);
      } catch(...) {
        everythingOk = false;
      }
    }
    return everythingOk;
  }

public:

  bool run(ParamType_ param)
  {
    yat::AutoMutex<LockType_> guard(this->lock_);
    return this->_run(param, this->observers_);
  }

  bool connected() const
  {
    yat::AutoMutex<LockType_> guard(this->lock_);
    return !this->observers_.empty();
  }

  void connect(Slot cb)
  {
    yat::AutoMutex<LockType_> guard(this->lock_);
    this->observers_.remove(cb);
    this->observers_.push_front(cb);
  }

  void disconnect(Slot cb)
  {
    yat::AutoMutex<LockType_> guard(this->lock_);
    this->observers_.remove(cb);
  }
};

} // namespace yat
