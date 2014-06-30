static const char *RcsId     = "$Header: /usr/local/CVS/Libraries/YAT4tango/samples/threaded_device/ThreadedDeviceClass.cpp,v 1.1 2007/07/18 13:09:43 leclercq Exp $";
static const char *TagName   = "$Name: release_1_2_4 $";
static const char *HttpServer= "http://www.esrf.fr/computing/cs/tango/tango_doc/ds_doc/";
//+=============================================================================
//
// file :        ThreadedDeviceClass.cpp
//
// description : C++ source for the ThreadedDeviceClass. A singleton
//               class derived from DeviceClass. It implements the
//               command list and all properties and methods required
//               by the ThreadedDevice once per process.
//
// project :     TANGO Device Server
//
// $Author: leclercq $
//
// $Revision: 1.1 $
//
// $Log: ThreadedDeviceClass.cpp,v $
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
// copyleft :   European Synchrotron Radiation Facility
//              BP 220, Grenoble 38043
//              FRANCE
//
//-=============================================================================
//
//  		This file is generated by POGO
//	(Program Obviously used to Generate tango Object)
//
//         (c) - Software Engineering Group - ESRF
//=============================================================================


#include <tango.h>

#include <ThreadedDevice.h>
#include <ThreadedDeviceClass.h>


namespace ThreadedDevice_ns
{


//
//----------------------------------------------------------------
//	Initialize pointer for singleton pattern
//----------------------------------------------------------------
//
ThreadedDeviceClass *ThreadedDeviceClass::_instance = NULL;

//+----------------------------------------------------------------------------
//
// method : 		ThreadedDeviceClass::ThreadedDeviceClass(string &s)
// 
// description : 	constructor for the ThreadedDeviceClass
//
// in : - s : The class name
//
//-----------------------------------------------------------------------------
ThreadedDeviceClass::ThreadedDeviceClass(string &s):DeviceClass(s)
{

	cout2 << "Entering ThreadedDeviceClass constructor" << endl;
	set_default_property();
	write_class_property();
	get_class_property();
	
	cout2 << "Leaving ThreadedDeviceClass constructor" << endl;

}
//+----------------------------------------------------------------------------
//
// method : 		ThreadedDeviceClass::~ThreadedDeviceClass()
// 
// description : 	destructor for the ThreadedDeviceClass
//
//-----------------------------------------------------------------------------
ThreadedDeviceClass::~ThreadedDeviceClass()
{
	_instance = NULL;
}

//+----------------------------------------------------------------------------
//
// method : 		ThreadedDeviceClass::instance
// 
// description : 	Create the object if not already done. Otherwise, just
//			return a pointer to the object
//
// in : - name : The class name
//
//-----------------------------------------------------------------------------
ThreadedDeviceClass *ThreadedDeviceClass::init(const char *name)
{
	if (_instance == NULL)
	{
		try
		{
			string s(name);
			_instance = new ThreadedDeviceClass(s);
		}
		catch (bad_alloc)
		{
			throw;
		}		
	}		
	return _instance;
}

ThreadedDeviceClass *ThreadedDeviceClass::instance()
{
	if (_instance == NULL)
	{
		cerr << "Class is not initialised !!" << endl;
		exit(-1);
	}
	return _instance;
}

//+----------------------------------------------------------------------------
//
// method : 		ThreadedDeviceClass::command_factory
// 
// description : 	Create the command object(s) and store them in the 
//			command list
//
//-----------------------------------------------------------------------------
void ThreadedDeviceClass::command_factory()
{

	//	add polling if any
	for (unsigned int i=0 ; i<command_list.size(); i++)
	{
	}
}

//+----------------------------------------------------------------------------
//
// method : 		ThreadedDeviceClass::get_class_property
// 
// description : 	Get the class property for specified name.
//
// in :		string	name : The property name
//
//+----------------------------------------------------------------------------
Tango::DbDatum ThreadedDeviceClass::get_class_property(string &prop_name)
{
	for (int i=0 ; i<cl_prop.size() ; i++)
		if (cl_prop[i].name == prop_name)
			return cl_prop[i];
	//	if not found, return  an empty DbDatum
	return Tango::DbDatum(prop_name);
}
//+----------------------------------------------------------------------------
//
// method : 		ThreadedDeviceClass::get_default_device_property()
// 
// description : 	Return the default value for device property.
//
//-----------------------------------------------------------------------------
Tango::DbDatum ThreadedDeviceClass::get_default_device_property(string &prop_name)
{
	for (int i=0 ; i<dev_def_prop.size() ; i++)
		if (dev_def_prop[i].name == prop_name)
			return dev_def_prop[i];
	//	if not found, return  an empty DbDatum
	return Tango::DbDatum(prop_name);
}

//+----------------------------------------------------------------------------
//
// method : 		ThreadedDeviceClass::get_default_class_property()
// 
// description : 	Return the default value for class property.
//
//-----------------------------------------------------------------------------
Tango::DbDatum ThreadedDeviceClass::get_default_class_property(string &prop_name)
{
	for (int i=0 ; i<cl_def_prop.size() ; i++)
		if (cl_def_prop[i].name == prop_name)
			return cl_def_prop[i];
	//	if not found, return  an empty DbDatum
	return Tango::DbDatum(prop_name);
}
//+----------------------------------------------------------------------------
//
// method : 		ThreadedDeviceClass::device_factory
// 
// description : 	Create the device object(s) and store them in the 
//			device list
//
// in :		Tango::DevVarStringArray *devlist_ptr : The device name list
//
//-----------------------------------------------------------------------------
void ThreadedDeviceClass::device_factory(const Tango::DevVarStringArray *devlist_ptr)
{

	//	Create all devices.(Automatic code generation)
	//-------------------------------------------------------------
	for (unsigned long i=0 ; i < devlist_ptr->length() ; i++)
	{
		cout4 << "Device name : " << (*devlist_ptr)[i].in() << endl;
						
		// Create devices and add it into the device list
		//----------------------------------------------------
		device_list.push_back(new ThreadedDevice(this, (*devlist_ptr)[i]));							 

		// Export device to the outside world
		// Check before if database used.
		//---------------------------------------------
		if ((Tango::Util::_UseDb == true) && (Tango::Util::_FileDb == false))
			export_device(device_list.back());
		else
			export_device(device_list.back(), (*devlist_ptr)[i]);
	}
	//	End of Automatic code generation
	//-------------------------------------------------------------

}
//+----------------------------------------------------------------------------
//	Method: ThreadedDeviceClass::attribute_factory(vector<Tango::Attr *> &att_list)
//-----------------------------------------------------------------------------
void ThreadedDeviceClass::attribute_factory(vector<Tango::Attr *> &att_list)
{
	//	Attribute : postThisValueToTheTask
	postThisValueToTheTaskAttrib	*post_this_value_to_the_task = new postThisValueToTheTaskAttrib();
	att_list.push_back(post_this_value_to_the_task);

	//	Attribute : ramdomVector
	ramdomVectorAttrib	*ramdom_vector = new ramdomVectorAttrib();
	att_list.push_back(ramdom_vector);

}

//+----------------------------------------------------------------------------
//
// method : 		ThreadedDeviceClass::get_class_property()
// 
// description : 	Read the class properties from database.
//
//-----------------------------------------------------------------------------
void ThreadedDeviceClass::get_class_property()
{
	//	Initialize your default values here (if not done with  POGO).
	//------------------------------------------------------------------

	//	Read class properties from database.(Automatic code generation)
	//------------------------------------------------------------------
	if (Tango::Util::instance()->_UseDb==false)
		return;

	//	Call database and extract values
	//--------------------------------------------
	get_db_class()->get_property(cl_prop);
	Tango::DbDatum	def_prop;
	int	i = -1;


	//	End of Automatic code generation
	//------------------------------------------------------------------

}

//+----------------------------------------------------------------------------
//
// method : 	ThreadedDeviceClass::set_default_property
// 
// description: Set default property (class and device) for wizard.
//              For each property, add to wizard property name and description
//              If default value has been set, add it to wizard property and
//              store it in a DbDatum.
//
//-----------------------------------------------------------------------------
void ThreadedDeviceClass::set_default_property()
{
	string	prop_name;
	string	prop_desc;
	string	prop_def;

	vector<string>	vect_data;
	//	Set Default Class Properties
	//	Set Default Device Properties
}
//+----------------------------------------------------------------------------
//
// method : 		ThreadedDeviceClass::write_class_property
// 
// description : 	Set class description as property in database
//
//-----------------------------------------------------------------------------
void ThreadedDeviceClass::write_class_property()
{
	//	First time, check if database used
	//--------------------------------------------
	if (Tango::Util::_UseDb == false)
		return;

	Tango::DbData	data;
	string	classname = get_name();
	string	header;
	string::size_type	start, end;

	//	Put title
	Tango::DbDatum	title("ProjectTitle");
	string	str_title("Threaded device toolbox example");
	title << str_title;
	data.push_back(title);

	//	Put Description
	Tango::DbDatum	description("Description");
	vector<string>	str_desc;
	str_desc.push_back("Gives an example of a device threaded by inheritance");
	description << str_desc;
	data.push_back(description);
		
	//	put cvs location
	string	rcsId(RcsId);
	string	filename(classname);
	start = rcsId.find("/");
	if (start!=string::npos)
	{
		filename += "Class.cpp";
		end   = rcsId.find(filename);
		if (end>start)
		{
			string	strloc = rcsId.substr(start, end-start);
			//	Check if specific repository
			start = strloc.find("/cvsroot/");
			if (start!=string::npos && start>0)
			{
				string	repository = strloc.substr(0, start);
				if (repository.find("/segfs/")!=string::npos)
					strloc = "ESRF:" + strloc.substr(start, strloc.length()-start);
			}
			Tango::DbDatum	cvs_loc("cvs_location");
			cvs_loc << strloc;
			data.push_back(cvs_loc);
		}
	}

	//	Get CVS tag revision
	string	tagname(TagName);
	header = "$Name: ";
	start = header.length();
	string	endstr(" $");
	end   = tagname.find(endstr);
	if (end>start)
	{
		string	strtag = tagname.substr(start, end-start);
		Tango::DbDatum	cvs_tag("cvs_tag");
		cvs_tag << strtag;
		data.push_back(cvs_tag);
	}

	//	Get URL location
	string	httpServ(HttpServer);
	if (httpServ.length()>0)
	{
		Tango::DbDatum	db_doc_url("doc_url");
		db_doc_url << httpServ;
		data.push_back(db_doc_url);
	}

	//	Call database and and values
	//--------------------------------------------
	get_db_class()->put_property(data);
}

}	// namespace