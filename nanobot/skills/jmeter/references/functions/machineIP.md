# __machineIP

## Function Name
`__machineIP`

## Category
Information

## Description
Get the local machine IP address. This function returns the IP address of the machine where JMeter is running.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Variable Name | A reference name for reusing the value computed by this function. | No |

## Usage Examples

### Basic Usage
```
${__machineIP}
```
Returns the local machine's IP address.

### In HTTP Request
```
/report?client_ip=${__machineIP}
```
Sends the local IP address as a parameter.

## Notes
- Returns the IP address of the local machine running JMeter.
- Useful for identifying which machine generated a request in distributed testing.

## Since
2.6

## Reference
- [Apache JMeter - __machineIP](https://jmeter.apache.org/usermanual/functions.html#__machineIP)
