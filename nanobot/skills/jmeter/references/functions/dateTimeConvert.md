# __dateTimeConvert

## Function Name
`__dateTimeConvert`

## Category
Formatting

## Description
Convert a date or time from source format to target format. This function parses a date string in one format and outputs it in another format.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Date String | The date string to convert from Source Date Format to Target Date Format. A date as a epoch time could be use here if Source Date Format is empty. | Yes |
| 2 | Source Date Format | The original date format. If empty, the Date String field must be a epoch time. | No |
| 3 | Target Date Format | The new date format | Yes |
| 4 | Name of variable | The name of the variable to set. | No |

## Usage Examples

### Basic conversion
```
${__dateTimeConvert(2026-03-24,yyyy-MM-dd,dd/MM/yyyy)}
```
Returns: "24/03/2026"

### Store in variable
```
${__dateTimeConvert(03/24/2026,MM/dd/yyyy,yyyy-MM-dd,formattedDate)}
Date: ${formattedDate}
```

### Time conversion
```
${__dateTimeConvert(14:30:45,HH:mm:ss,HH-mm-ss)}
```
Returns: "14-30-45"

### Full datetime
```
${__dateTimeConvert(2026-03-24 14:30:45,yyyy-MM-dd HH:mm:ss,dd MMM yyyy HH:mm)}
```
Returns: "24 Mar 2026 14:30"

### With locale
```
${__dateTimeConvert(24-Mar-2026,dd-MMM-yyyy,yyyy-MM-dd,,,en)}
```

### Converting timestamp
```
${__dateTimeConvert(${timestamp},dd/MM/yyyy HH:mm:ss,yyyy-MM-dd'T'HH:mm:ss)}
```

## Common Format Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| yyyy | 4-digit year | 2026 |
| MM | 2-digit month | 03 |
| dd | 2-digit day | 24 |
| HH | Hour (0-23) | 14 |
| mm | Minute | 30 |
| ss | Second | 45 |
| MMM | Month name (abbreviated) | Mar |
| MMMM | Month name (full) | March |

## Notes
- Uses SimpleDateFormat patterns for Java.
- If locale is not specified, uses the default locale.
- Useful for normalizing date formats across different APIs.
- Both input and output formats must be valid.

## Since
4.0

## Reference
- [Apache JMeter - __dateTimeConvert](https://jmeter.apache.org/usermanual/functions.html#__dateTimeConvert)
