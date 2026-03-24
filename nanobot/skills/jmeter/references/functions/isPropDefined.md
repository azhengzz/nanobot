# __isPropDefined

## Function Name
`__isPropDefined`

## Category
Properties

## Description
Test if a property exists. This function checks if a JMeter property is defined and returns "true" or "false".

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Property Name | The Property Name to be used to check if defined | Yes |

## Usage Examples

### Basic usage
```
${__isPropDefined(custom.prop)}
```
Returns "true" if property exists, "false" otherwise.

### Conditional logic
```
${__isPropDefined(useHttps)} == true
```

### In If Controller
```
${__isPropDefined(test.mode)}
```

### With default fallback
```
${__isPropDefined(myVar)} == false ? ${__P(myVar,default)} : ${__P(myVar)}
```

## Notes
- Returns the string "true" or "false" (not boolean).
- Useful for conditional test logic.
- Can be used in If Controllers.
- Checks if property exists, not if it has a value.

## Since
4.0

## Reference
- [Apache JMeter - __isPropDefined](https://jmeter.apache.org/usermanual/functions.html#__isPropDefined)
