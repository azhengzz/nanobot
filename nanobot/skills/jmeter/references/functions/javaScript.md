# __javaScript

## Function Name
`__javaScript`

## Category
Scripting

## Description
Process JavaScript (Nashorn). This function executes a JavaScript expression using the Nashorn JavaScript engine and returns the result.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Expression | The JavaScript expression to be executed. For example:<br>- `new Date()` - return the current date and time<br>- `Math.floor(Math.random()*(${maxRandom}+1))` - a random number between `0` and the variable `maxRandom`<br>- `${minRandom}+Math.floor(Math.random()*(${maxRandom}-${minRandom}+1))` - a random number between the variables `minRandom` and `maxRandom`<br>- `"${VAR}"=="abcd"` | Yes |
| 2 | Variable Name | A reference name for reusing the value computed by this function. | No |

## Usage Examples

### Basic expression
```
${__javaScript(2 + 3)}
```
Returns: 5

### String manipulation
```
${__javaScript('hello'.toUpperCase())}
```
Returns: "HELLO"

### Math functions
```
${__javaScript(Math.floor(Math.random() * 100))}
```

### With comma (escape required)
```
${__javaScript(Math.max(1\, 5))}
```

### Store in variable
```
${__javaScript(new Date().getTime(),timestamp)}
```

### Conditional logic
```
${__javaScript(${count} > 10 ? 'high' : 'low')}
```

### Object manipulation
```
${__javaScript(var obj = {a:1, b:2}; obj.a + obj.b)}
```

## Notes
- Uses Nashorn JavaScript engine (deprecated in Java 11+).
- Consider using `__groovy` for better performance.
- Must escape commas in script with backslash.
- Standard JavaScript syntax is supported.
- Returns the result of the last expression.

## Since
1.9

## Reference
- [Apache JMeter - __javaScript](https://jmeter.apache.org/usermanual/functions.html#__javaScript)
