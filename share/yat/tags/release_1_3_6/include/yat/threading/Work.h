/*!
 * \file    Work.h
 * \brief   Header file of the YAT work class.
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _WORK_H_
#define _WORK_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat/threading/Task.h>

namespace yat
{

class YAT_DECL Work
{
  friend class Worker;

public:
  /**
   * Constructor
   */
  Work (void);

  /**
   * Destructor
   */
  virtual ~Work (void);

protected:

  /**
   * Called when Worker is initialized
   */
  virtual void on_init (void);
    //- throw (Exception)

  /**
   * Called when the Worker receives a <EXIT> message
   */
  virtual void on_exit (void);
    //- throw (Exception)

  /**
   * Called when the Worker receives a <START> message
   */
  virtual void on_start (void);
    //- throw (Exception)

  /**
   * Called when the Worker receives a <STOP> message
   */
  virtual void on_stop (void);
    //- throw (Exception)

  /**
   * Called when the Worker receives a <RESET> message
   */
  virtual void on_reset (void);
    //- throw (Exception)

  /**
   * Called when the Worker receives a <ABORT> message
   */
  virtual void on_abort (void);
    //- throw (Exception)

  /**
   * Called when the Worker receives a <SUSPEND> message
   */
  virtual void on_suspend (void);
    //- throw (Exception)

  /**
   * Called when the Worker receives a <RESUME> message
   */
  virtual void on_resume (void);
    //- throw (Exception)

  /**
   * Called when the Worker receives a <TIMEOUT> message
   */
  virtual void on_timeout (void);
    //- throw (Exception)

  /**
   * Called when the Worker receives a <PERIODIC> message
   */
  virtual void on_periodic_msg (void);
    //- throw (Exception)

  /**
   * Called when the Worker receives a user defined message
   */
  virtual void on_user_msg (Message& in, Message *&out);
    //- throw (Exception)
};

} // namespace

#if defined (YAT_INLINE_IMPL)
# include <yat/threading/Work.i>
#endif // YAT_INLINE_IMPL

#endif
