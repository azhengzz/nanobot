# __machineName

## Function Name
`__machineName`

## Category
Information

## Description
Get the local machine name. This function returns the hostname of the machine where JMeter is running.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Variable Name | A reference name for reusing the value computed by this function. | No |

## Usage Examples

### Basic Usage
```
${__machineName}
```
Returns the local machine's hostname.

### In HTTP Request
```
/report?client_host=${__machineName}
```
Sends the local hostname as a parameter.

## Notes
- Returns the hostname of the local machine running JMeter.
- Useful for identifying which machine generated a request in distributed testing.

## Since
1.X

## Reference
- [Apache JMeter - __machineName](https://jmeter.apache.org/usermanual/functions.html#__machineName)
