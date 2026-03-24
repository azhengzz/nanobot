# __changeCase

## Function Name
`__changeCase`

## Category
String

## Description
Change case following different modes. This function changes the case of a string to upper, lower, capitalize, etc.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | String to change case | The String which case will be changed | Yes |
| 2 | change case mode | The mode to be used to change case, for example for `ab-CD eF`:<br>- `UPPER` result as AB-CD EF<br>- `LOWER` result as ab-cd ed<br>- `CAPITALIZE` result as Ab-CD eF<br>If no mode is given, `UPPER` is used as default. | No |
| 3 | Name of variable | The name of the variable to set. | No |

## Usage Examples

### Uppercase
```
${__changeCase(hello world)}
```
Returns: "HELLO WORLD"

### Lowercase
```
${__changeCase(HELLO WORLD,LOWER)}
```
Returns: "hello world"

### Capitalize
```
${__changeCase(hello world,CAPITALIZE)}
```
Returns: "Hello World"

### With variable
```
${__changeCase(${username},UPPER)}
```

### Store in variable
```
${__changeCase(input string,UPPER,result)}
${result}
```

## Modes

| Mode | Description | Example |
|------|-------------|---------|
| UPPER | Convert to uppercase | "HELLO WORLD" |
| LOWER | Convert to lowercase | "hello world" |
| CAPITALIZE | Capitalize first letter of each word | "Hello World" |

## Notes
- Default mode is UPPER if not specified.
- Case modes are case-insensitive.
- Useful for normalizing text input.

## Since
4.0

## Reference
- [Apache JMeter - __changeCase](https://jmeter.apache.org/usermanual/functions.html#__changeCase)
