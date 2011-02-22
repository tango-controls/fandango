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
#include <yat/threading/Worker.h>
#include <yat/threading/Work.h>

#if !defined (YAT_INLINE_IMPL)
# include <yat/threading/Worker.i>
#endif // YAT_INLINE_IMPL

namespace yat
{

// ============================================================================
// Worker::Worker
// ============================================================================
Worker::Worker (const std::string& _id, Work* _work, bool _delete_work)
  : Task(Config(false,
              0,
              false,
              0,
              false,
              kDEFAULT_LO_WATER_MARK,
              kDEFAULT_HI_WATER_MARK,
              false,
              0)),
    id_(_id),
    work_(work_),
    work_ownership_(_delete_work),
    err_manager_(0),
    state_(&stateNEW)
{
  YAT_TRACE("Worker::Worker");

  if (_work == 0)
  {
    THROW_YAT_ERROR("NULL_POINTER",
                    "An attempt to create a Worker with a NULL Work was made",
                    "Worker::Worker");
  }
}

// ============================================================================
// Worker::~Worker
// ============================================================================
Worker::~Worker ()
{
  YAT_TRACE("Worker::~Worker");

  if (this->work_ownership_)
    SAFE_DELETE_PTR(this->work_);

}

// ============================================================================
// Worker::append_child
// ============================================================================
void Worker::append_child (Worker* _worker)
{
  YAT_TRACE("Worker::append_child");

  if (_worker == 0)
    THROW_YAT_ERROR("NULL_POINTER",
                    "Trying to register a NULL pointer as a child worker",
                    "Worker::append_child");

  this->child_list_.push_back(_worker);
}

// ============================================================================
// Worker::register_err_manager
// ============================================================================
void Worker::register_err_manager(WorkerErrorManager* _c)
{
  YAT_TRACE("Worker::register_err_manager");

  if (_c == 0)
    THROW_YAT_ERROR("NULL_POINTER",
                    "Trying to register a NULL pointer as the error manager",
                    "Worker::register_err_manager");

  WorkerList& children = this->child_list_;
  WorkerList::iterator it;
  for (it = children.begin(); it != children.end(); it++)
  {
    Worker* child = (*it);
    try
    {
      child->register_err_manager(_c);
    }
    catch(...)
    {
      //- TODO : handle errors better here
      throw;
    }
  }

  this->err_manager_ = _c;
}


// ============================================================================
// Worker::handle_message
// ============================================================================
void Worker::handle_message (Message& _msg)
{
  YAT_TRACE("Worker::handle_message");

//-
//- Macro to ease the callback handling
//-
#define CALL_WORK_CALLBACK( msg_id, callback )                               \
  try                                                                        \
  {                                                                          \
    this->work_->callback;                                                   \
  }                                                                          \
  catch(Exception& ex)                                                       \
  {                                                                          \
    RETHROW_YAT_ERROR(ex,                                                    \
                      "INTERNAL_ERROR",                                      \
                      "Error during " #msg_id " message handling",           \
                      "Worker::handle_message");                             \
  }                                                                          \
  catch(...)                                                                 \
  {                                                                          \
    THROW_YAT_ERROR("UNKNOWN_ERROR",                                         \
                    "Unknown error during " #msg_id " message handling",     \
                    "Worker::handle_message");                               \
  }


//-
//- Macro to ease the message forwarding
//-
#define POST_TO_CHILDREN(msg_id, msg, wait, tmo_ms)                          \
  try                                                                        \
  {                                                                          \
    this->post_to_children(const_cast<Message*>(msg),                        \
                           wait,                                             \
                           tmo_ms);                                          \
  }                                                                          \
  catch(Exception& ex)                                                       \
  {                                                                          \
    RETHROW_YAT_ERROR(ex,                                                    \
                      "INTERNAL_ERROR",                                      \
                      "Could not forward " #msg_id " to children",           \
                      "Worker::handle_message");                             \
  }                                                                          \
  catch(...)                                                                 \
  {                                                                          \
    THROW_YAT_ERROR("UNKNOWN_ERROR",                                         \
                    "Unknown error when forwarding " #msg_id " to children", \
                    "Worker::handle_message");                               \
  }


  //- check if msg is allowed in the curent state
  if ( ! this->state_->is_allowed(_msg.type()) )
  {
    //- throw an exception but do NOT switch to FAULT state
    //- since it is not a fatal error
    //- the message will just be trashed
    THROW_YAT_ERROR("OPERATION_NOT_ALLOWED",
                    "This type of msg is not allowed in the current state",
                    "Worker::handle_message");
  }
  //- ok, msg is allowed. now process it

  try
  {
    switch (_msg.type())
	  {
      //----------------------------------------------------------
      //- WORKER_INIT msg handling
      //----------------------------------------------------------
	    case WORKER_INIT:
      {
        if (this->err_manager_ == 0)
          THROW_YAT_ERROR("OPERATION_NOT_ALLOWED",
                          "Unable to init a Worker if no error manager has been registered",
                          "Worker::handle_message");

        POST_TO_CHILDREN(WORKER_INIT, &_msg, true, kDEFAULT_MSG_TMO_MSECS);
        CALL_WORK_CALLBACK(WORKER_INIT, on_init());
        this->state_ = &this->stateSTANDBY;
        break;
      }
      //----------------------------------------------------------
      //- WORKER_EXIT msg handling
      //----------------------------------------------------------
  	  case WORKER_EXIT:
      {
        POST_TO_CHILDREN(WORKER_EXIT, &_msg, true, kDEFAULT_MSG_TMO_MSECS);
        CALL_WORK_CALLBACK(WORKER_EXIT, on_exit());
        break;
      }
      //----------------------------------------------------------
      //- WORKER_TIMEOUT msg handling
      //----------------------------------------------------------
  	  case WORKER_TIMEOUT:
      {
        CALL_WORK_CALLBACK(WORKER_TIMEOUT, on_timeout());
        break;
      }
      //----------------------------------------------------------
      //- WORKER_PERIODIC msg handling
      //----------------------------------------------------------
  	  case WORKER_PERIODIC:
      {
        CALL_WORK_CALLBACK(WORKER_PERIODIC, on_periodic_msg());
        break;
      }
      //----------------------------------------------------------
      //- WORKER_START msg handling
      //----------------------------------------------------------
  	  case WORKER_START:
      {
        POST_TO_CHILDREN(WORKER_START, &_msg, true, kDEFAULT_MSG_TMO_MSECS);
        CALL_WORK_CALLBACK(WORKER_START, on_start());
        this->state_ = &this->stateRUNNING;
        break;
      }
      //----------------------------------------------------------
      //- WORKER_STOP msg handling
      //----------------------------------------------------------
  	  case WORKER_STOP:
      {
        POST_TO_CHILDREN(WORKER_STOP, &_msg, true, kDEFAULT_MSG_TMO_MSECS);
        CALL_WORK_CALLBACK(WORKER_STOP, on_stop());
        this->state_ = &this->stateSTANDBY;
        break;
      }
      //----------------------------------------------------------
      //- WORKER_RESET msg handling
      //----------------------------------------------------------
  	  case WORKER_RESET:
      {
        POST_TO_CHILDREN(WORKER_RESET, &_msg, true, kDEFAULT_MSG_TMO_MSECS);
        CALL_WORK_CALLBACK(WORKER_RESET, on_reset());
        //- stay in RUNNING state
        break;
      }
      //----------------------------------------------------------
      //- WORKER_ABORT msg handling
      //----------------------------------------------------------
  	  case WORKER_ABORT:
      {
        POST_TO_CHILDREN(WORKER_ABORT, &_msg, true, kDEFAULT_MSG_TMO_MSECS);
        CALL_WORK_CALLBACK(WORKER_ABORT, on_abort());
        this->state_ = &this->stateSTANDBY;
        break;
      }
      //----------------------------------------------------------
      //- WORKER_SUSPEND msg handling
      //----------------------------------------------------------
  	  case WORKER_SUSPEND:
      {
        POST_TO_CHILDREN(WORKER_SUSPEND, &_msg, true, kDEFAULT_MSG_TMO_MSECS);
        CALL_WORK_CALLBACK(WORKER_SUSPEND, on_suspend());
        this->state_ = &this->stateSUSPENDED;
        break;
      }
      //----------------------------------------------------------
      //- WORKER_RESUME msg handling
      //----------------------------------------------------------
  	  case WORKER_RESUME:
      {
        POST_TO_CHILDREN(WORKER_RESUME, &_msg, true, kDEFAULT_MSG_TMO_MSECS);
        CALL_WORK_CALLBACK(WORKER_RESUME, on_resume());
        this->state_ = &this->stateRUNNING;
        break;
      }
      //----------------------------------------------------------
      //- WORKER_USER_MSG msg handling
      //----------------------------------------------------------
      default:
      {
        //- execute the user message
        Message* out_msg = 0;
        CALL_WORK_CALLBACK( WORKER_USER_MSG,
                            on_user_msg(const_cast<Message&>(_msg), out_msg) );

        //- then post the output to the children, without waiting for completion
        POST_TO_CHILDREN(WORKER_USER_MSG, out_msg, false, 0);
        break;
      }
    } //- switch (_msg.type())
  
  }
  catch(const Exception &ex)
  {
    this->state_ = &this->stateFAULT;

    //- notify the error manager
    if (this->err_manager_ != 0)
    {
      Message* msg = 0;
      WorkerError* we = 0;
      try
      {
        we = new WorkerError( this->id_, ex.errors );
        if (we == 0)
          throw std::bad_alloc();

        msg = new yat::Message(WorkerErrorManager::WORKER_ERROR);
        if (msg == 0)
          throw std::bad_alloc();

        msg->attach_data(we);

        we = 0; //- WorkerError object is now owned by the Message
                //- thus does not need deallocation in case an error
                //- occurs in the sequel

        this->err_manager_->post(msg);
      }
      catch(...)
      {
        SAFE_DELETE_PTR(we);
        SAFE_DELETE_PTR(msg);
        //- ignore error
      }
    }

  }

#undef CALL_WORK_CALLBACK
#undef POST_TO_CHILDREN_WAIT
}

// ============================================================================
// Worker::post_to_children
// ============================================================================
void Worker::post_to_children (Message* _msg, bool _wait, size_t _tmo_ms)
{
  YAT_TRACE("Worker::post_to_children");

  if (_msg != 0)
  {
    WorkerList& children = this->child_list_;
    WorkerList::iterator it;
    for (it = children.begin(); it != children.end(); it++)
    {
      Worker* child = (*it);
      try
      {
        if (_wait)
          child->post(_msg);
        else
          child->wait_msg_handled(_msg, _tmo_ms);
      }
      catch(...)
      {
        //- TODO : handle errors better here
        throw;
      }
    }
  }

}

// ============================================================================
// Worker::post_void_msg_to_self
// ============================================================================
void Worker::post_void_msg_to_self (MessageType _msg_type, bool _wait, size_t _tmo_ms)
{
  YAT_TRACE("Worker::post_void_msg_to_self");

  Message* msg = 0;

  //- Message allocation
  try
  {
    msg = new yat::Message(_msg_type, DEFAULT_MSG_PRIORITY, _wait);
    if (msg == 0)
      throw std::bad_alloc();
  }
  catch(...)
  {
    THROW_YAT_ERROR("OUT_OF_MEMORY",
                    "Error while allocating a message",
                    "Worker::post");
  }

  //- Message posting
  try
  {
    if (_wait)
      this->wait_msg_handled(msg, _tmo_ms);
    else
      this->post(msg);
  }
  catch (Exception &ex)
  {
    SAFE_RELEASE( msg );
    RETHROW_YAT_ERROR(ex,
                      "INTERNAL_ERROR",
                      "Message posting failed",
                      "Worker::post");
  }
  catch(...)
  {
    SAFE_RELEASE( msg );
    THROW_YAT_ERROR("UNKNOWN_ERROR",
                    "Unknown error when posting a Message",
                    "Worker::post");
  }
}

// ============================================================================
// Worker::start
// ============================================================================
void Worker::start (size_t _tmo_ms)
{
  YAT_TRACE("Worker::start");

  try
  {
    this->post_void_msg_to_self (WORKER_START, true, _tmo_ms);
  }
  catch(Exception& ex)
  {
    RETHROW_YAT_ERROR(ex,
                      "INTERNAL_ERROR",
                      "Message posting failed",
                      "Worker::start");
  }
  catch(...)
  {
    THROW_YAT_ERROR("UNKNOWN_ERROR",
                    "Unknown error when posting a message",
                    "Worker::start");
  }

}

// ============================================================================
// Worker::stop
// ============================================================================
void Worker::stop (size_t _tmo_ms)
{
  YAT_TRACE("Worker::stop");

  try
  {
    this->post_void_msg_to_self (WORKER_STOP, true, _tmo_ms);
  }
  catch(Exception& ex)
  {
    RETHROW_YAT_ERROR(ex,
                      "INTERNAL_ERROR",
                      "Message posting failed",
                      "Worker::stop");
  }
  catch(...)
  {
    THROW_YAT_ERROR("UNKNOWN_ERROR",
                    "Unknown error when posting a message",
                    "Worker::stop");
  }

}


// ============================================================================
// Worker::reset
// ============================================================================
void Worker::reset (size_t _tmo_ms)
{
  YAT_TRACE("Worker::reset");

  try
  {
    this->post_void_msg_to_self (WORKER_RESET, true, _tmo_ms);
  }
  catch(Exception& ex)
  {
    RETHROW_YAT_ERROR(ex,
                      "INTERNAL_ERROR",
                      "Message posting failed",
                      "Worker::reset");
  }
  catch(...)
  {
    THROW_YAT_ERROR("UNKNOWN_ERROR",
                    "Unknown error when posting a message",
                    "Worker::reset");
  }

}

// ============================================================================
// Worker::abort
// ============================================================================
void Worker::abort (size_t _tmo_ms)
{
  YAT_TRACE("Worker::abort");

  try
  {
    this->post_void_msg_to_self (WORKER_ABORT, true, _tmo_ms);
  }
  catch(Exception& ex)
  {
    RETHROW_YAT_ERROR(ex,
                      "INTERNAL_ERROR",
                      "Message posting failed",
                      "Worker::abort");
  }
  catch(...)
  {
    THROW_YAT_ERROR("UNKNOWN_ERROR",
                    "Unknown error when posting a message",
                    "Worker::abort");
  }

}

} // namespace
