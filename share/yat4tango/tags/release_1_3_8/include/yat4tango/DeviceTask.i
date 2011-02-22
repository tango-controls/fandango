/*!
 * \file    Task.i
 * \brief   Inlined code of the YAT4tango DeviceTask class.
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

namespace yat4tango
{

// ============================================================================
// DeviceTask::handle_message
// ============================================================================
YAT_INLINE void DeviceTask::handle_message (yat::Message& msg)
    //-   throw (yat::Exception)
{
  try
  {
    this->process_message(msg);
  }
  catch (const Tango::DevFailed& df)
  {
    throw TangoYATException(df);
  }
  catch (...)
  {
    throw yat::Exception();
  }
}

// ============================================================================
// DeviceTask::go
// ============================================================================
YAT_INLINE void DeviceTask::go (size_t _tmo_msecs)
    //- throw (Tango::DevFailed)
{
  try
  {
    this->Task::go(_tmo_msecs);
  }
  catch (const yat::Exception& ye)
  {
    throw YATDevFailed(ye);
  }
}

// ============================================================================
// DeviceTask::go
// ============================================================================
YAT_INLINE void DeviceTask::go (yat::Message * _msg, size_t _tmo_msecs)
    //- throw (Tango::DevFailed)
{
  try
  {
    this->Task::go(_msg, _tmo_msecs);
  }
  catch (const yat::Exception& ye)
  {
    throw YATDevFailed(ye);
  }
}
    
// ============================================================================
// DeviceTask::exit
// ============================================================================
YAT_INLINE void DeviceTask::exit ()
    //- throw (Tango::DevFailed)
{
  try
  {
    this->Task::exit();
  }
  catch (const yat::Exception& ye)
  {
    throw YATDevFailed(ye);
  }
}

// ============================================================================
// DeviceTask::post
// ============================================================================
YAT_INLINE void DeviceTask::post (yat::Message * _msg, size_t _tmo_msecs)
    //- throw (Tango::DevFailed)
{
  try
  {
    this->Task::post(_msg, _tmo_msecs);
  }
  catch (const yat::Exception& ye)
  {
    throw YATDevFailed(ye);
  }
}

// ============================================================================
// DeviceTask::wait_msg_handled
// ============================================================================
YAT_INLINE void DeviceTask::wait_msg_handled (yat::Message * _msg, size_t _tmo_msecs)
    //- throw (Tango::DevFailed)
{
  try
  {
    this->Task::wait_msg_handled(_msg, _tmo_msecs);
  }
  catch (const yat::Exception& ye)
  {
    throw YATDevFailed(ye);
  }
}

} //- namespace
