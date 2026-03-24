# __escapeOroRegexpChars

## Function Name
`__escapeOroRegexpChars`

## Category
String

## Description
Quote meta chars used by ORO regular expression. This function escapes special regex metacharacters in a string so they are treated as literal characters.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | String to escape | The string to be escaped. | Yes |
| 2 | Variable Name | A reference name - `refName` - for reusing the value created by this function. Stored values are of the form `${refName}`. | No |

## Usage Examples

### Basic usage
```
${__escapeOroRegexpChars(test.com)}
```
Returns: "test\\.com" (escapes the dot)

### Multiple special chars
```
${__escapeOroRegexpChars($10.00)}
```
Returns: "\\$10\\.00"

### Parentheses
```
${__escapeOroRegexpChars((test))}
```
Returns: "\\(test\\)"

### In regex match
```
${__regexFunction(${__escapeOroRegexpChars(${searchText})})}
```

## Metacharacters Escaped

| Character | Escaped As |
|-----------|------------|
| . | \\. |
| * | \\* |
| + | \\+ |
| ? | \\? |
| | | \\| |
| ( | \\( |
| ) | \\) |
| [ | \\[ |
| ] | \\] |
| { | \\{ |
| } | \\} |
| ^ | \\^ |
| $ | \\$ |
| \ | \\\\ |

## Notes
- Escapes all ORO regex metacharacters.
- Useful when searching for literal text containing special characters.
- Commonly used with `__regexFunction`.

## Since
2.9

## Reference
- [Apache JMeter - __escapeOroRegexpChars](https://jmeter.apache.org/usermanual/functions.html#__escapeOroRegexpChars)
