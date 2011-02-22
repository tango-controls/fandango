/*!
 * \file     
 * \brief    An example of yat::Task (and related classes) usage. .
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
 */

#include "my_task.h"

#define kLO_WATER_MARK   128
#define kHI_WATER_MARK   512
#define kPOST_MSG_TMO      2
#define kNUM_MSGS       4096

int main(int argc, char* argv[])
{
  YAT_LOG_STATIC("Instanciating Task...");
	
  MyTask * dt = new MyTask(kLO_WATER_MARK, kHI_WATER_MARK);
  
  YAT_LOG_STATIC("Starting Task...");
	
  try
  {
    dt->go(2000); 
  }
  catch (const yat::Exception&)
  {
    YAT_LOG_STATIC("yat exception caught - could not start task. aborting...");
    dt->exit();
    return 0;
  }
  catch (...)
  {
    YAT_LOG_STATIC("unknown exception caught - could not start task. aborting...");
    dt->exit();
    return 0;
  }
  yat::Message * m = 0;

  for (size_t i = 0; i < kNUM_MSGS; i++)
  {
    try
    {
      m = new yat::Message(kDUMMY_MSG);
      if (m == 0) 
        throw std::bad_alloc();
      dt->post(m, kPOST_MSG_TMO);
    }
    catch (const std::bad_alloc&)
    {
      YAT_LOG_STATIC("std::bad_alloc except. caught - could not post msg#" << i);
    }
    catch (const yat::Exception&)
    {
      YAT_LOG_STATIC("tango except. caught - could not post msg#" << i);
    }
    catch (...)
    {
      YAT_LOG_STATIC("unknown except. caught - could not post msg#" << i);
    }
  }

#ifdef WIN32
  ::Sleep(2000);
#else
  ::sleep(2);
#endif

  try
  {
    dt->exit();
  }
  catch (const yat::Exception&)
  {
    YAT_LOG_STATIC("tango except. caught - could stop task. aborting...");
  }
  catch (...)
  {
    YAT_LOG_STATIC("unknown except. caught - could stop task. aborting...");
    return 0;
  }

  return 0;
}

