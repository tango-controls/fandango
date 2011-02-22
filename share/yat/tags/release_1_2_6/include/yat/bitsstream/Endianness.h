/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

//=============================================================================
// original authors..Aniruddha Gokhale, Carlos O'Ryan, ... (ACE lib)
// hackers...........N. Leclercq & J. Malik - SOLEIL
//=============================================================================
// The current implementation assumes that the host has	1-byte, 2-byte and 
// 4-byte integral types, and that it has single precision and double	precision 
// IEEE floats. Those assumptions are pretty	good these days, with Crays being
// the only known exception.
//=============================================================================

#ifndef	_YAT_ENDIANNESS_H_
#define	_YAT_ENDIANNESS_H_

//=============================================================================
// DEPENDENCIES
//=============================================================================
#include <yat/CommonHeader.h>

namespace yat
{

// ============================================================================
// class: Endianness
// ============================================================================
class YAT_DECL Endianness
{
public:
  // = Constants defined by the	CDR protocol.
  // By	defining as many of these constants as possible	as enums we
  // ensure they get inlined and avoid pointless static	memory
  // allocations.

   typedef enum
   {
     BO_LITTLE_ENDIAN,
     BO_BIG_ENDIAN
   } ByteOrder;

  enum
  {
    // Note that some of these get reused as part of the standard
    // binary format: unsigned is the same size	as its signed cousin,
    // float is	LONG_SIZE, and double is LONGLONG_SIZE.
    OCTET_SIZE = 1,
    SHORT_SIZE = 2,
    LONG_SIZE =	4,
    LONGLONG_SIZE = 8,
    LONGDOUBLE_SIZE = 16,
    OCTET_ALIGN	= 1,
    SHORT_ALIGN	= 2,
    LONG_ALIGN = 4,
    LONGLONG_ALIGN = 8,
    LONGDOUBLE_ALIGN = 8,
    MAX_ALIGNMENT = 8,
  };

  //- host bytes ordering
  static const Endianness::ByteOrder host_endianness;
  static const Endianness::ByteOrder not_host_endianness;

  //- bytes ordering required for host platform
  inline static bool data_needs_bytes_reordering (const Endianness::ByteOrder & _data_bo)
  {
    return _data_bo != Endianness::host_endianness;
  };

  /**
   * Do	byte swapping for each basic IDL type size.  There exist only
   * routines to put byte, halfword (2 bytes), word (4 bytes),
   * doubleword	(8 bytes) and quadword (16 byte); because those	are
   * the IDL basic type	sizes.
   */
  static void swap_2  (const char *orig, char *target);
  static void swap_4  (const char *orig, char *target);
  static void swap_8  (const char *orig, char *target);
  static void swap_16 (const char *orig, char *target);

  static void swap_2_array  (const char *orig, char *target, size_t length);
  static void swap_4_array  (const char *orig, char *target, size_t length);
  static void swap_8_array  (const char *orig, char *target, size_t length);
  static void swap_16_array (const char	*orig, char *target, size_t length);
};

} //- namespace 

//=============================================================================
// INLINED CODE
//=============================================================================
#if defined (YAT_INLINE_IMPL)
# include <yat/bitsstream/Endianness.i>
#endif // YAT_INLINE_IMPL

#endif //- _ENDIANNESS_H_
