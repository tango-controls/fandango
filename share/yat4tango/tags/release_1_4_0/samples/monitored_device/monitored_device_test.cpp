/*!
 * \file     
 * \brief    An example of yat::SharedPtr usage
 * \author   N. Leclercq, J. Malik - Synchrotron SOLEIL
 */

#include <iostream>
#include <yat/threading/Thread.h>
#include <yat4tango/MonitoredDevice.h>
#include <yat4tango/MonitoredDeviceTask.h>
            
//-----------------------------------------------------------------------------
// MAIN
//-----------------------------------------------------------------------------
int main(int argc, char* argv[])
{
/*
  {
    yat4tango::MonitoredDevice md("tmp/test/tangotest_1");
    std::cout << "instanciated MonitoredDevice" << std::endl; 

    //- add the same attr twice (second add should be silently ignored)
    yat4tango::MonitoredAttributeKey kstate = md.add_monitored_attribute("State");
    yat4tango::MonitoredAttributeKey kstate_bis = md.add_monitored_attribute("State");
    std::cout << "added <State> attribute twice. returned keys should be the same... " << std::endl;
    if (kstate == kstate_bis)
    {
      std::cout << "ok. keys match." << std::endl;
    }
    else
    {
      std::cout << "ko. keys don't match! fix that bug in the yat4tango lib then retry ;-)" << std::endl;
    }
    
    //- add a dummy attr (there is no "foo" attr on the TangoTest device)
    yat4tango::MonitoredAttributeKey k_foo = md.add_monitored_attribute("foo");
    
    //- add more attrs 
    yat4tango::MonitoredAttributeKey k_ls = md.add_monitored_attribute("long_scalar");  
    yat4tango::MonitoredAttributeKey k_ds = md.add_monitored_attribute("double_scalar"); 
    yat4tango::MonitoredAttributeKey k_lsro = md.add_monitored_attribute("long_spectrum_ro"); 
    yat4tango::MonitoredAttributeKey k_liro = md.add_monitored_attribute("long_image_ro"); 
    
    for (size_t i = 0; i < 10; i++)
    {
      //- read attributes 
      md.poll_attributes();
      
      //- retrieve <foo> attr by key 
      yat4tango::MonitoredAttribute & ma_foo = md.get_monitored_attribute(k_foo);
      //- try to extract its value (error expected)
      try 
      {
        Tango::DevDouble tdd;
        ma_foo.get_value(tdd);
      }
      catch (Tango::DevFailed& df) 
      {
        std::cout << "ok. got expected error: " << df.errors[0].desc << std::endl;
      }
      
      //- retrieve <long_scalar> attr by name
      yat4tango::MonitoredAttribute & ma_ls = md.get_monitored_attribute("long_scalar");    
      //- try to extract its value as a Tango::DevDouble (error expected)
      try 
      {
        Tango::DevDouble tdd;
        ma_ls.get_value(tdd);
        std::cout << "ko. operation was supposed to fail!" << std::endl;
      }
      catch (Tango::DevFailed& df) 
      {
        std::cout << "ok. got expected error: " << df.errors[0].desc << std::endl;
      }
      //- try to extract its value as a Tango::DevLong (no error expected)
      try 
      {
        Tango::DevLong tdl;
        ma_ls.get_value(tdl);
        std::cout << "ok. current <long_scalar> value is " << tdl << std::endl;
      }
      catch (Tango::DevFailed& df) 
      {
        std::cout << "ko. got unexpected error: " << df.errors[0].desc << std::endl;
      }
      
      //- more tests
      yat4tango::MonitoredAttribute & ma_ds = md.get_monitored_attribute(k_ds);
      //- try to extract its value as a Tango::DevLong (no error expected)
      try 
      {
        Tango::DevDouble tdd;
        ma_ds.get_value(tdd);
        std::cout << "ok. current <long_scalar> value is " << tdd << std::endl;
      }
      catch (Tango::DevFailed& df) 
      {
        std::cout << "ko. got unexpected error: " << df.errors[0].desc << std::endl;
      }
      
      //- try to extract its value as a Tango::DevLong (no error expected)
      try 
      {
        size_t dimx, dimy;
        std::vector<Tango::DevLong> v;
        md.get_monitored_attribute(k_lsro).get_value(v, &dimx, &dimy);
        std::cout << "ok. <long_spectrum_ro> size is " << dimx << " x " << dimy << std::endl;
      }
      catch (Tango::DevFailed& df) 
      {
        std::cout << "ko. got unexpected error: " << df.errors[0].desc << std::endl;
      }
      
      yat4tango::MonitoredAttribute & ma_liro = md.get_monitored_attribute("long_image_ro");
      //- try to extract its value as a Tango::DevLong (no error expected)
      try 
      {
        size_t dimx, dimy;
        std::vector<Tango::DevLong> v;
        ma_liro.get_value(v, &dimx, &dimy);
        std::cout << "ok. <long_image_ro> size is " << dimx << " x " << dimy << std::endl;
      }
      catch (Tango::DevFailed& df) 
      {
        std::cout << "ko. got unexpected error: " << df.errors[0].desc << std::endl;
      }
      
      yat::Thread::sleep(500);
    }
  }
*/

  {
    std::cout << std::endl;
    std::cout << std::endl;
    std::cout << std::endl;
 
    yat4tango::MonitoredDeviceTask * mdt = new yat4tango::MonitoredDeviceTask("tmp/test/tangotest_1");

    yat4tango::MonitoredAttributeKey k_ls   = mdt->add_monitored_attribute("long_scalar");  
    yat4tango::MonitoredAttributeKey k_ds   = mdt->add_monitored_attribute("double_scalar"); 
    yat4tango::MonitoredAttributeKey k_lsro = mdt->add_monitored_attribute("long_spectrum_ro"); 
    yat4tango::MonitoredAttributeKey k_liro = mdt->add_monitored_attribute("long_image_ro"); 

    mdt->set_polling_period(250);

    mdt->start();

    for (size_t i = 0; i < 20; i++)
    {
      //-------------------------------------------------
      try 
      {
        Tango::DevLong tdl;
        mdt->get_monitored_attribute(k_ls).get_value(tdl);
        std::cout << "ok. current <long_scalar> value is " << tdl << std::endl;
      }
      catch (Tango::DevFailed& df) 
      {
        std::cout << "ko. got unexpected error: " << df.errors[0].desc << std::endl;
      }
      //-------------------------------------------------
      try 
      {
        Tango::DevDouble tdd;
        mdt->get_monitored_attribute(k_ds).get_value(tdd);
        std::cout << "ok. current <long_scalar> value is " << tdd << std::endl;
      }
      catch (Tango::DevFailed& df) 
      {
        std::cout << "ko. got unexpected error: " << df.errors[0].desc << std::endl;
      }
      //-------------------------------------------------
      try 
      {
        size_t dimx, dimy;
        std::vector<Tango::DevLong> v;
        mdt->get_monitored_attribute(k_lsro).get_value(v, &dimx, &dimy);
        std::cout << "ok. <long_spectrum_ro> size is " << dimx << " x " << dimy << std::endl;
      }
      catch (Tango::DevFailed& df) 
      {
        std::cout << "ko. got unexpected error: " << df.errors[0].desc << std::endl;
      }
      //-------------------------------------------------
      try 
      {
        size_t dimx, dimy;
        std::vector<Tango::DevLong> v;
        mdt->get_monitored_attribute(k_liro).get_value(v, &dimx, &dimy);
        std::cout << "ok. <long_image_ro> size is " << dimx << " x " << dimy << std::endl;
      }
      catch (Tango::DevFailed& df) 
      {
        std::cout << "ko. got unexpected error: " << df.errors[0].desc << std::endl;
      }
      //-------------------------------------------------
      yat::Thread::sleep(100);
    }
    
    std::cout << "asking the MonitoredDeviceTask to quit..." << std::endl;
    mdt->quit();
    std::cout << "MonitoredDeviceTask exited" << std::endl;
  }
  
  return 0;
}
