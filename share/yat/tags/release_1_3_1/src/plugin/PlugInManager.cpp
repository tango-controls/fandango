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
#include <yat/plugin/PlugInManager.h>

namespace yat
{

  PlugInManager::PlugInManager()
  {
  }


  PlugInManager::~PlugInManager()
  {
    unload_all();
  }


  std::pair<IPlugInInfo*, IPlugInFactory*>
    PlugInManager::load( const std::string &library_file_name )
  {
    //- first verify that the plugin is not already loaded
    for (PlugIns::iterator it = m_plugIns.begin(); it != m_plugIns.end(); ++it)
    {
      if ( (*it).m_fileName == library_file_name)
        return std::make_pair((*it).m_info, (*it).m_factory);
    }

    //- ok, does not already exist : load it
    PlugInEntry entry;
    entry.m_fileName = library_file_name;
    entry.m_plugin = new PlugIn( library_file_name );
    entry.m_info = entry.m_plugin->info();
    entry.m_factory = entry.m_plugin->factory();

    m_plugIns.push_back( entry );

    return std::make_pair(entry.m_info , entry.m_factory);
  }


  void 
    PlugInManager::unload( const std::string &library_file_name )
  {
    if (m_plugIns.empty())
      return;
    for ( PlugIns::iterator it = m_plugIns.begin(); it != m_plugIns.end(); ++it )
    {
      if ( (*it).m_fileName == library_file_name )
      {
        unload( *it );
        m_plugIns.erase( it );
        break;
      }
    }
  }

  void 
    PlugInManager::unload_all( void )
  {
    if (m_plugIns.empty())
      return;
    for ( PlugIns::iterator it = m_plugIns.begin(); it != m_plugIns.end(); ++it )
    {
      unload( *it );
    }
  }

  void 
    PlugInManager::unload( PlugInEntry &plugin_info )
  {
    try
    {
      delete plugin_info.m_factory;
      delete plugin_info.m_info;
      delete plugin_info.m_plugin;
    }
    catch (...)
    {
      plugin_info.m_plugin = NULL;
      throw;
    }
  }



}
