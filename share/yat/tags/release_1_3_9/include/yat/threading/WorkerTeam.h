/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _WORKERTEAM_H_
#define _WORKERTEAM_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat/threading/WorkerErrorManager.h>

namespace yat
{

class Worker;
class WorkerErrorManager;

class YAT_DECL WorkerTeam
{
public:

  WorkerTeam ();
		//- throw (Exception)

  ~WorkerTeam ();

  void register_entry_point (Worker* _w);
    //- throw (Exception)

private:
  Worker* entry_point_;
  WorkerErrorManager* err_manager_;
};

} // namespace

#if defined (YAT_INLINE_IMPL)
# include <yat/threading/WorkerTeam.i>
#endif // YAT_INLINE_IMPL

#endif
