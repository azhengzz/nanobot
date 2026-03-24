# __log

## Function Name
`__log`

## Category
Information

## Description
Log (or display) a message and return the value. This function logs a message to the JMeter log file and returns the message value.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | String to be logged | A string | Yes |
| 2 | Log Level | `OUT`, `ERR`, `DEBUG`, `INFO` (default), `WARN` or `ERROR` | No |
| 3 | Throwable text | If non-empty, creates a Throwable to pass to the logger | No |
| 4 | Comment | If present, it is displayed in the string. Useful for identifying what is being logged. | No |

## Usage Examples

### Basic usage
```
${__log(Message to log)}
```
Logs "Message to log" at INFO level and returns the same string.

### Log at different level
```
${__log(Warning message,WARN)}
```
Logs at WARN level.

### Log to System.out
```
${__log(Debug message,OUT)}
```
Logs to standard output.

### Log error
```
${__log(Error occurred,ERROR,Exception details)}
```
Logs an error with exception details.

### Store log result
```
${__log(Processing item ${itemId},,logResult)}
```

## Notes
- The message is logged to the JMeter log file (jmeter.log by default).
- Unlike `__logn`, this function returns the message value.
- Useful for debugging test plans.

## Since
2.2

## Reference
- [Apache JMeter - __log](https://jmeter.apache.org/usermanual/functions.html#__log)
