/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_EXCEPTION_H_
#define _YAT_EXCEPTION_H_

// ============================================================================
// DEPENDENCIES
// ============================================================================
#include <string>
#include <vector>
#include <yat/CommonHeader.h>

namespace yat 
{

#define THROW_YAT_ERROR( reason, desc, origin ) \
  throw yat::Exception( (reason), (desc), (origin) )

#define RETHROW_YAT_ERROR( exception, reason, desc, origin ) \
  { \
    exception.push_error( (reason), (desc), (origin) ); \
    throw exception; \
  }

  // ============================================================================
  // Error Severity
  // ============================================================================
  typedef enum {
    WARN, 
    ERR, 
    PANIC
  } ErrorSeverity;

  // ============================================================================
  //! The Error class
  // ============================================================================
  //!  
  //! detailed description to be written
  //!
  // ============================================================================
  struct YAT_DECL Error
  {
    /**
    * Initialization. 
    */
    Error (void);

    /**
    * Initialization. 
    */
    Error ( const char *reason,
            const char *desc,
            const char *origin,
            int err_code = -1, 
            int severity = yat::ERR);
    /**
    * Initialization. 
    */
    Error ( const std::string& reason,
            const std::string& desc,
            const std::string& origin, 
            int err_code = -1, 
            int severity = yat::ERR);

    /**
    * Copy constructor. 
    */
    Error (const Error& src);

    /**
    * Error details: code 
    */
    virtual ~Error (void);

    /**
    * operator= 
    */
    Error& operator= (const Error& _src);

    /**
    * Error details: reason 
    */
    std::string reason;

    /**
    * Error details: description 
    */
    std::string desc;

    /**
    * Error details: origin 
    */
    std::string origin;

    /**
    * Error details: code 
    */
    int code;

    /**
    * Error details: severity 
    */
    int severity;
  };

  // ============================================================================
  //! The Exception class
  // ============================================================================
  //!  
  //! detailed description to be written
  //!
  // ============================================================================
  class YAT_DECL Exception
  {
  public:

    typedef std::vector<Error> ErrorList;

    /**
    * Ctor
    */
    Exception (void);

    /**
    * Ctor
    */
    Exception ( const char *reason,
                const char *desc,
                const char *origin,
                int err_code = -1, 
                int severity = yat::ERR);

    /**
    * Ctor
    */
    Exception ( const std::string& reason,
                const std::string& desc,
                const std::string& origin, 
                int err_code = -1, 
                int severity = yat::ERR);

    /**
    * Ctor
    */
    Exception (const Error& error);

    /**
    * Copy ctor
    */
    Exception (const Exception& src);

    /**
    * operator=
    */
    Exception& operator= (const Exception& _src); 

    /**
    * Dtor
    */
    virtual ~Exception (void);

    /**
    * Push the specified error into the errors list.
    */
    void push_error ( const char *reason,
                      const char *desc,
                      const char *origin, 
                      int err_code = -1, 
                      int severity = yat::ERR);

    /**
    * Push the specified error into the errors list.
    */
    void push_error ( const std::string& reason,
                      const std::string& desc,
                      const std::string& origin, 
                      int err_code = -1, 
                      int severity = yat::ERR);

    /**
    * Push the specified error into the errors list.
    */
    void push_error (const Error& error);
    
    /**
    * Dump.
    */
    virtual void dump (void) const;

    /**
    * The errors list
    */
    ErrorList errors;
  };

} // namespace

/*
#if defined (YAT_INLINE_IMPL)
# include <yat/Exception.i>
#endif // YAT_INLINE_IMPL
*/

#endif // _MESSAGE_H_
