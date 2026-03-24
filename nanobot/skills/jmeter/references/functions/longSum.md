# __longSum

## Function Name
`__longSum`

## Category
Calculation

## Description
Add long numbers. The longSum function can be used to compute the sum of two or more long integer values. Similar to `__intSum` but supports larger numbers (long type).

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | First argument | The first long value. | Yes |
| 2 | Second argument | The second long value. | Yes |
| 3+ | nth argument | The nth long value. | No |
| last | last argument | A reference name for reusing the value computed by this function. If specified, the reference name must contain at least one non-numeric character otherwise it will be treated as another long value to be added. | No |

## Usage Examples

### Basic addition
```
${__longSum(10000000000,20000000000)}
```
Returns: 30000000000

### Multiple numbers
```
${__longSum(1000000,2000000,3000000)}
```
Returns: 6000000

### Store in variable
```
${__longSum(${timestamp},${offset},newTime)}
```

### For large counters
```
${__longSum(${baseId},1000,${__threadNum})}
```

## Notes
- Supports larger numbers than `__intSum` (64-bit vs 32-bit).
- All values are treated as long integers.
- The reference name is optional but must not be a valid integer if provided.
- Can add any number of long values (not just two).
- Works on the Test Plan (unlike some other functions).

## Since
2.3.2

## Reference
- [Apache JMeter - __longSum](https://jmeter.apache.org/usermanual/functions.html#__longSum)
