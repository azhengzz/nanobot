# __logn

## Function Name
`__logn`

## Category
Information

## Description
Log (or display) a message with empty return value. This function logs a message to the JMeter log file but returns an empty string (unlike `__log` which returns the message).

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | String to be logged | A string | Yes |
| 2 | Log Level | `OUT`, `ERR`, `DEBUG`, `INFO` (default), `WARN` or `ERROR` | No |
| 3 | Throwable text | If non-empty, creates a Throwable to pass to the logger | No |

## Usage Examples

### Basic usage
```
${__logn(Message to log)}
```
Logs "Message to log" at INFO level and returns empty string.

### Log at WARN level
```
${__logn(Warning message,WARN)}
```
Logs at WARN level.

### Debug logging
```
${__logn(Debug info,DEBUG)}
```
Logs at DEBUG level.

### In path (doesn't affect output)
```
/api/endpoint${__logn(Processing request,INFO)}
```
Logs the message but doesn't add anything to the path.

## Notes
- The message is logged to the JMeter log file (jmeter.log by default).
- Returns an empty string, so it can be inserted anywhere without affecting the output.
- Useful for debugging without modifying values.
- Differs from `__log` which returns the message value.

## Since
2.2

## Reference
- [Apache JMeter - __logn](https://jmeter.apache.org/usermanual/functions.html#__logn)
