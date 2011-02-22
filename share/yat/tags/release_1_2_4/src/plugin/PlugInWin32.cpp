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

#ifdef YAT_WIN32


namespace yat
{

  PlugIn::LibraryHandle 
    PlugIn::do_load_library( const std::string &library_file_name )
  {
    return ::LoadLibrary( library_file_name.c_str() );
  }


  void 
    PlugIn::do_release_library()
  {
    ::FreeLibrary( static_cast<HINSTANCE>(m_libraryHandle) );
  }


  PlugIn::Symbol 
    PlugIn::do_find_symbol( const std::string &symbol )
  {
    FARPROC far_proc = ::GetProcAddress( static_cast<HINSTANCE>(m_libraryHandle), 
                                         symbol.c_str() );
    return static_cast<PlugIn::Symbol>(far_proc);
  }


  std::string 
    PlugIn::get_last_error_detail() const
  {
    LPVOID lp_msg_buf;
    ::FormatMessage( 
                    FORMAT_MESSAGE_ALLOCATE_BUFFER | 
                    FORMAT_MESSAGE_FROM_SYSTEM | 
                    FORMAT_MESSAGE_IGNORE_INSERTS,
                    NULL,
                    ::GetLastError(),
                    MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), // Default language
                    (LPTSTR) &lp_msg_buf,
                    0,
                    NULL 
                    );

    std::string message = (LPCTSTR)lp_msg_buf;

    // Free the buffer.
    ::LocalFree( lp_msg_buf );

    return message;
  }


}


#endif