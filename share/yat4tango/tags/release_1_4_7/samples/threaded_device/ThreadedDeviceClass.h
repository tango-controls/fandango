//=============================================================================
//
// file :         ThreadedDeviceClass.h
//
// description :  Include for the ThreadedDeviceClass root class.
//                This class is represents the singleton class for
//                the ThreadedDevice device class.
//                It contains all properties and methods which the 
//                ThreadedDevice requires only once e.g. the commands.
//			
// project :      TANGO Device Server
//
// $Author: leclercq $
//
// $Revision: 1.1 $
//
// $Log: ThreadedDeviceClass.h,v $
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
// copyleft :     European Synchrotron Radiation Facility
//                BP 220, Grenoble 38043
//                FRANCE
//
//=============================================================================
//
//  		This file is generated by POGO
//	(Program Obviously used to Generate tango Object)
//
//         (c) - Software Engineering Group - ESRF
//=============================================================================

#ifndef _ThreadedDeviceCLASS_H
#define _ThreadedDeviceCLASS_H

#include <tango.h>
#include <ThreadedDevice.h>


namespace ThreadedDevice_ns
{
//=====================================
//	Define classes for attributes
//=====================================
class ramdomVectorAttrib: public Tango::SpectrumAttr
{
public:
	ramdomVectorAttrib():SpectrumAttr("ramdomVector", Tango::DEV_DOUBLE, Tango::READ, 1024) {};
	~ramdomVectorAttrib() {};
	
	virtual void read(Tango::DeviceImpl *dev,Tango::Attribute &att)
	{(static_cast<ThreadedDevice *>(dev))->read_ramdomVector(att);}
	virtual bool is_allowed(Tango::DeviceImpl *dev,Tango::AttReqType ty)
	{return (static_cast<ThreadedDevice *>(dev))->is_ramdomVector_allowed(ty);}
};

class postThisValueToTheTaskAttrib: public Tango::Attr
{
public:
	postThisValueToTheTaskAttrib():Attr("postThisValueToTheTask", Tango::DEV_DOUBLE, Tango::READ_WRITE) {};
	~postThisValueToTheTaskAttrib() {};
	
	virtual void read(Tango::DeviceImpl *dev,Tango::Attribute &att)
	{(static_cast<ThreadedDevice *>(dev))->read_postThisValueToTheTask(att);}
	virtual void write(Tango::DeviceImpl *dev,Tango::WAttribute &att)
	{(static_cast<ThreadedDevice *>(dev))->write_postThisValueToTheTask(att);}
	virtual bool is_allowed(Tango::DeviceImpl *dev,Tango::AttReqType ty)
	{return (static_cast<ThreadedDevice *>(dev))->is_postThisValueToTheTask_allowed(ty);}
};

//=========================================
//	Define classes for commands
//=========================================
//
// The ThreadedDeviceClass singleton definition
//

class ThreadedDeviceClass : public Tango::DeviceClass
{
public:
//	properties member data

//	add your own data members here
//------------------------------------

public:
	Tango::DbData	cl_prop;
	Tango::DbData	cl_def_prop;
	Tango::DbData	dev_def_prop;

//	Method prototypes
	static ThreadedDeviceClass *init(const char *);
	static ThreadedDeviceClass *instance();
	~ThreadedDeviceClass();
	Tango::DbDatum	get_class_property(string &);
	Tango::DbDatum	get_default_device_property(string &);
	Tango::DbDatum	get_default_class_property(string &);
	
protected:
	ThreadedDeviceClass(string &);
	static ThreadedDeviceClass *_instance;
	void command_factory();
	void get_class_property();
	void attribute_factory(vector<Tango::Attr *> &);
	void write_class_property();
	void set_default_property();

private:
	void device_factory(const Tango::DevVarStringArray *);
};


}	//	namespace ThreadedDevice_ns

#endif // _ThreadedDeviceCLASS_H
