# __property

## Function Name
`__property`

## Category
Properties

## Description
Read a property. This function reads a JMeter property and returns its value. Properties are different from variables - they are global across all threads.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Property Name | The property name to be retrieved. | Yes |
| 2 | Variable Name | A reference name for reusing the value computed by this function. | No |
| 3 | Default Value | The default value for the property. | No |

## Usage Examples

### Basic usage
```
${__property(user.dir)}
```
Returns the value of "user.dir" property.

### With default value
```
${__property(custom.prop,default value)}
```
Returns "custom.prop" value or "default value" if not found.

### Store in variable
```
${__property(server.url,http://localhost,serverUrl)}
URL: ${serverUrl}
```

### In HTTP request
```
${__property(base.url)}/api/users
```

## Notes
- Properties are global across all threads (unlike variables).
- Properties are usually set via command line (-J) or jmeter.properties.
- Returns the default value if property is not found.
- Useful for environment-specific configuration.

## Since
2.0

## Reference
- [Apache JMeter - __property](https://jmeter.apache.org/usermanual/functions.html#__property)
