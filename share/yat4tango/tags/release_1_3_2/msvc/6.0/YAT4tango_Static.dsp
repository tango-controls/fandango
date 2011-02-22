# Microsoft Developer Studio Project File - Name="YAT4tango_Static" - Package Owner=<4>
# Microsoft Developer Studio Generated Build File, Format Version 6.00
# ** DO NOT EDIT **

# TARGTYPE "Win32 (x86) Static Library" 0x0104

CFG=YAT4tango_Static - Win32 Release
!MESSAGE This is not a valid makefile. To build this project using NMAKE,
!MESSAGE use the Export Makefile command and run
!MESSAGE 
!MESSAGE NMAKE /f "YAT4tango_Static.mak".
!MESSAGE 
!MESSAGE You can specify a configuration when running NMAKE
!MESSAGE by defining the macro CFG on the command line. For example:
!MESSAGE 
!MESSAGE NMAKE /f "YAT4tango_Static.mak" CFG="YAT4tango_Static - Win32 Release"
!MESSAGE 
!MESSAGE Possible choices for configuration are:
!MESSAGE 
!MESSAGE "YAT4tango_Static - Win32 Release" (based on "Win32 (x86) Static Library")
!MESSAGE "YAT4tango_Static - Win32 Debug" (based on "Win32 (x86) Static Library")
!MESSAGE 

# Begin Project
# PROP AllowPerConfigDependencies 0
# PROP Scc_ProjName ""
# PROP Scc_LocalPath ""
CPP=cl.exe
RSC=rc.exe

!IF  "$(CFG)" == "YAT4tango_Static - Win32 Release"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 0
# PROP BASE Output_Dir "Release"
# PROP BASE Intermediate_Dir "Release"
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 0
# PROP Output_Dir "YAT4Tango\static\release"
# PROP Intermediate_Dir "YAT4Tango\static\release"
# PROP Target_Dir ""
# ADD BASE CPP /nologo /W3 /GX /O2 /D "WIN32" /D "NDEBUG" /D "_MBCS" /D "_LIB" /YX /FD /c
# ADD CPP /MD /W3 /GR /GX /O2 /I "../../include" /I "../../../YAT/include" /I "$(SOLEIL_ROOT)/omniorb/include" /I "$(SOLEIL_ROOT)/tango/include" /I "$(SOLEIL_ROOT)/dev/include" /D "WIN32" /D "NDEBUG" /D "_MBCS" /D "_LIB" /FR /FD /Zm200 /c
# ADD BASE RSC /l 0x40c /d "NDEBUG"
# ADD RSC /l 0x40c /d "NDEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LIB32=link.exe -lib
# ADD BASE LIB32 /nologo
# ADD LIB32 /nologo /out:"..\..\lib\static\msvc-6.0\libYAT4Tango.lib"

!ELSEIF  "$(CFG)" == "YAT4tango_Static - Win32 Debug"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 1
# PROP BASE Output_Dir "Debug"
# PROP BASE Intermediate_Dir "Debug"
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 1
# PROP Output_Dir "YAT4Tango\static\debug"
# PROP Intermediate_Dir "YAT4Tango\static\debug"
# PROP Target_Dir ""
# ADD BASE CPP /nologo /W3 /Gm /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_MBCS" /D "_LIB" /YX /FD /GZ /c
# ADD CPP /MDd /W3 /GR /GX /ZI /Od /I "../../include" /I "../../../YAT/include" /I "$(SOLEIL_ROOT)/omniorb/include" /I "$(SOLEIL_ROOT)/tango/include" /I "$(SOLEIL_ROOT)/dev/include" /D "WIN32" /D "_MBCS" /D "DEBUG" /D "_LIB" /D "_DEBUG" /FR /FD /I /I /GZ /Zm200 /c
# ADD BASE RSC /l 0x40c /d "_DEBUG"
# ADD RSC /l 0x40c /d "_DEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LIB32=link.exe -lib
# ADD BASE LIB32 /nologo
# ADD LIB32 /nologo /out:"..\..\lib\static\msvc-6.0\libYAT4Tangod.lib"

!ENDIF 

# Begin Target

# Name "YAT4tango_Static - Win32 Release"
# Name "YAT4tango_Static - Win32 Debug"
# Begin Group "src"

# PROP Default_Filter ""
# Begin Source File

SOURCE=..\..\src\DynamicAttr.cpp
# End Source File
# Begin Source File

SOURCE=..\..\src\DynamicAttrHelper.cpp
# End Source File
# Begin Source File

SOURCE=..\..\src\ExceptionHelper.cpp
# End Source File
# Begin Source File

SOURCE=..\..\src\PlugInAttr.cpp
# End Source File
# Begin Source File

SOURCE=..\..\src\PlugInHelper.cpp
# End Source File
# Begin Source File

SOURCE=..\..\src\ThreadSafeDeviceProxy.cpp
# End Source File
# End Group
# Begin Group "include"

# PROP Default_Filter ""
# Begin Group "yat4tango"

# PROP Default_Filter ""
# Begin Source File

SOURCE=..\..\include\yat4tango\CommonHeader.h
# End Source File
# Begin Source File

SOURCE=..\..\include\yat4tango\DynamicAttr.h
# End Source File
# Begin Source File

SOURCE=..\..\include\yat4tango\DynamicAttr.tpp
# End Source File
# Begin Source File

SOURCE=..\..\include\yat4tango\DynamicAttrHelper.h
# End Source File
# Begin Source File

SOURCE=..\..\include\yat4tango\DynamicAttrHelper.i
# End Source File
# Begin Source File

SOURCE=..\..\include\yat4tango\ExceptionHelper.h
# End Source File
# Begin Source File

SOURCE=..\..\include\yat4tango\Export.h
# End Source File
# Begin Source File

SOURCE=..\..\include\yat4tango\PlugInAttr.h
# End Source File
# Begin Source File

SOURCE=..\..\include\yat4tango\PlugInAttr.i
# End Source File
# Begin Source File

SOURCE=..\..\include\yat4tango\PlugInAttr.tpp
# End Source File
# Begin Source File

SOURCE=..\..\include\yat4tango\PlugInHelper.h
# End Source File
# Begin Source File

SOURCE=..\..\include\yat4tango\PlugInHelper.i
# End Source File
# Begin Source File

SOURCE=..\..\include\yat4tango\ThreadSafeDeviceProxy.h
# End Source File
# Begin Source File

SOURCE=..\..\include\yat4tango\ThreadSafeDeviceProxy.i
# End Source File
# Begin Source File

SOURCE=..\..\include\yat4tango\ThreadSafeDeviceProxyHelper.h
# End Source File
# End Group
# End Group
# End Target
# End Project
