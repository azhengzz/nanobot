# __digest

## Function Name
`__digest`

## Category
Calculation

## Description
Generate a digest (hash) using various algorithms. This function generates a cryptographic hash/digest of the input string using specified algorithms like MD5, SHA-1, SHA-256, etc.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Algorithm | The algorithm to be used to encrypt. For possible algorithms See MessageDigest in StandardNames (MD2, MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512) | Yes |
| 2 | String to encode | The String that will be encrypted | Yes |
| 3 | Salt to add | Salt to be added to string before encryption (optional) | No |
| 4 | Upper Case value | Result will be in upper case if value is "true" (optional) | No |
| 5 | Name of variable | The name of the variable to set. | No |

## Usage Examples

### MD5 hash
```
${__digest(MD5,Hello World)}
```
Returns: "b10a8db164e0754105b7a99be72e3fe5"

### SHA-256 hash
```
${__digest(SHA-256,MyPassword)}
```

### Store in variable
```
${__digest(SHA-1,password123,hashedPassword)}
Hash: ${hashedPassword}
```

### With salt
```
${__digest(SHA-256,user123,saltValue,hashed)}
```

### In HTTP request
```
/login?username=${user}&hash=${__digest(MD5,${password})}
```

### For API signature
```
/signature?value=${__digest(SHA-256,${data}${secret})}
```

## Common Algorithms

| Algorithm | Description | Output Length |
|-----------|-------------|---------------|
| MD5 | Message Digest 5 (deprecated for security) | 32 hex chars |
| SHA-1 | Secure Hash Algorithm 1 (deprecated) | 40 hex chars |
| SHA-256 | SHA-2 with 256-bit output | 64 hex chars |
| SHA-384 | SHA-2 with 384-bit output | 96 hex chars |
| SHA-512 | SHA-2 with 512-bit output | 128 hex chars |

## Notes
- Returns the hash as a hexadecimal string.
- Salt (if provided) is prepended to the input string.
- Useful for password hashing, data integrity, API signatures.
- For password storage, use proper password hashing (bcrypt, PBKDF2) instead.

## Since
4.0

## Reference
- [Apache JMeter - __digest](https://jmeter.apache.org/usermanual/functions.html#__digest)
