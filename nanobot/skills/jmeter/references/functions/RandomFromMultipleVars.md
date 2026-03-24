# __RandomFromMultipleVars

## Function Name
`__RandomFromMultipleVars`

## Category
Calculation

## Description
Extracts an element from the values of a set of variables separated by `|`. This function takes multiple variable names and randomly selects one of their values.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Source Variables | Variable names separated by `|` that contain the values that will be used as input for random computation | Yes |
| 2 | Variable Name | A reference name for reusing the value computed by this function. | No |

## Usage Examples

### Basic usage
```
${__RandomFromMultipleVars(var1|var2|var3)}
```
Randomly returns the value of var1, var2, or var3.

### Store in variable
```
${__RandomFromMultipleVars(A|B|C,choice)}
Selected: ${choice}
```

### With predefined variables
```
# Assume: color1=red, color2=blue, color3=green
${__RandomFromMultipleVars(color1|color2|color3,randomColor)}
```

### In HTTP request
```
/type?value=${__RandomFromMultipleVars(optionA|optionB|optionC)}
```

### Multiple selections
```
${__RandomFromMultipleVars(${prefix}1|${prefix}2|${prefix}3)}
```

## Notes
- Variable names are separated by pipe (`|`) characters.
- The function randomly selects one variable name and returns its value.
- If a variable doesn't exist, returns the variable name itself.
- Useful for A/B testing, random selection from predefined options.

## Since
3.1

## Reference
- [Apache JMeter - __RandomFromMultipleVars](https://jmeter.apache.org/usermanual/functions.html#__RandomFromMultipleVars)
