# __setProperty

## Function Name
`__setProperty`

## Category
Properties

## Description
Set a JMeter property. This function sets a JMeter property value. Properties are global and persist for the duration of the test.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Property Name | The property name to be set. | Yes |
| 2 | Property Value | The value for the property. | Yes |
| 3 | True/False | Should the original value be returned? | No |

## Usage Examples

### Basic usage
```
${__setProperty(myProp,value)}
```
Sets "myProp" to "value".

### Store previous value
```
${__setProperty(counter,${newValue},oldValue)}
Previous: ${oldValue}
```

### Dynamic value
```
${__setProperty(requestCount,${__counter(FALSE)})}
```

### In test flow
```
${__setProperty(lastResponse,${response})}
```

## Notes
- Properties are global across all threads.
- Properties persist for the duration of the test.
- Returns the previous value of the property (or null if didn't exist).
- Useful for sharing data between thread groups.
- Different from variables which are thread-local.

## Since
2.1

## Reference
- [Apache JMeter - __setProperty](https://jmeter.apache.org/usermanual/functions.html#__setProperty)
