# __timePick

## Function Name
`__timePick`

## Category
Time

## Description
Pick a specific day from a week, month, or year based on a given timestamp. Returns Unix timestamp by default or formatted date string.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Time Type | Type of period: `W` (Week), `M` (Month), or `Y` (Year) | Yes |
| 2 | Day Number | Day number (positive for Nth day, negative for Nth day from end) | Yes |
| 3 | Timestamp | Unix timestamp (13-digit ms). Default: current time | No |
| 4 | Format | Date format pattern (e.g., `yyyy-MM-dd HH:mm:ss:SSS`). Default: returns timestamp | No |
| 5 | Variable Name | A reference name for reusing the picked date value. | No |

## Usage Examples

### First day of current month
```
${__timePick(M,1)}
```
Returns timestamp of the 1st day of current month.

### Last day of current month
```
${__timePick(M,-1)}
```
Returns timestamp of the last day of current month.

### First day of current week (Monday)
```
${__timePick(W,1)}
```
Note: Week starts on Monday (1=Monday, 7=Sunday)

### Last day of current week (Sunday)
```
${__timePick(W,7)}
```

### First day of current year
```
${__timePick(Y,1)}
```

### Last day of current year
```
${__timePick(Y,-1)}
```

### With specific timestamp (10-digit)
```
${__timePick(M,15,1643832306)}
```
Returns the 15th day of the month for timestamp `1643832306`.

### With date format
```
${__timePick(M,1,,yyyy-MM-dd HH:mm:ss)}
```
Returns formatted date string like "2024-01-01 00:00:00".

### Store in variable
```
${__timePick(W,1,,yyyy-MM-dd,firstDay)}
${firstDay}
```

## Time Types

| Type | Description | Day Range |
|------|-------------|-----------|
| W | Week | 1-7 (Monday to Sunday) |
| M | Month | 1 to 31, or -1 to -31 (from end) |
| Y | Year | 1 to 366, or -1 to -366 (from end) |

## Notes
- For weeks: Day 1 is Monday, Day 7 is Sunday
- Negative numbers count from the end (-1 = last day)
- Default timestamp is current time if not provided
- Supports both 13-digit (milliseconds) and 10-digit (seconds) timestamps
- Default output is Unix timestamp in milliseconds
- Useful for generating dynamic dates in test scenarios

## Since
5.1.1 (Custom Extension)

## Reference
- [JMeter 二次开发源码](https://gitee.com/azhengzz/JmeterSecondaryDevelopmentForIDEA/blob/master/JMeter_5.1.1/src/extension/com/gitee/qa/jmeter/functions/TimePick.java)
- [Java SimpleDateFormat](https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html)
