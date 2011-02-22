/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_PORTABILITY_H_
#define _YAT_PORTABILITY_H_

#if (defined(WIN32) || defined(_WIN32))
#  include <yat/config-win32.h>

#elif defined(_linux_) || defined (__linux__)
#  include <yat/config-linux.h>

#else
//?????? SUNOS ????????
#endif



/**
 *  Define portable string streams
 */
#ifdef YAT_HAS_SSTREAM

# include <sstream>
  namespace yat
  {
    typedef std::ostringstream OSStream;
    typedef std::istringstream ISStream;
    typedef std::stringstream  SStream;
  }

#else

# include <string>
# include <strstream>

  namespace yat
  {
    class OSStream : public std::ostrstream
    {
    public:
      std::string str()
      {
        //- in case it is not already done, add an 'end of string' character
        (*this) << '\0'; 
        //- create a string containing the data of the strstream
        std::string ret(std::ostrstream::str()); 
        //- call freeze such that the std::ostrstream will delete its internal string
        std::ostrstream::freeze(false);
        return ret;
      }
    };

    class ISStream : public std::istrstream
    {
    public:
      std::string str()
      {
        //- in case it is not already done, add an 'end of string' character
        (*this) << '\0'; 
        //- create a string containing the data of the strstream
        std::string ret(std::istrstream::str()); 
        //- call freeze such that the std::istrstream will delete its internal string
        std::istrstream::freeze(false);
        return ret;
      }
    };

    class SStream : public std::strstream
    {
    public:
      std::string str()
      {
        //- in case it is not already done, add an 'end of string' character
        (*this) << '\0'; 
        //- create a string containing the data of the strstream
        std::string ret(std::strstream::str()); 
        //- call freeze such that the std::strstream will delete its internal string
        std::strstream::freeze(false);
        return ret;
      }
    };
  }
#endif

#endif
