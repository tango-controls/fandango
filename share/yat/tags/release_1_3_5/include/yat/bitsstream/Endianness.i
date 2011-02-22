/*!
 * \file    
 * \brief   
 * \author  N. Leclercq, J. Malik - Synchrotron SOLEIL
 * 
 * \remarks See \link COPYING COPYING for license details \endlink
 */

namespace yat 
{

//=============================================================================
// Endianness::swap_2
//=============================================================================
inline void
Endianness::swap_2 (const char *orig, char* target)
{
#if YAT_HAS_PENTIUM == 1
# if defined(__GNUG__)
    unsigned short a = *reinterpret_cast<const unsigned short*>(orig);
    asm( "rolw $8, %0" : "=r" (a) : "0" (a) );
    *reinterpret_cast<unsigned short*>(target) = a;
# elif defined(_MSC_VER) 
    __asm mov ebx, orig;
    __asm mov ecx, target;
    __asm mov ax, [ebx];
    __asm rol ax, 8;
    __asm mov [ecx], ax;
# endif
#endif
}

//=============================================================================
// Endianness::swap_4
//=============================================================================
inline void
Endianness::swap_4 (const char* orig, char* target)
{
#if YAT_HAS_PENTIUM == 1
# if defined(__GNUG__)
    register unsigned int j = *reinterpret_cast<const unsigned int*>(orig);
    asm ("bswap %1" : "=r" (j) : "0" (j));
    *reinterpret_cast<unsigned int*>(target) = j;
# elif defined(_MSC_VER) 
    __asm mov ebx, orig;
    __asm mov ecx, target;
    __asm mov eax, [ebx];
    __asm bswap eax;
    __asm mov [ecx], eax;
# endif
#endif
}

//=============================================================================
// Endianness::swap_8
//=============================================================================
inline void
Endianness::swap_8 (const char* orig, char* target)
{
#if YAT_HAS_PENTIUM == 1
# if defined(__GNUG__)
   register unsigned int i = *reinterpret_cast<const unsigned int*>(orig);
   register unsigned int j = *reinterpret_cast<const unsigned int*>(orig + 4);
   asm ("bswap %1" : "=r" (i) : "0" (i));
   asm ("bswap %1" : "=r" (j) : "0" (j));
   *reinterpret_cast<unsigned int*>(target + 4) = i;
   *reinterpret_cast<unsigned int*>(target) = j;
# elif defined(_MSC_VER) 
   __asm mov ecx, orig;
   __asm mov edx, target;
   __asm mov eax, [ecx];
   __asm mov ebx, 4[ecx];
   __asm bswap eax;
   __asm bswap ebx;
   __asm mov 4[edx], eax;
   __asm mov [edx], ebx;
# endif
#endif
}

//=============================================================================
// Endianness::swap_16
//=============================================================================
inline void
Endianness::swap_16 (const char* orig, char* target)
{
  Endianness::swap_8(orig + 8, target);
  Endianness::swap_8(orig, target + 8);
}

} //- namespace 

