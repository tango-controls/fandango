/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_XSTRING_H_
#define _YAT_XSTRING_H_

//=============================================================================
// DEPENDENCIES
//=============================================================================
#include <yat/CommonHeader.h>

namespace yat 
{

// ============================================================================
// XString class
// ============================================================================
template <typename _T>
class XString
{

public:	
	
  //- converts string content to numeric type _T
  //- should also work for any "istringstream::operator>>" supported type
  //---------------------------------------------------------------------
	static _T to_num (const std::string& _s, bool _throw = true)
	{
		ISStream iss(_s.c_str());

		_T num_val;

		if ( (iss >> num_val) == false )
    {
      if (_throw)
      {
        OSStream desc;
        desc << "conversion from string to num failed [" 
             << _s
             << "]"
             << std::ends;
		    THROW_YAT_ERROR ("SOFTWARE_ERROR",
											   desc.str().c_str(),
											   "XString::to_num");
      }
      return 0;
    }

    return num_val;
	} 

  //- converts from type _T to std::string
  //---------------------------------------------------------------------
	static std::string to_string (const _T & _t, bool _throw = true)
	{
		OSStream oss;

    if ( (oss << std::fixed << _t) == false )
    {
      if (_throw)
      {
        OSStream desc;
        desc << "conversion from num to string failed [" 
             << _t
             << "]"
             << std::ends;
		    THROW_YAT_ERROR ("SOFTWARE_ERROR",
											   desc.str().c_str(),
											   "XString::to_string");
      }
      return std::string("");
    }

    return oss.str();
	} 

};

} //- namespace

#endif // _XSTRING_H_
