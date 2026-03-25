# __aesEncrypt

## Function Name
`__aesEncrypt`

## Category
Calculation

## Description
Encrypt a string using AES algorithm with CBC mode and PKCS5Padding. This function performs AES encryption on the input plaintext and returns the Base64-encoded ciphertext.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Plaintext | The string to be encrypted | Yes |
| 2 | Key | Encryption key (16/24/32 bytes length). Empty string uses default key: `ABCDEFGHIJKL_key` | No |
| 3 | IV | Initialization vector (16 bytes length). Empty string uses default IV: `ABCDEFGHIJKLM_iv` | No |
| 4 | Variable Name | A reference name for reusing the encrypted value. | No |

## Usage Examples

### Basic encryption with default key and IV
```
${__aesEncrypt(hello world,,)}
```
Returns AES-encrypted ciphertext of "hello world" using default key and IV.

### Custom key
```
${__aesEncrypt(my secret data,1234567890123456,,)}
```
Encrypts with 16-byte custom key.

### Custom key and IV
```
${__aesEncrypt(sensitive data,0123456789ABCDEF,FEDCBA9876543210)}
```
Encrypts with 16-byte key and 16-byte IV.

### Store in variable
```
${__aesEncrypt(password123,myKey1234567890,myIV0123456789,encryptedPwd)}
Encrypted: ${encryptedPwd}
```

### In HTTP request
```
/login?username=${user}&token=${__aesEncrypt(${password},1234567890123456,ABCDEFGHIJKLMNOP)}
```

### 24-byte key (AES-192)
```
${__aesEncrypt(data,012345678901234567890123,,)}
```

### 32-byte key (AES-256)
```
${__aesEncrypt(data,01234567890123456789012345678901,,)}
```

## Notes
- Encryption algorithm: AES/CBC/PKCS5Padding
- Key length must be 16, 24, or 32 bytes (corresponding to AES-128, AES-192, AES-256)
- IV length must be exactly 16 bytes
- Returns Base64-encoded ciphertext
- Empty key uses default: `ABCDEFGHIJKL_key`
- Empty IV uses default: `ABCDEFGHIJKLM_iv`
- Requires BouncyCastle provider
- Useful for encrypting sensitive test data before transmission

## Since
5.1.1 (Custom Extension)

## Reference
- [JMeter 二次开发源码](https://gitee.com/azhengzz/JmeterSecondaryDevelopmentForIDEA/blob/master/JMeter_5.1.1/src/extension/com/gitee/qa/jmeter/functions/AESEncrypt.java)
