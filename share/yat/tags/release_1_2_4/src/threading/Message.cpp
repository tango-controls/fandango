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
#include <yat/threading/Message.h>
#include <iostream>

#if !defined (YAT_INLINE_IMPL)
# include <yat/threading/Message.i>
#endif // YAT_INLINE_IMPL

namespace yat
{

// ============================================================================
// Message::msg_counter
// ============================================================================
#if defined (YAT_DEBUG)
  Message::MessageID Message::msg_counter = 0;
#endif

// ============================================================================
// Message::allocate 
// ============================================================================
Message * Message::allocate (size_t _msg_type, size_t _msg_priority, bool _waitable)
  throw (Exception)
{
	YAT_TRACE_STATIC("Message::allocate");  
  
  yat::Message * msg = 0;
     
  try
  {
    msg = new yat::Message (_msg_type, _msg_priority, _waitable);
  	if (msg == 0)
      throw std::bad_alloc();
  }
  catch (const std::bad_alloc&)
  {
    THROW_YAT_ERROR("OUT_OF_MEMORY",
                    "Message allocation failed",
                    "Message::allocate");
	}
  catch (...)
  {
    THROW_YAT_ERROR("UNKNOWN_ERROR",
                    "Message allocation failed [unknown exception caught]",
                    "Message::allocate");
	}

  return msg;
}

// ============================================================================
// Message::Message
// ============================================================================
Message::Message (size_t _msg_type, size_t _msg_priority, bool _waitable)
	: SharedObject (),
    processed_ (false),
		type_ (_msg_type),
    priority_ (_msg_priority),
		user_data_ (0),
		msg_data_ (0),
		has_error_ (false),
    cond_ (0)
#if defined (YAT_DEBUG)
    , id_ (++Message::msg_counter)
#endif
{
	YAT_TRACE("Message::Message");

  if (_waitable)
    this->make_waitable();
}

// ============================================================================
// Message::~Message
// ============================================================================
Message::~Message ()
{
	YAT_TRACE("Message::~Message");

	if (this->msg_data_)
  {
		delete this->msg_data_;
    this->msg_data_ = 0;
  }

	if (this->cond_)
  {
    if (! this->processed_)
    {
      AutoMutex<Mutex> guard(this->lock_);
      this->cond_->broadcast();
    }
		delete this->cond_;
    this->cond_ = 0;
  }

	//-note: errors_ contains some Tango::DevError which itself
	//-note: contains CORBA::string_member which releases the 
	//-note: associated memory (i.e. char*)
}

// ============================================================================
// Message::to_string
// ============================================================================
const char * Message::to_string (void) const
{
	switch (this->type_)
	{
		case TASK_INIT:
			return "TASK_INIT";
			break;
		case TASK_TIMEOUT:
			return "TASK_TIMEOUT";
			break;
		case TASK_PERIODIC:
			return "TASK_PERIODIC";
			break;
		case TASK_EXIT:
			return "TASK_EXIT";
			break;
	}
	return "UNKNOWN OR USER DEFINED MSG";
}

// ============================================================================
// Message::dump
// ============================================================================
void Message::dump (void) const
{
  std::cout << "---- Msg@" << std::hex << this << std::dec << std::endl;
#if defined (YAT_DEBUG)
  std::cout << "- id.........." << this->id_ << std::endl;
#endif
  std::cout << "- processed..." << (this->processed_ ? "true" : "false") << std::endl;
  std::cout << "- type........" << this->type_ << std::endl;
  std::cout << "- priority...." << this->priority_ << std::endl;
  std::cout << "- has error..." << this->has_error_ << std::endl;
  std::cout << "- user_data..." << std::hex << this->user_data_ << std::dec <<  std::endl;
  std::cout << "- msg_data...." << std::hex << this->msg_data_ << std::dec << std::endl;
  std::cout << "- waitable...." << (this->cond_ ? "true" : "false") << std::endl;
}

// ============================================================================
// Message::make_waitable 
// ============================================================================
void Message::make_waitable (void)
  throw (Exception)
{ 
  if (this->cond_)
    return;

  try
  {
    this->cond_ = new yat::Condition(this->lock_);
    if (this->cond_ == 0)
      throw std::bad_alloc();
  }
  catch (const std::bad_alloc&)
  {
    THROW_YAT_ERROR("MEMORY_ERROR",
                    "memory allocation failed",
                    "Message::make_waitable");
  }
  catch (...)
  {
    THROW_YAT_ERROR("UNKNOWN_ERROR",
                    "memory allocation failed",
                    "Message::make_waitable");
  }
}

} // namespace