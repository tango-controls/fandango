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
#include <yat4tango/DeviceTask.h>

#if !defined (YAT_INLINE_IMPL)
# include <yat4tango/DeviceTask.i>
#endif // YAT_INLINE_IMPL

namespace yat4tango
{

// ======================================================================
// DeviceTask::DeviceTask
// ======================================================================
DeviceTask::DeviceTask (Tango::DeviceImpl * _dev)
  : yat::Task(), Tango::LogAdapter(_dev)
{
	YAT_TRACE("DeviceTask::DeviceTask");
}

// ======================================================================
// DeviceTask::DeviceTask
// ======================================================================
DeviceTask::DeviceTask (const Task::Config& _cfg, Tango::DeviceImpl * _dev)
  : yat::Task(_cfg), Tango::LogAdapter(_dev)
{
	YAT_TRACE("DeviceTask::DeviceTask");
}

// ======================================================================
// DeviceTask::~DeviceTask
// ======================================================================
DeviceTask::~DeviceTask (void)
{
	YAT_TRACE("DeviceTask::~DeviceTask");
}

} // namespace
