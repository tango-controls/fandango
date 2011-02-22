//=============================================================================
//
// file :        ThreadedDevice.h
//
// description : Include for the ThreadedDevice class.
//
// project :	Threaded device toolbox example
//
// $Author: leclercq $
//
// $Revision: 1.1 $
//
// $Log: ThreadedDevice.h,v $
// Revision 1.1  2007/07/18 13:09:43  leclercq
// no message
//
// Revision 1.3  2007/07/18 13:02:50  leclercq
// Added a threaded device example
//
// Revision 1.1  2007/07/18 12:57:05  leclercq
// Added a threaded device example
//
//
// copyleft :    European Synchrotron Radiation Facility
//               BP 220, Grenoble 38043
//               FRANCE
//
//=============================================================================
//
//  		This file is generated by POGO
//	(Program Obviously used to Generate tango Object)
//
//         (c) - Software Engineering Group - ESRF
//=============================================================================
#ifndef _ThreadedDevice_H
#define _ThreadedDevice_H

#include <tango.h>
//using namespace Tango;

#include "MyYatTask.h"

/**
 * @author	$Author: leclercq $
 * @version	$Revision: 1.1 $
 */

 //	Add your own constants definitions here.
 //-----------------------------------------------


namespace ThreadedDevice_ns
{

/**
 * Class Description:
 * Gives an example of a device threaded by inheritance
 */

/*
 *	Device States Description:
 *  Tango::FAULT :    Initialization failed or runtime error
 *
 *  Tango::RUNNING :  Device is up and running
 */


class ThreadedDevice: public Tango::Device_3Impl
{
public :
	//	Add your own data members here
	//-----------------------------------------


	//	Here is the Start of the automatic code generation part
	//-------------------------------------------------------------	
/**
 *	@name attributes
 *	Attributs member data.
 */
//@{
		Tango::DevDouble	*attr_postThisValueToTheTask_read;
		Tango::DevDouble	attr_postThisValueToTheTask_write;
		Tango::DevDouble	*attr_ramdomVector_read;
//@}

/**
 *	@name Device properties
 *	Device properties member data.
 */
//@{
//@}

/**@name Constructors
 * Miscellaneous constructors */
//@{
/**
 * Constructs a newly allocated Command object.
 *
 *	@param cl	Class.
 *	@param s 	Device Name
 */
	ThreadedDevice(Tango::DeviceClass *cl,string &s);
/**
 * Constructs a newly allocated Command object.
 *
 *	@param cl	Class.
 *	@param s 	Device Name
 */
	ThreadedDevice(Tango::DeviceClass *cl,const char *s);
/**
 * Constructs a newly allocated Command object.
 *
 *	@param cl	Class.
 *	@param s 	Device name
 *	@param d	Device description.
 */
	ThreadedDevice(Tango::DeviceClass *cl,const char *s,const char *d);
//@}

/**@name Destructor
 * Only one desctructor is defined for this class */
//@{
/**
 * The object desctructor.
 */	
	~ThreadedDevice() {delete_device();};
/**
 *	will be called at device destruction or at init command.
 */
	void delete_device();
//@}

	
/**@name Miscellaneous methods */
//@{
/**
 *	Initialize the device
 */
	virtual void init_device();
/**
 *	Always executed method befor execution command method.
 */
	virtual void always_executed_hook();

//@}

/**
 * @name ThreadedDevice methods prototypes
 */

//@{
/**
 *	Hardware acquisition for attributes.
 */
	virtual void read_attr_hardware(vector<long> &attr_list);
/**
 *	Extract real attribute values for postThisValueToTheTask acquisition result.
 */
	virtual void read_postThisValueToTheTask(Tango::Attribute &attr);
/**
 *	Write postThisValueToTheTask attribute values to hardware.
 */
	virtual void write_postThisValueToTheTask(Tango::WAttribute &attr);
/**
 *	Extract real attribute values for ramdomVector acquisition result.
 */
	virtual void read_ramdomVector(Tango::Attribute &attr);
/**
 *	Read/Write allowed for postThisValueToTheTask attribute.
 */
	virtual bool is_postThisValueToTheTask_allowed(Tango::AttReqType type);
/**
 *	Read/Write allowed for ramdomVector attribute.
 */
	virtual bool is_ramdomVector_allowed(Tango::AttReqType type);

/**
 *	Read the device properties from database
 */
	 void get_device_property();
//@}

	//	Here is the end of the automatic code generation part
	//-------------------------------------------------------------	



protected :	
	//	Add your own data members here
	//-----------------------------------------

  //- the device task
	MyYatTask * dev_task;

	//- just a double... see attribute <postThisValueToTheTask>
	double value;
	
	//- the last available data obtained from the task
	MyYatTask::MyDataBuffer * dev_data;
};

}	// namespace_ns

#endif	// _ThreadedDevice_H
