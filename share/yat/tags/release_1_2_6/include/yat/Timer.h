/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

#ifndef _YAT_TIMER_H_
#define _YAT_TIMER_H_

#include <yat/CommonHeader.h>


// ============================================================================
// TIME MACROS
// ============================================================================
#include <ctime>
#if defined (YAT_WIN32)
# include <sys/timeb.h>
# include <time.h>
#else
# include <sys/time.h>
#endif

typedef struct _timeval
{
  int tv_sec;
  int tv_usec;
  time_t tv_utc;
  _timeval ()
    : tv_sec(0), tv_usec(0), tv_utc(0) {}
} _timeval;
# define _TIMESTAMP _timeval

#if defined (YAT_WIN32)
  typedef struct
  {
    int tv_sec;
    int tv_nsec;
  } _timespec;
# define _TIMESPEC _timespec
#else
# define _TIMESPEC timespec
#endif

#if defined (YAT_WIN32)	
# define _GET_TIME(T) \
  do \
  { \
    struct _timeb _timeb_now; \
    ::_ftime(&_timeb_now); \
    T.tv_sec = static_cast<int>(_timeb_now.time); \
    T.tv_usec = static_cast<int>(1000 * _timeb_now.millitm); \
    ::time(&T.tv_utc); \
  } while (0)
#else
# define _GET_TIME(T) \
  do \
  { \
    struct timeval _now; \
    ::gettimeofday(&_now, 0); \
    T.tv_sec = _now.tv_sec; \
    T.tv_usec = _now.tv_usec; \
    ::time(&T.tv_utc); \
  } while (0)
#endif

# define _MAX_DATE_LEN 256
# define _TIMESTAMP_TO_DATE(T,S) \
  do \
  { \
    struct tm * tmv = ::localtime(&T.tv_utc); \
    char b[_MAX_DATE_LEN]; \
    ::memset(b, 0, _MAX_DATE_LEN); \
    ::strftime(b, _MAX_DATE_LEN, "%a, %d %b %Y %H:%M:%S", tmv); \
    S = std::string(b); \
  } while (0)
# define	_RESET_TIMESTAMP(T) \
  do \
  { \
    T.tv_sec = 0; \
    T.tv_usec = 0; \
    T.tv_utc = 0; \
  } while (0)
# define	_COPY_TIMESTAMP(S, D) \
  do \
  { \
    D.tv_sec = S.tv_sec; \
    D.tv_usec = S.tv_usec; \
    D.tv_utc = S.tv_utc; \
  } while (0)
  
  
#define	_ELAPSED_SEC(B, A) \
  static_cast<double>((A.tv_sec - B.tv_sec) + (1.E-6 * (A.tv_usec - B.tv_usec)))

#define	_ELAPSED_MSEC(B, A) _ELAPSED_SEC(B, A) * 1.E3

#define	_ELAPSED_USEC(B, A) _ELAPSED_SEC(B, A) * 1.E6

#define _IS_VALID_TIMESTAMP(T) T.tv_sec != 0 || T.tv_usec != 0

#define	_TMO_EXPIRED(B, A, TMO) _ELAPSED_SEC (B, A) > TMO


#if defined (YAT_WIN32)
  namespace std 
  { 
    using ::clock_t; 
    using ::clock; 
  }
#endif

namespace yat
{
  typedef _TIMESTAMP Timestamp;
  typedef _TIMESPEC  Timespec;

#if ! defined (YAT_WIN32)	
  //- timer  -------------------------------------------------------------------
  //  A timer object measures elapsed time.
  //  It is recommended that implementations measure wall clock rather than CPU
  //  time since the intended use is performance measurement on systems where
  //  total elapsed time is more important than just process or CPU time.
  //  Warnings: The maximum measurable elapsed time may well be only 596.5+ hours
  //  due to implementation limitations.  The accuracy of timings depends on the
  //  accuracy of timing information provided by the underlying platform, and
  //  this varies a great deal from platform to platform.
  //----------------------------------------------------------------------------
  class Timer
  {
  public:
    Timer () 
    { 
      _start_time = std::clock(); 
    } 
    
    void restart() 
    {
      _start_time = std::clock(); 
    }

    //- return elapsed time in seconds
    double elapsed_sec ()            
    { 
      return  double(std::clock() - _start_time) / CLOCKS_PER_SEC; 
    }

    //- return elapsed time in milliseconds
    double elapsed_msec ()            
    { 
      return  1.E3 * double(std::clock() - _start_time) / CLOCKS_PER_SEC; 
    }

    //- return elapsed time in microseconds
    double elapsed_usec ()             
    { 
      return  1.E6 * double(std::clock() - _start_time) / CLOCKS_PER_SEC; 
    }

  private:
    std::clock_t _start_time;
  };
  
#else // ! YAT_WIN32

  class Timer 
  {
  private:
      LARGE_INTEGER _start;
      LARGE_INTEGER _stop;
      LARGE_INTEGER _frequency;
      inline double li_to_secs( LARGE_INTEGER & li)
      {
        return (double)li.QuadPart / (double)_frequency.QuadPart;
      }
      
  public:
      Timer () 
      {
        _start.QuadPart = 0;
        _stop.QuadPart = 0;
        ::QueryPerformanceFrequency(&_frequency);
        ::QueryPerformanceCounter(&_start);
      }
      
      void restart() 
      {
        ::QueryPerformanceCounter(&_start) ;
      }
      
      //- return elapsed time in seconds
      double elapsed_sec ()             
      { 
        ::QueryPerformanceCounter(&_stop);
        LARGE_INTEGER dt;
        dt.QuadPart = _stop.QuadPart - _start.QuadPart;
        return li_to_secs(dt);
      }

      //- return elapsed time in milliseconds
      double elapsed_msec ()           
      { 
        return  1.E3 * elapsed_sec (); 
      }

      //- return elapsed time in microseconds
      double elapsed_usec ()            
      { 
        return  1.E6 * elapsed_sec (); 
      }
  };
#endif // ! YAT_WIN32
}

#endif
