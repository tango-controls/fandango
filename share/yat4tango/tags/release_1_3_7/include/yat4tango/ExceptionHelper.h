/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT4TANGO_EXCEPTION_HELPER_H_
#define _YAT4TANGO_EXCEPTION_HELPER_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat4tango/CommonHeader.h>
#include <yat/Exception.h>

//-----------------------------------------------------------------------------
// WINDOWS PRAGMA
//-----------------------------------------------------------------------------
#if defined (WIN32)
# pragma warning (disable : 4286)
#endif

#define _CPTC(X) static_cast<const char*>(X)

//=============================================================================
// THROW_DEVFAILED MACRO
//=============================================================================
#define THROW_DEVFAILED(p, q, r) \
  Tango::Except::throw_exception(_CPTC(p), _CPTC(q), _CPTC(r))

//=============================================================================
// RETHROW_DEVFAILED
//=============================================================================
#define RETHROW_DEVFAILED(ex, p, q, r) \
  Tango::Except::re_throw_exception(ex, _CPTC(p), _CPTC(q), _CPTC(r))

//=============================================================================
// _YAT_TO_TANGO_EXCEPTION MACRO
//=============================================================================
#define _YAT_TO_TANGO_EXCEPTION(_yat_ex, _tango_ex) \
  const yat::Exception::ErrorList & ael = _yat_ex.errors; \
  Tango::DevErrorList tel(ael.size()); \
  tel.length(ael.size()); \
  for (size_t _ii = 0; _ii < ael.size(); _ii++) \
  { \
    tel[_ii].reason = CORBA::string_dup(ael[_ii].reason.c_str()); \
    tel[_ii].desc   = CORBA::string_dup(ael[_ii].desc.c_str()); \
    tel[_ii].origin = CORBA::string_dup(ael[_ii].origin.c_str()); \
    switch (ael[_ii].severity) \
    { \
      case yat::WARN: \
        tel[_ii].severity = Tango::WARN; \
        break; \
      case yat::PANIC: \
        tel[_ii].severity = Tango::PANIC; \
        break; \
      case yat::ERR: \
      default: \
        tel[_ii].severity = Tango::ERR; \
        break; \
    } \
  } \
  Tango::DevFailed _tango_ex(tel)

//=============================================================================
// THROW_YAT_TO_TANGO_EXCEPTION MACRO
//=============================================================================
#define THROW_YAT_TO_TANGO_EXCEPTION(_yat_ex) \
  _YAT_TO_TANGO_EXCEPTION(_yat_ex, _tango_ex); \
  throw _tango_ex

//=============================================================================
// _HANDLE_YAT_EXCEPTION MACRO
//=============================================================================
#define _HANDLE_YAT_EXCEPTION(_cmd, _origin) \
  catch (const yat::Exception& _yat_ex) \
  { \
    _YAT_TO_TANGO_EXCEPTION(_yat_ex, _tango_ex); \
    TangoSys_OMemStream r; \
    r << _cmd \
      << " failed" \
      << std::ends; \
    TangoSys_OMemStream d; \
    d << "YAT Exception caught while trying to execute " \
      << _cmd \
      << std::ends; \
    TangoSys_OMemStream o; \
    o << _origin \
      << " [" \
      << __FILE__ \
      << "::" \
      << __LINE__ \
      << "]" \
      << std::ends; \
    Tango::Except::re_throw_exception(_tango_ex, \
                                      _CPTC(r.str().c_str()), \
				                              _CPTC(d.str().c_str()), \
				                              _CPTC(o.str().c_str())); \
  } \
  catch (...) \
  { \
    TangoSys_OMemStream r; \
    r << _cmd \
      << " failed [UNKNOWN_ERROR]" \
      << std::ends; \
    TangoSys_OMemStream d; \
    d << "unknown exception caught while trying to execute " \
      << _cmd \
      << std::ends; \
    TangoSys_OMemStream o; \
    o << _origin \
      << " [" \
      << __FILE__ \
      << "::" \
      << __LINE__ \
      << "]" \
      << std::ends; \
    Tango::DevErrorList errors(1); \
    errors.length(1); \
    errors[0].severity = Tango::ERR; \
    errors[0].reason = CORBA::string_dup(r.str().c_str()); \
    errors[0].desc = CORBA::string_dup(d.str().c_str()); \
    errors[0].origin = CORBA::string_dup(o.str().c_str()); \
    Tango::DevFailed _tango_ex(errors); \
    throw _tango_ex; \
  }

//=============================================================================
// _TANGO_TO_YAT_EXCEPTION MACRO
//=============================================================================
#define _TANGO_TO_YAT_EXCEPTION(_tango_ex, _yat_ex) \
  const Tango::DevErrorList & tel = _tango_ex.errors; \
  yat::Exception::ErrorList yel(tel.length()); \
  for (size_t _ii = 0; _ii < yel.size(); _ii++) \
  { \
    yel[_ii].reason = std::string(tel[_ii].reason); \
    yel[_ii].desc   = std::string(tel[_ii].desc); \
    yel[_ii].origin = std::string(tel[_ii].origin); \
    switch (tel[_ii].severity) \
    { \
      case Tango::WARN: \
        yel[_ii].severity = yat::WARN; \
        break; \
      case Tango::PANIC: \
       yel[_ii].severity = yat::PANIC; \
        break; \
      case Tango::ERR: \
      default: \
        yel[_ii].severity = yat::ERR; \
        break; \
    } \
  } \
  yat::Exception _yat_ex; \
  _yat_ex.errors = yel;
  
namespace yat4tango
{
#ifdef YAT_WIN32
#  pragma warning( push )
#  pragma warning( disable: 4275 )
#endif

  /*
   *
   */
  class YAT4TANGO_DECL YATDevFailed : public Tango::DevFailed
  {
  public:
    YATDevFailed( const yat::Exception& ex );
  };

  /*
   *
   */
  class YAT4TANGO_DECL TangoYATException : public yat::Exception
  {
  public:
    TangoYATException( const Tango::DevFailed& );
  };


#ifdef YAT_WIN32
#  pragma warning( pop )
#endif

} // namespace


#endif // _EXCEPTION_HELPER_H_



