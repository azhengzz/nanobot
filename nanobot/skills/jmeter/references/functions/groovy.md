# __groovy

## Function Name
`__groovy`

## Category
Scripting

## Description
Run an Apache Groovy script. This function executes a Groovy script expression and returns the result. Groovy is the recommended scripting language for JMeter.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Expression to evaluate | An Apache Groovy script (not a file name) | Yes |
| 2 | Name of variable | A reference name for reusing the value computed by this function. | No |

## Usage Examples

### Basic expression
```
${__groovy(2 + 3)}
```
Returns: 5

### String manipulation
```
${__groovy('hello'.toUpperCase())}
```
Returns: "HELLO"

### Access variables
```
${__groovy(vars.get('myVar'))}
```

### Set variables
```
${__groovy(vars.put('newVar', 'value'))}
```

### Complex logic
```
${__groovy(import java.util.UUID; UUID.randomUUID().toString())}
```

### With comma in script (escape required)
```
${__groovy(Math.max(1\, 5))}
```

### Store in variable
```
${__groovy('${__time(dd/MM/yyyy)}'.substring(3,5),day)}
```

### Sample result access
```
${__groovy(prev.getResponseDataAsString())}
```

## Notes
- Groovy is the recommended scripting language for JMeter.
- Access JMeter variables via `vars` object.
- Access properties via `props` object.
- Access previous sample via `prev` object.
- Access context via `ctx` object.
- Must escape commas in script with backslash.
- Can use full Groovy syntax including imports.

## Available Objects

| Object | Description |
|--------|-------------|
| `vars` | JMeterVariables - access and set JMeter variables |
| `props` | JMeterProperties - access JMeter properties |
| `prev` | SampleResult - previous sample result |
| `ctx` | JMeterContext - current context |
| `out` | System.out - print to console |
| `log` | Logger - log messages |

## Since
3.1

## Reference
- [Apache JMeter - __groovy](https://jmeter.apache.org/usermanual/functions.html#__groovy)
