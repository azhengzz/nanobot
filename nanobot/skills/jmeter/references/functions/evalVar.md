# __evalVar

## Function Name
`__evalVar`

## Category
Variables

## Description
Evaluate an expression stored in a variable. This function evaluates an expression that is stored in a variable and returns the result.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Variable name | The variable to be evaluated. | Yes |

## Usage Examples

### Basic usage
```
# Assume: myExpr=2 + 3
${__evalVar(myExpr)}
```
Returns: "5" (as string)

### With stored function call
```
# Assume: func=${__time(YMD)}
${__evalVar(func)}
```

### Dynamic calculation
```
# store: calc=${count} * 2
${__evalVar(calc)}
```

### Complex expression
```
# Assume: expr=${var1} + ${var2}
${__evalVar(expr)}
```

## Notes
- Evaluates the content of a variable as an expression.
- Similar to `__eval` but processes the variable content.
- Returns the result as a string.
- Useful for dynamic expression evaluation.

## Since
2.3.1

## Reference
- [Apache JMeter - __evalVar](https://jmeter.apache.org/usermanual/functions.html#__evalVar)
