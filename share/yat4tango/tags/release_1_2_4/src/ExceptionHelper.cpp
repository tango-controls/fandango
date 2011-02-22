// ============================================================================
//
// = CONTEXT
//    TANGO Project - ImgBeamAnalyzer DeviceServer - Data class
//
// = File
//    Data.cpp
//
// = AUTHOR
//    Julien Malik
//
// ============================================================================

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <yat4tango/ExceptionHelper.h>

namespace yat4tango
{
  YATDevFailed::YATDevFailed(const yat::Exception& ex)
  {
    const yat::Exception::ErrorList& yat_errors = ex.errors;
    errors.length( yat_errors.size() );
    for (size_t i = 0; i < errors.length(); i++)
    {
      errors[i].reason = CORBA::string_dup( yat_errors[i].reason.c_str() );
      errors[i].desc   = CORBA::string_dup( yat_errors[i].desc.c_str()   );
      errors[i].origin = CORBA::string_dup( yat_errors[i].origin.c_str() );
      switch (yat_errors[i].severity)
      {
        case yat::WARN:
          errors[i].severity = Tango::WARN;
          break;
        case yat::PANIC:
          errors[i].severity = Tango::PANIC;
          break;
        case yat::ERR:
        default:
          errors[i].severity = Tango::ERR;
          break;
      }
    }
  }


  TangoYATException::TangoYATException( const Tango::DevFailed& df )
  {
    const Tango::DevErrorList& tango_err_list = df.errors;
    for (size_t i = 0; i < tango_err_list.length(); i++) 
    {
      Tango::ErrSeverity df_sev = df.errors[i].severity;
      yat::ErrorSeverity yat_sev = (df_sev == Tango::WARN ? yat::WARN
                                    : (df_sev == Tango::ERR ? yat::ERR
                                       : (df_sev == Tango::PANIC ? yat::PANIC
                                          : yat::ERR)));
      
      this->push_error( df.errors[i].reason,
                        df.errors[i].desc,
                        df.errors[i].origin,
                        -1,
                        yat_sev);
    }
  }
}
