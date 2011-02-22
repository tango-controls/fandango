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
#include <math.h>
#include <algorithm>
#include <yat/CommonHeader.h>
#include <yat/threading/Utilities.h>
#include <yat/threading/MessageQ.h>

#if !defined (YAT_INLINE_IMPL)
# include <yat/threading/MessageQ.i>
#endif // YAT_INLINE_IMPL

namespace yat
{

// ============================================================================
// MessageQ::MessageQ
// ============================================================================
MessageQ::MessageQ (size_t _lo_wm, size_t _hi_wm, bool _throw_on_post_tmo)
: 	
    msg_q_ (0),
    msg_producer_sync_ (lock_),
    msg_consumer_sync_ (lock_),
		state_(MessageQ::OPEN),
		enable_timeout_msg_ (false),
    enable_periodic_msg_ (false),
    lo_wm_ (_lo_wm),
    hi_wm_ (_hi_wm),
    saturated_ (false),
    throw_on_post_msg_timeout_ (_throw_on_post_tmo),
    last_returned_msg_periodic_ (false)
#if defined (YAT_DEBUG)
    , has_been_saturated (0)
    , has_been_unsaturated (0)
    , max_num_msg (0)
    , posted_with_waiting_msg_counter (0)
    , posted_without_waiting_msg_counter (0)
    , trashed_msg_counter (0)
    , trashed_on_post_tmo_counter (0)
#endif
{
	YAT_TRACE("MessageQ::MessageQ");

	_RESET_TIMESTAMP(this->last_periodic_msg_ts_);
}

// ============================================================================
// MessageQ::~MessageQ
// ============================================================================
MessageQ::~MessageQ (void)
{
	YAT_TRACE("MessageQ::~MessageQ");
	
	MutexLock guard(this->lock_);

	this->state_ = MessageQ::CLOSED;

#if ! defined (YAT_DEBUG)
  
  this->clear_i();

#else

  size_t num_msg_in_q = this->clear_i();

  unsigned long total_msg = this->posted_with_waiting_msg_counter 
                          + this->posted_without_waiting_msg_counter
                          + this->trashed_msg_counter
                          + this->trashed_on_post_tmo_counter;

  unsigned long actually_handled_msg = total_msg 
                                     - num_msg_in_q 
                                     - this->trashed_msg_counter
                                     - this->trashed_on_post_tmo_counter;

  YAT_LOG("MessageQ::statistics::has reached hw " << this->has_been_saturated << " times");

  YAT_LOG("MessageQ::statistics::has reached lw " << this->has_been_unsaturated << " times");

  YAT_LOG("MessageQ::statistics::has contained up to " << this->max_num_msg << " msgs");

  YAT_LOG("MessageQ::statistics::immediate msg posting::" << this->posted_without_waiting_msg_counter);

  YAT_LOG("MessageQ::statistics::delayed msg posting::" << this->posted_with_waiting_msg_counter);

  YAT_LOG("MessageQ::statistics::trashed on post tmo::" << this->trashed_on_post_tmo_counter);

  YAT_LOG("MessageQ::statistics::trashed on other criteria::" << this->trashed_msg_counter);

  YAT_LOG("MessageQ::statistics::total msg::" << total_msg);

  YAT_LOG("MessageQ::statistics::pending when msgQ destroyed::" << num_msg_in_q);

  YAT_LOG("MessageQ::statistics::actually handled msg::" << actually_handled_msg);

#endif
}

// ============================================================================
// MessageQ::close
// ============================================================================
void MessageQ::close (void)
{
	//- YAT_TRACE("MessageQ::close");
	
	MutexLock guard(this->lock_);

	this->state_ = MessageQ::CLOSED;
}

// ============================================================================
// MessageQ::clear_i
// ============================================================================
size_t MessageQ::clear_i (void)
{
  size_t num_msg_in_q = this->msg_q_.size();

  while (! this->msg_q_.empty())
  {
	  Message * m = this->msg_q_.front ();
    if (m) m->release();
	  this->msg_q_.pop_front();
  }

  return num_msg_in_q;
}

// ============================================================================
// MessageQ::post
// ============================================================================
int MessageQ::post (yat::Message * msg, size_t _tmo_msecs)
	throw (Exception)
{
	YAT_TRACE("MessageQ::post");

	//- check input
	if (! msg) return 0;

	//- do not post any TIMEOUT or PERIODIC msg
	if (msg->type() == TASK_TIMEOUT || msg->type() == TASK_PERIODIC)
	{
#if defined (YAT_DEBUG)
    this->trashed_msg_counter++;
#endif
		//- silently trash the message
		msg->release();
		return 0;
	}

  //- enter critical section (required for cond.var. to work properly)
	MutexLock guard(this->lock_);

	//- can only post a msg on an opened MsgQ
	if (this->state_ != MessageQ::OPEN)
	{
#if defined (YAT_DEBUG)
    this->trashed_msg_counter++;
#endif
		//- silently trash the message (should we throw an exception instead?)
		msg->release();
		return 0;
	}

  //- we force post of ctrl message even if the msQ is saturated
  if (msg->is_thread_ctrl_message()) 
  {
    //- insert msg according to its priority
    try
    {
	    this->insert_i(msg);
    }
    catch (...)
    {
      //- insert_i released the message (no memory leak)
      THROW_YAT_ERROR("INTERNAL_ERROR",
                      "Could not post ctrl message [msgQ insertion error]",
                      "MessageQ::post");
    }
	  //- wakeup msg consumers (tell them there is a message to handle)
    //- this will work since we are under critical section 
	  msg_consumer_sync_.signal();
    //- do some stats 
#if defined (YAT_DEBUG)
    this->posted_without_waiting_msg_counter++;
#endif
    //- done (skip remaining code)
    return 0;
  }

  //- is the messageQ saturated?
  if (! this->saturated_ && (this->msg_q_.size() == this->hi_wm_))
  {
    YAT_LOG("MessageQ::post::**** SATURATED ****");
    //- do some stats 
#if defined (YAT_DEBUG)
    this->has_been_saturated++;
#endif
    //- mark msgQ as saturated
    this->saturated_ = true;
  }

  //- msg is not a ctrl message...
  //- wait for the messageQ to have room for new messages
  if (! this->wait_not_full_i(_tmo_msecs))
  {
    YAT_LOG("MessageQ::post::tmo expired");
    //- can't post msg, destroy it in order to avoid memory leak
    msg->release(); 
    //- do some stats 
#if defined (YAT_DEBUG)
    this->trashed_on_post_tmo_counter++;
#endif
    //- throw exception if the messageQ is configured to do so
    if (this->throw_on_post_msg_timeout_)
    {
      THROW_YAT_ERROR("TIMEOUT_EXPIRED",
                      "Could not post message [timeout expired]",
                      "MessageQ::post");
    }
    //- return if we didn't throw an exception
    return 0;
  }

  //- ok there is enough room to post our msg
  DEBUG_ASSERT(this->msg_q_.size() <= this->hi_wm_);

  //- insert the message according to its priority
  try
  {
	  this->insert_i(msg);
  }
  catch (...)
  {
    //- insert_i released the message (no memory leak)
    THROW_YAT_ERROR("INTERNAL_ERROR",
                    "Could not post message [msgQ insertion error]",
                    "MessageQ::post");
  }

  //- do some stats 
#if defined (YAT_DEBUG)
  if (this->msg_q_.size() > this->max_num_msg)
    this->max_num_msg = this->msg_q_.size();
#endif

	//- wakeup msg consumers (tell them there is a new message to handle)
  //- this will work since we are still under critical section
	msg_consumer_sync_.signal ();

  return 0;
}

// ============================================================================
// MessageQ::next_message
// ============================================================================
yat::Message * MessageQ::next_message (size_t _tmo_msecs)
{
	YAT_TRACE("MessageQ::next_message");

  YAT_LOG("MessageQ::next_message::waiting for next message");

  //- enter critical section (required for cond.var. to work properly)
	MutexLock guard(this->lock_);

  //- wait for the messageQ to contain at least one message
  do
  {
    if (! this->wait_not_empty_i(_tmo_msecs))
    {
      //- <wait_not_empty_i> returned <false> : means no msg in msg queue after <_tmo_msecs>
      YAT_LOG("MessageQ::next_message::tmo expired [MessageQ::wait_not_empty_i returned false]");
      
      //- it may be time to return a periodic message
      if (this->enable_periodic_msg_ && this->periodic_tmo_expired(_tmo_msecs))
      {
        this->last_returned_msg_periodic_ = true;
        GET_TIME(this->last_periodic_msg_ts_);
        return new Message(TASK_PERIODIC); 
      }
      
      //- else return a timeout msg 
      if (this->enable_timeout_msg_)
      {
        this->last_returned_msg_periodic_ = false;
        return new Message(TASK_TIMEOUT);
      }
    }
    else
    {
      //- <wait_not_empty_i> returned <true> : means there is at least one msg in msg queue after
      break;
    }
  } while (1);

  //- ok, there should be at least one message in the messageQ
  DEBUG_ASSERT(this->msg_q_.empty() == false);

  //- we are still under critical section since the "Condition::timed_wait" 
  //- located in "wait_not_empty_i" garantee the associated mutex (i.e. 
  //- this->lock_ in the present case) is acquired when the function returns.

	//- get msg from Q
  yat::Message * msg = this->msg_q_.front();

  //- parano. debugging
  DEBUG_ASSERT(msg != 0);

  //- if the msg is a ctrl msg...
  if (msg->is_thread_ctrl_message())
  {
    //... then extract it from the Q and return it
	  this->msg_q_.pop_front();
    //- if we reach the low water mark, then wakeup msg producer(s) 
    if (this->saturated_ && this->msg_q_.size() <= this->lo_wm_)
    {
      YAT_LOG("MessageQ::next_message::**** UNSATURATED ****");
      //- do some stats 
#if defined (YAT_DEBUG)
      this->has_been_unsaturated++;
#endif
      //- no more saturated
      this->saturated_ = false;
      //- this will work since we are still under critical section
      this->msg_producer_sync_.broadcast();
    }
	  return msg;
  }

  //- avoid PERIODIC msg starvation (see note above)
  if (
       this->enable_periodic_msg_ 
         && 
       this->periodic_tmo_expired (_tmo_msecs) 
         && 
       this->last_returned_msg_periodic_ == false
     )
  {
    //- we didn't actually extract the <msg> from the Q.
    //- we just "accessed it using "pop_front" so no need to reinject it into the Q
    this->last_returned_msg_periodic_ = true;
    _GET_TIME(this->last_periodic_msg_ts_);
    return new Message(TASK_PERIODIC); 
  }
  //- PERIODIC msg disabled or last returned message was a PERIODIC...
  //- ... just return msg currently on top of Q
  else 
  {
    this->last_returned_msg_periodic_ = false;
    //... then extract it from the Q and return it
	  this->msg_q_.pop_front();
    //- if we reach the low water mark, then wakeup msg producer(s) 
    if (this->saturated_ && (this->msg_q_.size() - 1) <= this->lo_wm_)
    {
      YAT_LOG("MessageQ::next_message::**** UNSATURATED ****");
      //- do some stats 
#if defined (YAT_DEBUG)
      this->has_been_unsaturated++;
#endif
      //- no more saturated
      this->saturated_ = false;
      //- this will work since we are still under critical section
      this->msg_producer_sync_.broadcast(); 
    }
	  return msg;
  }

  //- should never reach this spoint
  return 0;
}

// ============================================================================
// MessageQ::wait_not_empty_i
// ============================================================================
bool MessageQ::wait_not_empty_i (size_t _tmo_msecs)
{
	//- <this->lock_> MUST be locked by the calling thread
  //----------------------------------------------------

  //- while the messageQ is empty...
  while (this->msg_q_.empty ())
  {
 	  //- wait for a msg or tmo expiration 
    if (! this->msg_consumer_sync_.timed_wait(_tmo_msecs))
      return false; 
  }

  //- at least one message available in the MsgQ
  return true;
} 


// ============================================================================
// MessageQ::wait_not_full_i
// ============================================================================
bool MessageQ::wait_not_full_i (size_t _tmo_msecs)
{
	//- <this->lock_> MUST be locked by the calling thread
  //----------------------------------------------------

#if defined (YAT_DEBUG)
 //- do some stats
 if (this->saturated_)
 {
#endif

  //- while the messageQ is empty...
  while (this->saturated_)
  {
 	  //- wait for a msg or tmo expiration 
    if (! this->msg_producer_sync_.timed_wait(_tmo_msecs))
      return false; 
#if defined (YAT_DEBUG)
    //- do some stats
    else if (! this->saturated_)
      this->posted_with_waiting_msg_counter++;
#endif
  }

#if defined (YAT_DEBUG)
 }
 else
 {
   //- do some stats
   this->posted_without_waiting_msg_counter++;
 }
#endif

  //- at least one message available in the MsgQ
  return true;
}

// ============================================================================
// Binary predicate
// ============================================================================
static bool insert_msg_criterion (Message * const m1, Message * const m2)
{
  return m2->priority() < m1->priority();  
}
 
// ============================================================================
// MessageQ::insert_i
// ============================================================================
void MessageQ::insert_i (Message * _msg)
  throw (Exception)
{
  try
  {
    if (this->msg_q_.empty())
    {
      //- optimization: no need to take count of the msg priority
      this->msg_q_.push_front (_msg);
    }
    else
    { 
      //- insert msg according to its priority
      MessageQImpl::iterator pos = std::upper_bound(this->msg_q_.begin(),
                                                    this->msg_q_.end(),
                                                    _msg,
                                                    insert_msg_criterion);
      this->msg_q_.insert(pos, _msg);
    }
  }
  catch (...)
  {
    Exception e("INTERNAL_ERROR", 
                "could insert message into the message queue", 
                "MessageQ::insert_i");
    _msg->set_error(e);
    _msg->processed();
    _msg->release();
  }
}

} // namespace
