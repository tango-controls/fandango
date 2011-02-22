static const char *RcsId = "$Header: /usr/local/CVS/Libraries/YAT4tango/samples/threaded_device/ClassFactory.cpp,v 1.1 2007/07/18 13:09:43 leclercq Exp $";
//+=============================================================================
//
// file :        ClassFactory.cpp
//
// description : C++ source for the class_factory method of the DServer
//               device class. This method is responsible to create
//               all class singletin for a device server. It is called
//               at device server startup
//
// project :     TANGO Device Server
//
// $Author: leclercq $
//
// $Revision: 1.1 $
//
// $Log: ClassFactory.cpp,v $
// Revision 1.1  2007/07/18 13:09:43  leclercq
// no message
//
// Revision 1.4  2007/07/18 13:02:50  leclercq
// Added a threaded device example
//
//
// copyleft :    European Synchrotron Radiation Facility
//               BP 220, Grenoble 38043
//               FRANCE
//
//-=============================================================================
//
//  		This file is generated by POGO
//	(Program Obviously used to Generate tango Object)
//
//         (c) - Software Engineering Group - ESRF
//=============================================================================


#include <tango.h>
#include <ThreadedDeviceClass.h>

/**
 *	Create ThreadedDeviceClass singleton and store it in DServer object.
 */

void Tango::DServer::class_factory()
{

	add_class(ThreadedDevice_ns::ThreadedDeviceClass::init("ThreadedDevice"));

}
