/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */
#ifndef _YAT_SINGLETON_H
#define _YAT_SINGLETON_H

namespace yat
{
  template <class T>
  class Singleton
  {
  protected: //! protected structors because this is a base class
    Singleton()
    {
    }

    virtual ~Singleton()
    {
    }

  public:
    //! static method to get the unique instance of the class
    static T& instance( void )
    {
      static T the_unique_instance;
      return the_unique_instance;
    }
  };
}

#endif
