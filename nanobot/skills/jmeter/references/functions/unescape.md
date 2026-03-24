# __unescape

## Function Name
`__unescape`

## Category
String

## Description
Process strings containing Java escapes (e.g. \n & \t). This function interprets Java escape sequences and converts them to their actual characters.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | String to unescape | The string to be unescaped. | Yes |

## Usage Examples

### Newline
```
${__unescape(Line 1\\nLine 2)}
```
Returns: "Line 1\nLine 2" (actual newline)

### Tab
```
${__unescape(Hello\\tWorld)}
```
Returns: "Hello\tWorld" (actual tab)

### Backslash
```
${__unescape(C:\\\\path)}
```
Returns: "C:\\path"

### Unicode
```
${__unescape(\\u0048ello)}
```
Returns: "Hello"

### Combined escapes
```
${__unescape(Line1\\n\\tIndented\\nLine2)}
```

## Escape Sequences Supported

| Sequence | Result |
|----------|--------|
| \b | Backspace |
| \t | Horizontal tab |
| \n | Linefeed (newline) |
| \f | Form feed |
| \r | Carriage return |
| \" | Double quote |
| \' | Single quote |
| \\ | Backslash |
| \uXXXX | Unicode character (hex) |

## Notes
- Interprets standard Java escape sequences.
- Double backslashes needed in function call.
- Useful for multi-line strings in HTTP bodies.
- Complement to `__escapeHtml` and `__escapeXml`.

## Since
2.3.3

## Reference
- [Apache JMeter - __unescape](https://jmeter.apache.org/usermanual/functions.html#__unescape)
