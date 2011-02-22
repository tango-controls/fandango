//----------------------------------------------------------------------------
// YAT LIBRARY
//----------------------------------------------------------------------------
//
// Copyright (C) 2006-2009  The Tango Community
//
// Part of the code comes from the ACE Framework
// see http://www.cs.wustl.edu/~schmidt/ACE.html for more about ACE
//
// The thread native implementation has been initially inspired by omniThread
// - the threading support library that comes with omniORB. 
// see http://omniorb.sourceforge.net/ for more about omniORB.
// Contributors form the TANGO community:
// Ramon Sunes (ALBA) 
// The YAT library is free software; you can redistribute it and/or modify it 
// under the terms of the GNU General Public License as published by the Free 
// Software Foundation; either version 2 of the License, or (at your option) 
// any later version.
//
// The YAT library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
// Public License for more details.
//
// A copy of the GPL version 2 is available below. 
//
// Contact:
//      Nicolas Leclercq
//      Synchrotron SOLEIL
//------------------------------------------------------------------------------

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
# define  _RESET_TIMESTAMP(T) \
  do \
  { \
    T.tv_sec = 0; \
    T.tv_usec = 0; \
    T.tv_utc = 0; \
  } while (0)
# define  _COPY_TIMESTAMP(S, D) \
  do \
  { \
    D.tv_sec = S.tv_sec; \
    D.tv_usec = S.tv_usec; \
    D.tv_utc = S.tv_utc; \
  } while (0)
  
  
#define  _ELAPSED_SEC(B, A) \
  static_cast<double>((A.tv_sec - B.tv_sec) + (1.E-6 * (A.tv_usec - B.tv_usec)))

#define  _ELAPSED_MSEC(B, A) _ELAPSED_SEC(B, A) * 1.E3

#define  _ELAPSED_USEC(B, A) _ELAPSED_SEC(B, A) * 1.E6

#define _IS_VALID_TIMESTAMP(T) T.tv_sec != 0 || T.tv_usec != 0

#define  _TMO_EXPIRED(B, A, TMO) _ELAPSED_SEC (B, A) > TMO


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
  // ============================================================================
  // class Timer
  // ============================================================================
  class Timer
  {
  public:
    Timer () 
    { 
      this->restart();
    } 
    
    void restart() 
    {
      ::gettimeofday(&m_start_time, NULL); 
    }

    //- return elapsed time in seconds
    double elapsed_sec () const             
    { 
      struct timeval now;
      ::gettimeofday(&now, NULL);
      return (now.tv_sec - m_start_time.tv_sec) + 1e-6 * (now.tv_usec - m_start_time.tv_usec);
    }

    //- return elapsed time in milliseconds
    double elapsed_msec () const             
    { 
      struct timeval now;
      ::gettimeofday(&now, NULL);
      return 1e3 * (now.tv_sec - m_start_time.tv_sec) + 1e-3 * (now.tv_usec - m_start_time.tv_usec);
    }

    //- return elapsed time in microseconds
    double elapsed_usec () const             
    { 
      struct timeval now;
      ::gettimeofday(&now, NULL);
      return 1e6 * (now.tv_sec - m_start_time.tv_sec) + (now.tv_usec - m_start_time.tv_usec);
    }

  private:
    struct timeval m_start_time;
  };
#else // ! YAT_WIN32
  // ============================================================================
  // class Timer
  // ============================================================================
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
