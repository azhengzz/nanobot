# __rsaEncrypt

## Function Name
`__rsaEncrypt`

## Category
Calculation

## Description
Encrypt a string using RSA algorithm with a public key. Returns Base64-encoded ciphertext.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Plaintext | The string to be encrypted | Yes |
| 2 | Public Key | RSA public key in Base64 format | Yes |
| 3 | Variable Name | A reference name for reusing the encrypted value. | No |

## Usage Examples

### Basic encryption
```
${__rsaEncrypt(hello world,MIGfMA0GCSq...)}
```
Returns RSA-encrypted ciphertext of "hello world".

### Store in variable
```
${__rsaEncrypt(password123,MIGfMA0GCSq...,encryptedPwd)}
Encrypted: ${encryptedPwd}
```

### In HTTP request
```
/login?username=${user}&token=${__rsaEncrypt(${password},MIGfMA0GCSq...)}
```

### Encrypt JSON data
```
${__rsaEncrypt({"username":"admin","id":123},MIGfMA0GCSq...)}
```

### For API signature
```
{
  "data": "${__rsaEncrypt(sensitive data,MIGfMA0GCSq...)}"
}
```

## Notes
- Encryption algorithm: RSA
- Public key must be in Base64 format (X.509 encoded)
- Returns Base64-encoded ciphertext
- Public key cannot be empty
- RSA is asymmetric encryption (encrypts with public key, decrypts with private key)
- Useful for encrypting sensitive data before transmission
- Requires valid RSA public key

## Since
5.1.1 (Custom Extension)

## Reference
- [JMeter 二次开发源码](https://gitee.com/azhengzz/JmeterSecondaryDevelopmentForIDEA/blob/master/JMeter_5.1.1/src/extension/com/gitee/qa/jmeter/functions/RSAEncrypt.java)
- [RSA Encryption - Wikipedia](https://en.wikipedia.org/wiki/RSA_(cryptosystem))
