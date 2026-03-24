# __BeanShell

## Function Name
`__BeanShell`

## Category
Scripting

## Description
Run a BeanShell script. This function executes a BeanShell script expression and returns the result.

**Note**: BeanShell is deprecated in favor of Groovy. Use `__groovy` for new scripts.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | BeanShell script | A beanshell script (not a file name) | Yes |
| 2 | Name of variable | A reference name for reusing the value computed by this function. | No |

## Usage Examples

### Basic expression
```
${__BeanShell(2 + 3)}
```
Returns: 5

### String manipulation
```
${__BeanShell("hello".toUpperCase())}
```
Returns: "HELLO"

### Access variables
```
${__BeanShell(vars.get("myVar"))}
```

### Set variables
```
${__BeanShell(vars.put("newVar", "value"))}
```

### With comma (escape required)
```
${__BeanShell(Math.max(1\, 5))}
```

### Store in variable
```
${__BeanShell(1 + 2,result)}
Value: ${result}
```

## Available Objects

| Object | Description |
|--------|-------------|
| `vars` | JMeterVariables - access and set JMeter variables |
| `props` | JMeterProperties - access JMeter properties |
| `prev` | SampleResult - previous sample result |
| `ctx` | JMeterContext - current context |
| `log` | Logger - log messages |

## Notes
- **BeanShell is deprecated**. Use `__groovy` instead.
- Similar syntax to Java.
- Must escape commas in script with backslash.
- Performance is lower than Groovy.
- Considered legacy, may be removed in future versions.

## Since
1.X

## Reference
- [Apache JMeter - __BeanShell](https://jmeter.apache.org/usermanual/functions.html#__BeanShell)
