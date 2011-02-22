## Process this file with automake to produce Makefile.in

lib_LTLIBRARIES = libyat.la

libyat_la_LDFLAGS = -version-info 1:0:0 \
                    $(YAT_LIBS) \
                    $(TANGO_LIBS)

libyat_la_CXXFLAGS = -I$(top_srcdir)/include \
                    $(YAT_CFLAGS) \
                    $(TANGO_CFLAGS)

libyat_la_SOURCES = \
	DeviceTask.cpp \
	DynamicAttr.cpp \
	DynamicAttrHelper.cpp \
	PlugInAttr.cpp \
	PlugInHelper.cpp \
	ThreadSafeDeviceProxy.cpp \
	MonitoredAttribute.cpp \
	MonitoredDevice.cpp \
	MonitoredDeviceTask.cpp


