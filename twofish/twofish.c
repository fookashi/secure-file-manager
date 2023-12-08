#include "twofish.h"
#include "stdio.h"
#include "stdlib.h"


#define UINT32_MASK    ( (((uint32_t)2)<<31) - 1 )
#define ROL32( x, n )  ( (x)<<(n) | ((x) & UINT32_MASK) >> (32-(n)) )
#define ROR32( x, n )  ( (x)>>(n) | ((x) & UINT32_MASK) << (32-(n)) )

#define b0(X) (X & 0xff)
#define b1(X) ((X >> 8) & 0xff)
#define b2(X) ((X >> 16) & 0xff)
#define b3(X) ((X >> 24) & 0xff)

#define GET32( p ) \
( (uint32_t)((p)[0]) | (uint32_t)((p)[1])<< 8 | (uint32_t)((p)[2])<<16 | (uint32_t)((p)[3])<<24 )

#define PUT32( v, p ) \
(p)[0] = (uint8_t)(((v)) & 0xff); (p)[1] = (uint8_t)(((v) >>  8) & 0xff); (p)[2] = (uint8_t)(((v) >> 16) & 0xff); (p)[3] = (uint8_t)(((v) >> 24) & 0xff)


#define q0  Q[0]
#define q1  Q[1]


#define H02( y, L )  MDS[0][q0[q0[y]^L[ 8]]^L[0]]
#define H12( y, L )  MDS[1][q0[q1[y]^L[ 9]]^L[1]]
#define H22( y, L )  MDS[2][q1[q0[y]^L[10]]^L[2]]
#define H32( y, L )  MDS[3][q1[q1[y]^L[11]]^L[3]]
#define H03( y, L )  H02( q1[y]^L[16], L )
#define H13( y, L )  H12( q1[y]^L[17], L )
#define H23( y, L )  H22( q0[y]^L[18], L )
#define H33( y, L )  H32( q0[y]^L[19], L )
#define H04( y, L )  H03( q1[y]^L[24], L )
#define H14( y, L )  H13( q0[y]^L[25], L )
#define H24( y, L )  H23( q0[y]^L[26], L )
#define H34( y, L )  H33( q1[y]^L[27], L )



static uint32_t h( int k, uint8_t L[], int kCycles )
{
  switch( kCycles ) {

    case 2:
      return H02(k,L) ^ H12(k,L) ^ H22(k,L) ^ H32(k,L);
    case 3:
      return H03(k,L) ^ H13(k,L) ^ H23(k,L) ^ H33(k,L);
    case 4:
      return H04(k,L) ^ H14(k,L) ^ H24(k,L) ^ H34(k,L);
    default:
      break;
  }
}



static void fill_keyed_sboxes( uint8_t S[], int kCycles, twofish_key * xkey )
{
  int i;
  switch( kCycles ) {

    case 2:
      for( i=0; i<256; i++ )
      {
        xkey->s[0][i]= H02( i, S );
        xkey->s[1][i]= H12( i, S );
        xkey->s[2][i]= H22( i, S );
        xkey->s[3][i]= H32( i, S );
      }
      break;
    case 3:
      for( i=0; i<256; i++ )
      {
        xkey->s[0][i]= H03( i, S );
        xkey->s[1][i]= H13( i, S );
        xkey->s[2][i]= H23( i, S );
        xkey->s[3][i]= H33( i, S );
      }
      break;
    case 4:
      for( i=0; i<256; i++ )
      {
        xkey->s[0][i]= H04( i, S );
        xkey->s[1][i]= H14( i, S );
        xkey->s[2][i]= H24( i, S );
        xkey->s[3][i]= H34( i, S );
      }
      break;
    default:
      break;
  }
}

uint8_t gf_mult(uint8_t a, uint8_t b) {
    uint8_t result = 0;
    uint8_t carry;

    for (int i = 0; i < 8; i++) {
        if (b & 1) {
            result ^= a;
        }
        if (a > (a ^ IRRED_POLY)) {
            a ^= IRRED_POLY;
        }
        a <<= 1;
        b >>= 1;
    }

    return result;
}

void gf_mult_matrix(uint8_t* vector, uint8_t* matrix, uint8_t* result) {
    for (int i = 0; i < 4; i++) {
        result[i] = 0;
        for (int j = 0; j < 4; j++) {
            result[i] ^= gf_mult(vector[j], matrix[i * 8 + j]);
        }
    }
}


twofish_key* generate_key(uint8_t key[], int key_len){

  twofish_key* xkey = (twofish_key*) malloc(sizeof(twofish_key));
  
  int kCycles = key_len * 8 / 64;

  uint8_t K[key_len+kCycles*8];
  uint32_t A, B;
  
  uint8_t * kptr;
  uint8_t * sptr;
  

  memcpy( K, key, key_len );
  memset( K+key_len, 0, sizeof(K)-key_len );
  
  for(int i=0; i<40; i+=2 )
  {
    A = h(i, K, kCycles);
    B = h(i+1, K+4, kCycles);
    B = ROL32(B, 8);

    A += B;
    B += A;
    xkey->K[i] = A;
    xkey->K[i+1] = ROL32(B, 9);
  }

  A=B=0;
  kptr = K + key_len;
  sptr = K + key_len;
  
    while (kptr > K) {
        kptr -= 8;
        memcpy(sptr, kptr, 8);
        uint8_t temp_result[4];
        gf_mult_matrix(sptr, RS, sptr);

        sptr += 8;
    }
  
  fill_keyed_sboxes( K + key_len, kCycles, xkey );
  
  memset( K, 0, sizeof( K ) );
  return xkey;
}


#define g0(X,xkey) \
(xkey->s[0][b0(X)]^xkey->s[1][b1(X)]^xkey->s[2][b2(X)]^xkey->s[3][b3(X)])

#define g1(X,xkey) \
(xkey->s[0][b3(X)]^xkey->s[1][b0(X)]^xkey->s[2][b1(X)]^xkey->s[3][b2(X)])


#define ENCRYPT_RND( A,B,C,D, T0, T1, xkey, r ) \
T0 = g0(A,xkey); T1 = g1(B,xkey);\
C ^= T0+T1+xkey->K[8+2*(r)]; C = ROR32(C,1);\
D = ROL32(D,1); D ^= T0+2*T1+xkey->K[8+2*(r)+1]

#define ENCRYPT_CYCLE( A, B, C, D, T0, T1, xkey, r ) \
ENCRYPT_RND( A,B,C,D,T0,T1,xkey,2*(r)   );\
ENCRYPT_RND( C,D,A,B,T0,T1,xkey,2*(r)+1 )

#define ENCRYPT( A, B, C, D, T0, T1, xkey ) \
for (int i = 0; i < 8; i++) \
{ENCRYPT_CYCLE(A, B, C, D, T0, T1, xkey, i);}\



#define DECRYPT_RND( A,B,C,D, T0, T1, xkey, r ) \
T0 = g0(A,xkey); T1 = g1(B,xkey);\
C = ROL32(C,1); C ^= T0+T1+xkey->K[8+2*(r)];\
D ^= T0+2*T1+xkey->K[8+2*(r)+1]; D = ROR32(D,1)

#define DECRYPT_CYCLE( A, B, C, D, T0, T1, xkey, r ) \
DECRYPT_RND( A,B,C,D,T0,T1,xkey,2*(r)+1 );\
DECRYPT_RND( C,D,A,B,T0,T1,xkey,2*(r)   )

#define DECRYPT( A, B, C, D, T0, T1, xkey ) \
for (int i = 7; i >= 0; i--) \
{DECRYPT_CYCLE(A, B, C, D, T0, T1, xkey, i);}\


#define INPUT_WHITNING( src, A,B,C,D, xkey, koff ) \
A = GET32(src   )^xkey->K[koff]; B = GET32(src+ 4)^xkey->K[1+koff]; \
C = GET32(src+ 8)^xkey->K[2+koff]; D = GET32(src+12)^xkey->K[3+koff]


#define OUTPUT_WHITNING(dst, A,B,C,D, xkey, koff ) \
A ^= xkey->K[koff]; B ^= xkey->K[1+koff]; \
C ^= xkey->K[2+koff]; D ^= xkey->K[3+koff]; \
PUT32( A, dst   ); PUT32( B, dst+ 4 ); \
PUT32( C, dst+8 ); PUT32( D, dst+12 )


void encrypt_block(twofish_key * xkey, uint8_t p[16], uint8_t c[16])
{
    uint32_t A,B,C,D,T0,T1;


    INPUT_WHITNING( p, A,B,C,D, xkey, 0 );
  
    ENCRYPT( A,B,C,D,T0,T1,xkey );

    OUTPUT_WHITNING(c, C,D,A,B, xkey, 4 );
   
}


void decrypt_block( twofish_key * xkey, uint8_t c[16], uint8_t p[16])
{
    uint32_t A,B,C,D,T0,T1;

    INPUT_WHITNING( c, A,B,C,D, xkey, 4 );

    DECRYPT( A,B,C,D,T0,T1,xkey);

    OUTPUT_WHITNING(p, C,D,A,B, xkey, 0 );

}


void encrypt_file(char *filepath, twofish_context *context, char* tmppath, ProgressCallback callback) {
    FILE *fp = fopen(filepath, "rb");
    FILE *tmp = fopen(tmppath, "wb");

    uint8_t buf[16];
    uint8_t iv[16];
    memcpy(iv, context->iv, 16);
    int mode = context->mode;

    fseek(fp, 0, SEEK_END);
    long fileSize = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    long bytesRead = 0;
    float progress = 0;

    switch (mode) {
        case ECB:
            while (fread(buf, 1, sizeof(buf), fp) > 0) {
                
                encrypt_block(context->key, buf, buf);
                fwrite(buf, 1, sizeof(buf), tmp);
                bytesRead += sizeof(buf);
                progress = (float)bytesRead / fileSize;     
                callback(progress);
            }
            break;

        case CBC:
            while (fread(buf, 1, sizeof(buf), fp) > 0) {
                for (int i = 0; i < 16; i++) {
                    buf[i] ^= iv[i];
                }
                encrypt_block(context->key, buf, buf);
                memcpy(iv, buf, 16);
                fwrite(buf, 1, sizeof(buf), tmp);
                bytesRead += sizeof(buf);
                progress = (float)bytesRead / fileSize;
                callback(progress);
            }
            break;

        case CFB:
            while (fread(buf, 1, sizeof(buf), fp) > 0) {
                encrypt_block(context->key, iv, iv);
                for (int i = 0; i < 16; i++) {
                    buf[i] ^= iv[i];
                }
                fwrite(buf, 1, sizeof(buf), tmp);
                memcpy(iv, buf, 16);
                bytesRead += sizeof(buf);
                progress = (float)bytesRead / fileSize;
                callback(progress);
            }
            break;

        case OFB:
            while (fread(buf, 1, sizeof(buf), fp) > 0) {
                encrypt_block(context->key, iv, iv);
                for (int i = 0; i < 16; i++) {
                    buf[i] ^= iv[i];
                }
                fwrite(buf, 1, sizeof(buf), tmp);
                bytesRead += sizeof(buf);
                progress = (float)bytesRead / fileSize;
                callback(progress);
            }
            break;

        default:
            break;
    }

    fclose(tmp);
    fclose(fp);
}

void decrypt_file(char *filepath, twofish_context *context, char* tmppath, ProgressCallback callback) {
    FILE *fp = fopen(filepath, "rb");
    FILE *tmp = fopen(tmppath, "wb");

    uint8_t buf[16];
    uint8_t iv[16];
    memcpy(iv, context->iv, 16);
    int mode = context->mode;

    fseek(fp, 0, SEEK_END);
    long fileSize = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    long bytesRead = 0;
    float progress = 0;

    switch (mode) {
        case ECB:
            while (fread(buf, 1, sizeof(buf), fp) > 0){
                
                decrypt_block(context->key, buf, buf);
                fwrite(buf, 1, sizeof(buf), tmp);
                bytesRead += sizeof(buf);
                progress = (float)bytesRead / fileSize;
                callback(progress);
            }
            break;

        case CBC:
            while (fread(buf, 1, sizeof(buf), fp) > 0) {
                uint8_t temp[16];
                memcpy(temp, buf, 16);

                decrypt_block(context->key, buf, buf);

                for (int i = 0; i < 16; i++) {
                    buf[i] ^= iv[i];
                }

                memcpy(iv, temp, 16);
                fwrite(buf, 1, sizeof(buf), tmp);
                bytesRead += sizeof(buf);
                progress = (float)bytesRead / fileSize;
                callback(progress);
            }
            break;

        case CFB:
            while (fread(buf, 1, sizeof(buf), fp) > 0) {
                encrypt_block(context->key, iv, iv);
                uint8_t temp[16];
                memcpy(temp, buf, 16);

                for (int i = 0; i < 16; i++) {
                    buf[i] ^= iv[i];
                }

                fwrite(buf, 1, sizeof(buf), tmp);
                memcpy(iv, temp, 16);
                bytesRead += sizeof(buf);
                progress = (float)bytesRead / fileSize;
                callback(progress);
            }
            break;

        case OFB:
            while (fread(buf, 1, sizeof(buf), fp) > 0) {
                encrypt_block(context->key, iv, iv);
                for (int i = 0; i < 16; i++) {
                    buf[i] ^= iv[i];
                }
                fwrite(buf, 1, sizeof(buf), tmp);
                bytesRead += sizeof(buf);
                progress = (float)bytesRead / fileSize;
                callback(progress);
            }
            break;

        default:
            break;
    }
    fclose(tmp);
    fclose(fp);
}


twofish_context* generate_context(char* iv, int mode, twofish_key* key){
    twofish_context* context = (twofish_context*)malloc(sizeof(twofish_context));
    memcpy(context->iv,iv, 16);
    context->key=key;
    context->mode = mode;
    return context;
}