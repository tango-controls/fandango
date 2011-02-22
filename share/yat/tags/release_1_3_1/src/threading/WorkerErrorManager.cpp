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
#include <yat/threading/WorkerErrorManager.h>

#if !defined (YAT_INLINE_IMPL)
# include <yat/threading/WorkerErrorManager.i>
#endif // YAT_INLINE_IMPL

namespace yat
{

// ============================================================================
// WorkerErrorManager::WorkerErrorManager
// ============================================================================
WorkerErrorManager::WorkerErrorManager (void)
  : Task(Config(false,
              0,
              false,
              0,
              false,
              kDEFAULT_LO_WATER_MARK,
              kDEFAULT_HI_WATER_MARK,
              false,
              0)),
    has_error_(false),
    entry_point_(0)
{
  YAT_TRACE("WorkerErrorManager::WorkerErrorManager");

  this->enable_timeout_msg (false);
  this->enable_periodic_msg(false);

}

// ============================================================================
// WorkerErrorManager::~WorkerErrorManager
// ============================================================================
WorkerErrorManager::~WorkerErrorManager (void)
{
  YAT_TRACE("WorkerErrorManager::~WorkerErrorManager");
}

// ============================================================================
// WorkerErrorManager::exit
// ============================================================================
void WorkerErrorManager::exit (void)
{
  YAT_TRACE("WorkerErrorManager::exit");
}

// ============================================================================
// WorkerErrorManager::notify_error
// ============================================================================
void WorkerErrorManager::handle_message(Message& _msg)
{
  YAT_TRACE("WorkerErrorManager::handle_message");

  try
  {
    switch (_msg.type())
	  {
    case TASK_INIT:
      {
        break;
      }
    case TASK_EXIT:
      {
        break;
      }
    case WORKER_ERROR:
      {
        WorkerError* e = 0;

        //- get the error from the msg
        try
        {
         //- extract error from msg
          _msg.detach_data(e);
         //- store the error
         this->last_error_ = *e;
         delete e;
        }
        catch(...)
        {
          YAT_LOG("Unable to dettach data from a WORKER_ERROR msg");
          YAT_LOG("-> leaving the place");
          return;
        }


        //- send an ABORT msg to the entry-point
        this->entry_point_->abort();
        
        break;
      }
    case CLEAR_ERROR_STATUS:
      {
        this->has_error_ = false;
        this->last_error_ = WorkerError();
      }
    default:
      {
        break;
      }
    } //- switch (_msg.type())
  }
  catch(...)
  {
  }
}


} // namespace
