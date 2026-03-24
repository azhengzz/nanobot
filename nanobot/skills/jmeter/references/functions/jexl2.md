# __jexl2

## Function Name
`__jexl2`

## Category
Scripting

## Description
Evaluate a Commons JEXL2 expression. This function evaluates an expression using the Apache Commons JEXL2 expression language.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Expression | The expression to be evaluated. For example, `6*(5+2)` | Yes |
| 2 | Name of variable | The name of the variable to set. | No |

## Usage Examples

### Basic expression
```
${__jexl2(2 + 3)}
```
Returns: 5

### Access variables
```
${__jexl2(myVar + 10)}
```

### Conditional
```
${__jexl2(x > 5 ? 'big' : 'small')}
```

### String concatenation
```
${__jexl2('Hello ' + name)}
```

### Store in variable
```
${__jexl2(count * 2,result)}
```

### With functions
```
${__jexl2(empty(myVar) ? 'default' : myVar)}
```

## Notes
- JEXL2 provides a simpler expression language than full scripting.
- Consider using `__jexl3` for newer features.
- Can access JMeter variables directly by name.
- No need to escape commas in most cases.

## Since
jexl2 (2.1.1)

## Reference
- [Apache JMeter - __jexl2](https://jmeter.apache.org/usermanual/functions.html#__jexl2)
