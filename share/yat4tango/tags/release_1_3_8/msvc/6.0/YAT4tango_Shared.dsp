# Microsoft Developer Studio Project File - Name="YAT4tango_Shared" - Package Owner=<4>
# Microsoft Developer Studio Generated Build File, Format Version 6.00
# ** DO NOT EDIT **

# TARGTYPE "Win32 (x86) Dynamic-Link Library" 0x0102

CFG=YAT4tango_Shared - Win32 Debug
!MESSAGE This is not a valid makefile. To build this project using NMAKE,
!MESSAGE use the Export Makefile command and run
!MESSAGE 
!MESSAGE NMAKE /f "YAT4tango_Shared.mak".
!MESSAGE 
!MESSAGE You can specify a configuration when running NMAKE
!MESSAGE by defining the macro CFG on the command line. For example:
!MESSAGE 
!MESSAGE NMAKE /f "YAT4tango_Shared.mak" CFG="YAT4tango_Shared - Win32 Debug"
!MESSAGE 
!MESSAGE Possible choices for configuration are:
!MESSAGE 
!MESSAGE "YAT4tango_Shared - Win32 Release" (based on "Win32 (x86) Dynamic-Link Library")
!MESSAGE "YAT4tango_Shared - Win32 Debug" (based on "Win32 (x86) Dynamic-Link Library")
!MESSAGE 

# Begin Project
# PROP AllowPerConfigDependencies 0
# PROP Scc_ProjName ""
# PROP Scc_LocalPath ""
CPP=cl.exe
MTL=midl.exe
RSC=rc.exe

!IF  "$(CFG)" == "YAT4tango_Shared - Win32 Release"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 0
# PROP BASE Output_Dir "Release"
# PROP BASE Intermediate_Dir "Release"
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 0
# PROP Output_Dir "YAT4Tango\shared\release"
# PROP Intermediate_Dir "YAT4Tango\shared\release"
# PROP Ignore_Export_Lib 0
# PROP Target_Dir ""
# ADD BASE CPP /nologo /MT /W3 /GX /O2 /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /D "_USRDLL" /D "YAT4tango_Shared_EXPORTS" /YX /FD /c
# ADD CPP /MD /W3 /GR /GX /O2 /I "../../include" /I "../../../YAT/include" /I "$(SOLEIL_ROOT)/omniorb/include" /I "$(SOLEIL_ROOT)/tango/include" /D "WIN32" /D "NDEBUG" /D "_WINDOWS" /D "_MBCS" /D "_USRDLL" /D "YAT_DLL" /D "YAT4TANGO_BUILD" /FR /FD /c
# ADD BASE MTL /nologo /D "NDEBUG" /mktyplib203 /win32
# ADD MTL /nologo /D "NDEBUG" /mktyplib203 /win32
# ADD BASE RSC /l 0x40c /d "NDEBUG"
# ADD RSC /l 0x40c /d "NDEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib /nologo /dll /machine:I386
# ADD LINK32 tango.lib log4tango.lib omniORB407_rt.lib omniDynamic407_rt.lib omnithread32_rt.lib COS407_rt.lib kernel32.lib user32.lib gdi32.lib winspool.lib ws2_32.lib comdlg32.lib advapi32.lib shell32.lib comctl32.lib tango.lib log4tango.lib omniORB407_rt.lib omniDynamic407_rt.lib omnithread32_rt.lib COS407_rt.lib kernel32.lib user32.lib gdi32.lib winspool.lib ws2_32.lib comdlg32.lib advapi32.lib shell32.lib comctl32.lib /nologo /dll /machine:I386 /out:"..\..\bin\msvc-6.0\libYAT4Tango.dll" /implib:"..\..\lib\shared\msvc-6.0\libYAT4Tango.lib" /libpath:"$(SOLEIL_ROOT)/tango/lib/shared" /libpath:"$(SOLEIL_ROOT)/omniorb/lib/x86_win32"
# SUBTRACT LINK32 /pdb:none /nodefaultlib

!ELSEIF  "$(CFG)" == "YAT4tango_Shared - Win32 Debug"

# PROP BASE Use_MFC 0
# PROP BASE Use_Debug_Libraries 1
# PROP BASE Output_Dir "Debug"
# PROP BASE Intermediate_Dir "Debug"
# PROP BASE Target_Dir ""
# PROP Use_MFC 0
# PROP Use_Debug_Libraries 1
# PROP Output_Dir "YAT4Tango\shared\debug"
# PROP Intermediate_Dir "YAT4Tango\shared\debug"
# PROP Ignore_Export_Lib 0
# PROP Target_Dir ""
# ADD BASE CPP /nologo /MTd /W3 /Gm /GX /ZI /Od /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "_MBCS" /D "_USRDLL" /D "ADTB Shared Library_EXPORTS" /YX /FD /GZ /c
# ADD CPP /MDd /W3 /GR /GX /ZI /Od /I "../../include" /I "../../../YAT/include" /I "$(SOLEIL_ROOT)/omniorb/include" /I "$(SOLEIL_ROOT)/tango/include" /D "WIN32" /D "_DEBUG" /D "_WINDOWS" /D "_MBCS" /D "_USRDLL" /D "YAT_DLL" /D "YAT4TANGO_BUILD" /FR /FD /GZ /c
# ADD BASE MTL /nologo /D "_DEBUG" /mktyplib203 /win32
# ADD MTL /nologo /D "_DEBUG" /mktyplib203 /win32
# ADD BASE RSC /l 0x40c /d "_DEBUG"
# ADD RSC /l 0x40c /d "_DEBUG"
BSC32=bscmake.exe
# ADD BASE BSC32 /nologo
# ADD BSC32 /nologo
LINK32=link.exe
# ADD BASE LINK32 kernel32.lib user32.lib gdi32.lib winspool.lib comdlg32.lib advapi32.lib shell32.lib ole32.lib oleaut32.lib uuid.lib odbc32.lib odbccp32.lib /nologo /dll /debug /machine:I386 /pdbtype:sept
# ADD LINK32 tangod.lib log4tangod.lib omniORB407_rtd.lib omniDynamic407_rtd.lib omnithread32_rtd.lib COS407_rtd.lib kernel32.lib user32.lib gdi32.lib winspool.lib ws2_32.lib comdlg32.lib advapi32.lib shell32.lib comctl32.lib tangod.lib log4tangod.lib omniORB407_rtd.lib omniDynamic407_rtd.lib omnithread32_rtd.lib COS407_rtd.lib kernel32.lib user32.lib gdi32.lib winspool.lib ws2_32.lib comdlg32.lib advapi32.lib shell32.lib comctl32.lib /nologo /dll /debug /machine:I386 /out:"..\..\bin\msvc-6.0\libYAT4Tangod.dll" /implib:"..\..\lib\shared\msvc-6.0\libYAT4Tangod.lib" /pdbtype:sept /libpath:"$(SOLEIL_ROOT)/tango/lib/shared" /libpath:"$(SOLEIL_ROOT)/omniorb/lib/x86_win32"
# SUBTRACT LINK32 /pdb:none /nodefaultlib

!ENDIF 

# Begin Target

# Name "YAT4tango_Shared - Win32 Release"
# Name "YAT4tango_Shared - Win32 Debug"
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
