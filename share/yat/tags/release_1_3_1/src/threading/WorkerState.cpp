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
#include <yat/threading/Worker.h>

namespace yat
{

//- definition of the static states declared in Worker class
Worker::StateNEW       Worker::stateNEW;
Worker::StateRUNNING   Worker::stateRUNNING;
Worker::StateSTANDBY   Worker::stateSTANDBY;
Worker::StateSUSPENDED Worker::stateSUSPENDED;
Worker::StateFAULT     Worker::stateFAULT;

bool Worker::StateNEW::is_allowed( size_t msg_id )
{
  switch(msg_id)
  {
  case WORKER_INIT:
    return true;
  }
  return false;
}

bool Worker::StateRUNNING::is_allowed( size_t msg_id )
{
  //- strategy is different here :

  //- prevent only INIT, START, RESUME
  //- (we must allow almost all messages, especially the user messages
  //-  whose msg_id are not known)

  switch(msg_id)
  {
  case WORKER_INIT:
  case WORKER_START:
  case WORKER_RESUME:
    return false;
  }
  return true;
}

bool Worker::StateSTANDBY::is_allowed( size_t msg_id )
{
  switch(msg_id)
  {
  case Worker::WORKER_EXIT:
  case Worker::WORKER_START:
    return true;
  }
  return false;
}

bool Worker::StateSUSPENDED::is_allowed( size_t msg_id )
{
  switch(msg_id)
  {
  case Worker::WORKER_EXIT:
  case Worker::WORKER_STOP:
  case Worker::WORKER_ABORT:
  case Worker::WORKER_RESUME:
    return true;
  }
  return false;
}

bool Worker::StateFAULT::is_allowed( size_t msg_id )
{
  switch(msg_id)
  {
  case Worker::WORKER_EXIT:
  case Worker::WORKER_ABORT:
    return true;
  }
  return false;
}

} // namespace
