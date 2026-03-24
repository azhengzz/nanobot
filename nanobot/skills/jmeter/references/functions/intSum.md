# __intSum

## Function Name
`__intSum`

## Category
Calculation

## Description
Add int numbers. The intSum function can be used to compute the sum of two or more integer values.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | First argument | The first int value. | Yes |
| 2 | Second argument | The second int value. | Yes |
| 3+ | nth argument | The nth int value. | No |
| last | last argument | A reference name for reusing the value computed by this function. If specified, the reference name must contain at least one non-numeric character otherwise it will be treated as another int value to be added. | No |

## Usage Examples

### Basic addition
```
${__intSum(1,2)}
```
Returns: 3

### Multiple numbers
```
${__intSum(1,2,3,4)}
```
Returns: 10

### Store in variable
```
${__intSum(10,20,total)}
Result: ${total}
```

### With variables
```
${__intSum(${counter},5,offset)}
```
Adds counter value to 5 and stores in offset.

### In HTTP request
```
/offset/${__intSum(${baseOffset},10)}
```

## Notes
- All values are treated as integers.
- The reference name is optional but must not be a valid integer if provided.
- Can add any number of integers (not just two).
- Works on the Test Plan (unlike some other functions).

## Since
1.8.1

## Reference
- [Apache JMeter - __intSum](https://jmeter.apache.org/usermanual/functions.html#__intSum)
