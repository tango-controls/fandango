/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _WorkerErrorManager_H_
#define _WorkerErrorManager_H_


// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat/threading/Worker.h>

namespace yat
{

class YAT_DECL WorkerErrorManager : public Task
{
public:

  enum
  {
    WORKER_ERROR = FIRST_USER_MSG,
    CLEAR_ERROR_STATUS
  };

  WorkerErrorManager();

  virtual ~WorkerErrorManager();

  bool has_error() const;

  const WorkerError& get_error() const;

  virtual void exit (void)
    throw (Exception);

protected:
	//- handle_message -----------------------
	virtual void handle_message (Message&);
		//- throw (Exception)

private:

  bool has_error_;
  WorkerError last_error_;
  Worker * entry_point_;
};

} // namespace

#if defined (YAT_INLINE_IMPL)
# include <yat/threading/WorkerErrorManager.i>
#endif // YAT_INLINE_IMPL

#endif
