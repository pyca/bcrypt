#include <sys/types.h>
#include <stdint.h>
#include <string.h>

#define explicit_bzero(s,n) memset(s, 0, n)
#define DEF_WEAK(f)

#ifndef BYTE_ORDER
#ifndef BIG_ENDIAN
#define BIG_ENDIAN 4321
#define LITTLE_ENDIAN 1234
#endif

#if (*(uint16_t *)"\0\xff" < 0x100)
#define BYTE_ORDER BIG_ENDIAN
#else
#define BYTE_ORDER LITTLE_ENDIAN
#endif
#endif

// Clang has this macro, gcc does not.
#ifndef __has_builtin
  #define __has_builtin(x) 0
#endif

// Set up swap32/swap64 macros on all supported platforms
#if __has_builtin(__builtin_bswap32) && __has_builtin(__builtin_bswap64)
#define swap32 __builtin_bswap32
#define swap64 __builtin_bswap64
#elif defined(_WIN32)
#define swap32 _byteswap_ulong
#define swap64 _byteswap_uint64
#elif defined(__APPLE__)
#include <libkern/OSByteOrder.h>
#define swap32 OSSwapInt32
#define swap64 OSSwapInt64
#elif defined(__linux__)
#include <byteswap.h>
#elif defined(__OpenBSD__)
#include <sys/endian.h>
#define swap32 __swap32
#define swap64 __swap64
#else
#define swap32(x)  ((((x) >> 24) & 0xFF) | (((x) >> 8) & 0xFF00) | (((x) & 0xFF00) << 8) | (((x) & 0xFF) << 24))
#define swap64(x)  ((swap32(((x) >> 32) & 0xFFFFFFFF)) | (swap32((x) & 0xFFFFFFFF) << 32))
#endif


int bcrypt_hashpass(const char *key, const char *salt, char *encrypted, size_t encryptedlen);
int encode_base64(char *, const u_int8_t *, size_t);
int timingsafe_bcmp(const void *b1, const void *b2, size_t n);
