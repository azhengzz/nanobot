# __urlencode

## Function Name
`__urlencode`

## Category
String

## Description
Encode a string to a application/x-www-form-urlencoded string. This function encodes special characters in a string for use in URLs.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | String to encode | String to encode in URL encoded chars. | Yes |

## Usage Examples

### Basic usage
```
${__urlencode(Hello World)}
```
Returns: "Hello+World"

### Encode special characters
```
${__urlencode(name=John&Doe)}
```
Returns: "name%3DJohn%26Doe"

### Encode URL parameter
```
?search=${__urlencode(search term)}
```
Results in: "?search=search+term"

### With variable
```
${__urlencode(${userInput})}
```

### Encode file path
```
${__urlencode(C:\Program Files\test)}
```
Returns: "C%3A%5CProgram+Files%5Ctest"

### Encode for API
```
/data?value=${__urlencode(${jsonPayload})}
```

## Character Encoding

| Character | Encoded |
|-----------|---------|
| Space | + or %20 |
| ! | %21 |
| # | %23 |
| $ | %24 |
| % | %25 |
| & | %26 |
| ' | %27 |
| ( | %28 |
| ) | %29 |
| + | %2B |
| = | %3D |
| ? | %3F |

## Notes
- Encodes unsafe characters for URLs.
- Converts spaces to + (not %20).
- Encodes non-ASCII characters using UTF-8.
- Inverse of `__urldecode`.
- Use for query parameters and form data.

## Since
2.10

## Reference
- [Apache JMeter - __urlencode](https://jmeter.apache.org/usermanual/functions.html#__urlencode)
