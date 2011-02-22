/*!
 * \file     
 * \brief    An example of yat::Task (and related classes) usage. .
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
 */

#include <yat/Timer.h>
#include "my_task.h"

// ============================================================================
// play with the <lo> and <hi> msgQ watermarks to test the yat::msgQ in action
// ============================================================================
#define kLO_WATER_MARK  128
#define kHI_WATER_MARK  512

// ============================================================================
// play with the post msg timeout to test the associated yat::msgQ feature
// ============================================================================
#define kPOST_MSG_TMO 2

// ============================================================================
// number of message to be posted in this example
// ============================================================================
#define kNUM_MSGS 8192

// ============================================================================
//  main
// ============================================================================
int main(int argc, char* argv[])
{
 yat::Message * m = 0;

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

  for (size_t i = 0; i < kNUM_MSGS; i++)
  {
    try
    {
      //- post msg to consumer
      dt->post(new yat::Message(kDUMMY_MSG), kPOST_MSG_TMO);

      //- simulate some time consuming activity
      yat::ThreadingUtilities::sleep(0, 100000);
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

//- THIS IS JUST A CODE BACKUP FOR A WORK IN PROGRESS
#ifdef _USE_MSG_CACHE_ //- (see yat/CommonHeader.h)

  std::vector<yat::Message *> msgs(kNUM_MSGS);

  yat::Timer t;      

  for (size_t i = 0; i < msgs.size(); i++)
    msgs[i] = new yat::Message(kDUMMY_MSG);
  double dt_usec = t.elapsed_usec();
  std::cout << "First alloc took "
            << dt_usec
            << " usecs ["
            << dt_usec / kNUM_MSGS
            << " usecs per msg msg]"
            << std::endl;

  for (size_t i = 0; i < msgs.size(); i++)
    msgs[i]->release();

  t.restart();

  for (size_t i = 0; i < msgs.size(); i++)
    msgs[i] = new yat::Message(kDUMMY_MSG);
  dt_usec = t.elapsed_usec();
  std::cout << "Second alloc took "
            << dt_usec
            << " usecs ["
            << dt_usec / kNUM_MSGS
            << " usecs per msg msg]"
            << std::endl;

  for (size_t i = 0; i < msgs.size(); i++)
    msgs[i]->release();

  return 0;

#endif //- _USE_MSG_CACHE_