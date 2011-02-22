## Process this file with automake to produce Makefile.in

AM_LDFLAGS = -version-info 1:0:0 \
	$(YAT_LIBS) \
	$(TANGO_LIBS)

AM_CXXFLAGS = -I$(top_srcdir)/include \
	$(YAT_CFLAGS) \
	$(TANGO_CFLAGS)

lib_LTLIBRARIES = libyat4tango.la

libyat4tango_la_SOURCES = \
	DeviceTask.cpp \
	DynamicAttr.cpp \
	DynamicAttrHelper.cpp \
	ExceptionHelper.cpp \
	PlugInAttr.cpp \
	PlugInHelper.cpp \
	ThreadSafeDeviceProxy.cpp \
	MonitoredAttribute.cpp \
	MonitoredDevice.cpp \
	MonitoredDeviceTask.cpp

# Support for GNU Flymake, in Emacs.
check-syntax: AM_CXXFLAGS += -fsyntax-only -pipe
check-syntax:
	test -z "$(CHK_SOURCES)" || $(CXXCOMPILE) $(CHK_SOURCES)

.PHONY: check-syntax
