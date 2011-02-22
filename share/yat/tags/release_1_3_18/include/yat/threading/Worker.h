/*!
 * \file    Worker.h
 * \brief   Header file of the YAT worker class.
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _WORKER_H_
#define _WORKER_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <deque>
#include <utility>
#include <yat/threading/Task.h>

namespace yat
{

class Work;
class WorkerErrorManager;

typedef std::pair<std::string, Exception::ErrorList> WorkerError;

class YAT_DECL Worker : public Task
{
  friend class WorkerTeam;

public:
  /**
   * WorkerMessageType
   */
  typedef enum
  {
	  WORKER_INIT     = TASK_INIT,
    WORKER_TIMEOUT  = TASK_TIMEOUT,
    WORKER_PERIODIC = TASK_PERIODIC,
    WORKER_EXIT     = TASK_EXIT,
    WORKER_START    = FIRST_USER_MSG,
    WORKER_STOP,
    WORKER_RESET,
    WORKER_ABORT,
    WORKER_SUSPEND,
    WORKER_RESUME,
    WORKER_FIRST_USER_MSG
  } MessageType;

  /**
   * Creates a non initialized Worker instance (see init below)
   */
  Worker (const std::string& _id, 
          Work* _work,
          bool _delete_work = true);
    //- throw (Exception)

  /**
   * Release Worker's resources
   */
  virtual ~Worker ();

  /**
   * Appends a child worker, which will be forwarded each msg sent to the current instance
   */
  void append_child(Worker* _worker);
    //- throw (Exception)

  /**
   * Start the worker
   */
  void start (size_t _tmo_ms = 0);
    //- throw (Exception)

  /**
   * Stop the worker
   */
  void stop (size_t _tmo_ms = 0);
    //- throw (Exception)

  /**
   * Reset the worker, i.e. clean internal state as if worker had just been started
   */
  void reset (size_t _tmo_ms = 0);
    //- throw (Exception)

  /**
   * Abort the worker's activity (same as stop but with a higher priority)
   */
  void abort (size_t _tmo_ms = 0);
    //- throw (Exception)

protected:
  
  /**
   * Message handling procedure
   */
	virtual void handle_message (Message&)
    throw (Exception);

private:

  void post_void_msg_to_self(MessageType _msg_type, bool _wait = true, size_t _tmo_ms = 0);
    //- throw (Exception)

  void post_to_children(Message* _msg, bool _wait = true, size_t _tmo_ms = 0);
    //- throw (Exception)

  //- store the WorkerErrorManager pointer and call register_err_manager on the children
  void register_err_manager(WorkerErrorManager* _c);
    //- throw (Exception)

  std::string id_;

  Work* work_;

  bool work_ownership_;

  typedef std::deque<Worker*> WorkerList;
  WorkerList child_list_;

  WorkerErrorManager* err_manager_;

  class AbstractState
  {
  public:
    virtual bool is_allowed( size_t msg_id ) = 0;
  };

  #define CONCRETE_WORKERSTATE_DEF( ClassName, InstName ) \
  class ClassName : public AbstractState                  \
  {                                                       \
  public:                                                 \
    virtual bool is_allowed( size_t msg_id );             \
  };                                                      \
  static ClassName InstName;

  CONCRETE_WORKERSTATE_DEF( StateNEW      , stateNEW       )
  CONCRETE_WORKERSTATE_DEF( StateRUNNING  , stateRUNNING   )
  CONCRETE_WORKERSTATE_DEF( StateSTANDBY  , stateSTANDBY   )
  CONCRETE_WORKERSTATE_DEF( StateSUSPENDED, stateSUSPENDED )
  CONCRETE_WORKERSTATE_DEF( StateFAULT    , stateFAULT     )

  #undef CONCRETE_WORKERSTATE_DEF

  AbstractState* state_;
};

} // namespace

#if defined (YAT_INLINE_IMPL)
# include <yat/threading/Worker.i>
#endif // YAT_INLINE_IMPL

#endif
