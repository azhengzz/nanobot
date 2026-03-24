# __RandomString

## Function Name
`__RandomString`

## Category
Calculation

## Description
Generate a random string. This function creates a random string of specified length using characters from a given set.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Length | A number length of generated String | Yes |
| 2 | Characters to use | Chars used to generate String | No |
| 3 | Variable Name | A reference name for reusing the value computed by this function. | No |

## Usage Examples

### Alphanumeric string
```
${__RandomString(10,abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789)}
```
Returns a 10-character alphanumeric string.

### Store in variable
```
${__RandomString(8,abcdef0123456789,randomCode)}
Code: ${randomCode}
```

### Numeric string
```
${__RandomString(5,0123456789)}
```
Returns a 5-digit number as string.

### Special characters
```
${__RandomString(12,!@#$%^&*()_+-=[]{}|;:,.<>?)}
```

### In HTTP request
```
/session?id=${__RandomString(16,abcdef0123456789)}
```

### For testing input
```
<input value="${__RandomString(20,abcdefghijklmnopqrstuvwxyz)}">
```

## Notes
- Characters can be repeated in the character set.
- Each character is randomly selected from the set.
- The result is a string, not a number.
- Useful for generating test data, session IDs, etc.

## Since
2.6

## Reference
- [Apache JMeter - __RandomString](https://jmeter.apache.org/usermanual/functions.html#__RandomString)
