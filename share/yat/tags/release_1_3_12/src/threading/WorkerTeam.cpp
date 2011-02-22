/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat/threading/WorkerTeam.h>
#include <yat/threading/Worker.h>

#if !defined (YAT_INLINE_IMPL)
# include <yat/threading/WorkerTeam.i>
#endif // YAT_INLINE_IMPL

namespace yat
{

// ============================================================================
// WorkerTeam::WorkerTeam
// ============================================================================
WorkerTeam::WorkerTeam (void)
: entry_point_(0),
  err_manager_(0)
{
  YAT_TRACE("WorkerTeam::WorkerTeam");

  try
  {
    this->err_manager_ = new WorkerErrorManager;
    if (this->err_manager_ == 0)
      throw std::bad_alloc();
  }
  catch(const std::bad_alloc&)
  {
    THROW_YAT_ERROR("OUT_OF_MEMORY",
                    "The WorkerErrorManager could not be instantiated",
                    "WorkerTeam::WorkerTeam");
  }
  catch(...)
  {
    THROW_YAT_ERROR("UNKNOWN_ERROR",
                    "Unknown error occured while instantiating the WorkerErrorManager",
                    "WorkerTeam::WorkerTeam");
  }
}

// ============================================================================
// WorkerTeam::~WorkerTeam
// ============================================================================
WorkerTeam::~WorkerTeam (void)
{
  YAT_TRACE("WorkerTeam::~WorkerTeam");

  if (this->err_manager_)
  {
    this->err_manager_->exit();
    this->err_manager_ = 0;
  }

}

// ============================================================================
// WorkerTeam::register_entry_point
// ============================================================================
void WorkerTeam::register_entry_point(Worker* _w)
{
  YAT_TRACE("WorkerTeam::register_entry_point");

  
  //- check arg
  if (_w == 0)
  {
    THROW_YAT_ERROR("NULL_POINTER",
                    "Cannot register a null pointer as entry point",
                    "WorkerTeam::register_entry_point");
  }

  try
  {
    _w->register_err_manager(this->err_manager_);
  }
  catch(Exception& ex)
  {
    RETHROW_YAT_ERROR(ex,
                      "INTERNAL_ERROR",
                      "Registering error manager failed",
                      "WorkerTeam::register_entry_point");
  }
  catch(...)
  {
    THROW_YAT_ERROR("UNKNOWN_ERROR",
                    "Unknown error while registering error manager",
                    "WorkerTeam::register_entry_point");
  }

  this->entry_point_ = _w;
}


} // namespace
