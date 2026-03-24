# __P

## Function Name
`__P`

## Category
Properties

## Description
Read a property (shorthand method). This is a simplified shorthand for `__property` that reads a JMeter property.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Property Name | The property name to be retrieved. | Yes |
| 2 | Default Value | The default value for the property. If omitted, the default is set to "1". | No |

## Usage Examples

### Basic usage
```
${__P(port)}
```
Returns the value of "port" property.

### With default value
```
${__P(server.port,8080)}
```
Returns "server.port" value or 8080 if not found.

### In HTTP request
```
${__P(host,localhost)}:${__P(port,8080)}
```

### Command line usage
```
jmeter -Jhost=example.com -Jport=443
```
Then use: `${__P(host)}`

## Notes
- Shorthand for `__property`.
- Properties are set with `-J` command line option.
- Properties are global across all threads.
- Most commonly used property function in JMeter.

## Since
2.0

## Reference
- [Apache JMeter - __P](https://jmeter.apache.org/usermanual/functions.html#__P)
