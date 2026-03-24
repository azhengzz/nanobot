# __urldecode

## Function Name
`__urldecode`

## Category
String

## Description
Decode an application/x-www-form-urlencoded string. This function decodes a URL-encoded string back to its original form.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | String to decode | The string with URL encoded chars to decode. | Yes |

## Usage Examples

### Basic usage
```
${__urldecode(Hello%20World)}
```
Returns: "Hello World"

### Decode special characters
```
${__urldecode(name%3DJohn%26Doe)}
```
Returns: "name=John&Doe"

### Decode percent encoding
```
${__urldecode(100%25)}
```
Returns: "100%"

### From variable
```
${__urldecode(${encodedParam})}
```

### Process query parameter
```
${__urldecode(${__P(query.param)})}
```

### Decode UTF-8
```
${__urldecode(%E4%BD%A0%E5%A5%BD)}
```
Returns: "你好" (Chinese for "hello")

## Common Encodings

| Encoded | Decoded |
|---------|---------|
| %20 | Space |
| %21 | ! |
| %23 | # |
| %24 | $ |
| %25 | % |
| %26 | & |
| %27 | ' |
| %28 | ( |
| %29 | ) |
| %2B | + |
| %3D | = |
| %3F | ? |

## Notes
- Decodes %xx escape sequences.
- Converts + to space.
- Handles UTF-8 multi-byte characters.
- Inverse of `__urlencode`.

## Since
2.10

## Reference
- [Apache JMeter - __urldecode](https://jmeter.apache.org/usermanual/functions.html#__urldecode)
