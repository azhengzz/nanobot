# __jexl3

## Function Name
`__jexl3`

## Category
Scripting

## Description
Evaluate a Commons JEXL3 expression. This function evaluates an expression using the Apache Commons JEXL3 expression language, which is the recommended version of JEXL.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Expression | The expression to be evaluated. For example, `6*(5+2)` | Yes |
| 2 | Name of variable | The name of the variable to set. | No |

## Usage Examples

### Basic expression
```
${__jexl3(2 + 3)}
```
Returns: 5

### Access variables
```
${__jexl3(myVar + 10)}
```

### Conditional
```
${__jexl3(x > 5 ? 'big' : 'small')}
```

### String operations
```
${__jexl3(name.toUpperCase())}
```

### Store in variable
```
${__jexl3(count * 2,result)}
```

### With functions
```
__jexl3(empty(myVar) ? 'default' : myVar)
```

### List operations
```
__jexl3(list[0])
```

## Notes
- JEXL3 is the recommended version of JEXL for JMeter.
- Provides a simple expression language.
- Can access JMeter variables directly by name.
- Lightweight alternative to full scripting languages.
- Better performance than BeanShell.

## Since
jexl3 (3.0)

## Reference
- [Apache JMeter - __jexl3](https://jmeter.apache.org/usermanual/functions.html#__jexl3)
