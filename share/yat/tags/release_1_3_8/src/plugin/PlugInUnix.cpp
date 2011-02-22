/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat/plugin/PlugIn.h>


#if defined(YAT_LINUX) || defined(YAT_MACOSX)

#include <dlfcn.h>
#include <unistd.h>


namespace yat
{


  PlugIn::LibraryHandle 
    PlugIn::do_load_library( const std::string &library_file_name )
  {
    return ::dlopen( library_file_name.c_str(), RTLD_NOW | RTLD_GLOBAL );
  }


  void 
    PlugIn::do_release_library()
  {
    ::dlclose( m_libraryHandle);
  }


  PlugIn::Symbol 
    PlugIn::do_find_symbol( const std::string &symbol )
  {
    return ::dlsym ( m_libraryHandle, symbol.c_str() );
  }


  std::string 
    PlugIn::get_last_error_detail() const
  {
    return "";
  }


}


#endif
