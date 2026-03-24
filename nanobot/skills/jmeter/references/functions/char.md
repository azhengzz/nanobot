# __char

## Function Name
`__char`

## Category
String

## Description
Generate Unicode char values from a list of numbers. This function converts decimal values to their corresponding Unicode characters.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Unicode character number (decimal or 0xhex) | The decimal number (or hex number, if prefixed by `0x`, or octal, if prefixed by `0`) to be converted to a Unicode character. | Yes |

## Usage Examples

### Basic usage
```
${__char(65)}
```
Returns: "A"

### Multiple characters
```
${__char(72,101,108,108,111)}
```
Returns: "Hello"

### Special characters
```
${__char(32)}
```
Returns: " " (space)

### New line
```
${__char(10)}
```
Returns: "\n" (newline)

### Tab
```
${__char(9)}
```
Returns: "\t" (tab)

### Building strings
```
Line 1${__char(10)}Line 2
```

## Common Unicode Values

| Decimal | Character | Description |
|---------|-----------|-------------|
| 9 | \t | Tab |
| 10 | \n | New line |
| 13 | \r | Carriage return |
| 32 | Space | Space |
| 48-57 | 0-9 | Digits |
| 65-90 | A-Z | Uppercase letters |
| 97-122 | a-z | Lowercase letters |

## Notes
- Each argument is a decimal Unicode value.
- Multiple values can be provided.
- Returns the concatenated characters as a string.
- Useful for generating special characters.

## Since
2.3.3

## Reference
- [Apache JMeter - __char](https://jmeter.apache.org/usermanual/functions.html#__char)
