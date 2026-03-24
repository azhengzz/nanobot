# __isVarDefined

## Function Name
`__isVarDefined`

## Category
Properties

## Description
Test if a variable exists. This function checks if a JMeter variable is defined and returns "true" or "false".

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Variable Name | The Variable Name to be used to check if defined | Yes |

## Usage Examples

### Basic usage
```
${__isVarDefined(myVar)}
```
Returns "true" if variable exists, "false" otherwise.

### Conditional logic
```
${__isVarDefined(userToken)} == false
```

### In If Controller
```
${__isVarDefined(sessionId)}
```

### With default fallback
```
${__isVarDefined(data)} == false ? default : ${data}
```

### Safe access pattern
```
${__isVarDefined(config)} == true ? ${config} : ${__P(default.config)}
```

## Notes
- Returns the string "true" or "false" (not boolean).
- Checks for variables, not properties (use `__isPropDefined` for properties).
- Variable name should not include ${ } wrapper.
- Useful for conditional test logic.
- Can be used in If Controllers.

## Since
4.0

## Reference
- [Apache JMeter - __isVarDefined](https://jmeter.apache.org/usermanual/functions.html#__isVarDefined)
