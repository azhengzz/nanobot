# __timeToTimestamp

## Function Name
`__timeToTimestamp`

## Category
Time

## Description
Convert a formatted date string to Unix timestamp. This function parses a date string according to the specified format and returns the corresponding timestamp in milliseconds.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Date Format | Date format pattern (e.g., `yyyy-MM-dd HH:mm:ss:SSS`) | Yes |
| 2 | Date String | The date string to convert | Yes |
| 3 | Variable Name | A reference name for reusing the timestamp value. | No |

## Usage Examples

### Basic conversion
```
${__timeToTimestamp(yyyy-MM-dd HH:mm:ss:SSS,2022-09-01 09:41:23:589)}
```
Returns: `1661995283589`

### Simple date format
```
${__timeToTimestamp(yyyy-MM-dd,2024-01-15)}
```
Returns timestamp for 2024-01-15 00:00:00.

### Store in variable
```
${__timeToTimestamp(yyyy-MM-dd HH:mm:ss,2024-01-01 12:30:45,ts)}
Timestamp: ${ts}
```

### Chinese date format
```
${__timeToTimestamp(yyyy年MM月dd日 HH时mm分ss秒,2024年01月15日 14时30分00秒)}
```

### ISO format
```
${__timeToTimestamp(yyyy-MM-dd'T'HH:mm:ss,2024-01-15T14:30:00)}
```

### With milliseconds
```
${__timeToTimestamp(yyyy-MM-dd HH:mm:ss.SSS,2024-01-15 14:30:00.123)}
```

## Common Format Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| yyyy | 4-digit year | 2024 |
| MM | 2-digit month | 01-12 |
| dd | 2-digit day | 01-31 |
| HH | Hour (24h) | 00-23 |
| mm | Minute | 00-59 |
| ss | Second | 00-59 |
| SSS | Millisecond | 000-999 |

## Notes
- Returns timestamp in milliseconds (13-digit number)
- Format pattern must match the input date string structure
- If parsing fails, returns incorrect result or error
- Useful for calculating time differences, setting expiration dates
- Complement to JMeter's built-in `__time` function

## Since
5.1.1 (Custom Extension)

## Reference
- [JMeter 二次开发源码](https://gitee.com/azhengzz/JmeterSecondaryDevelopmentForIDEA/blob/master/JMeter_5.1.1/src/extension/com/gitee/qa/jmeter/functions/TimeToTimestamp.java)
- [Java SimpleDateFormat](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
