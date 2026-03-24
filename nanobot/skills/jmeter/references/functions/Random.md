# __Random

## Function Name
`__Random`

## Category
Calculation

## Description
Generate a random number. This function generates a random number within a specified range (inclusive).

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Minimum value | A number | Yes |
| 2 | Maximum value | A bigger number | Yes |
| 3 | Variable Name | A reference name for reusing the value computed by this function. | No |

## Usage Examples

### Basic usage
```
${__Random(1,100)}
```
Returns a random number between 1 and 100 (inclusive).

### Store in variable
```
${__Random(0,1000,randomNum)}
Value: ${randomNum}
```

### In HTTP request
```
/user?id=${__Random(1,10000)}
```

### For testing
```
/delay/${__Random(100,500)}
```

## Notes
- Both min and max values are inclusive.
- Returns an integer value.
- Each call generates a new random number.
- Spaces around variable name are trimmed by JMeter.

## Since
1.9

## Reference
- [Apache JMeter - __Random](https://jmeter.apache.org/usermanual/functions.html#__Random)
