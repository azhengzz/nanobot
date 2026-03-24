# __timeShift

## Function Name
`__timeShift`

## Category
Information

## Description
Return a date in various formats with the specified amount of seconds/minutes/hours/days added to or subtracted from a base date. This function allows you to calculate dates relative to the current time or a specified date.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Format | The format to be passed to DateTimeFormatter (for input data parsing and output formating). See DateTimeFormatter. If omitted, the function uses milliseconds since epoch format. | No |
| 2 | Date to shift | Indicate the date in the format set by the parameter `Format` to shift. If omitted, the date is set to *ZonedDateTime.now* with system zone *ZoneId.systemDefault()*. | No |
| 3 | value to shift | Indicate the specified amount of seconds, minutes, hours or days to shift according to a textual representation of a duration such as `PnDTnHnMn.nS`. See Duration#parse(CharSequence). If ommitted, no shifting will be done. | No |
| 4 | Locale to use for format | The locale used to format the date | No |
| 5 | Name of variable | The name of the variable to set. | No |

## Usage Examples

### Get yesterday's date
```
${__timeShift(yyyy-MM-dd,,P-1D)}
```
Returns yesterday's date (e.g., 2026-03-23).

### Get date 7 days from now
```
${__timeShift(dd/MM/yyyy,,P7D)}
```
Returns date 7 days in the future.

### Get time 2 hours ago
```
${__timeShift(HH:mm:ss,,P-2H)}
```
Returns time 2 hours ago.

### From specific date
```
${__timeShift(yyyy-MM-dd,2026-01-01,P30D)}
```
Returns 30 days after January 1, 2026.

### Store in variable
```
${__timeShift(yyyy-MM-dd HH:mm:ss,,,futureTime)}
${futureTime}
```

### Complex shift
```
${__timeShift(yyyy-MM-dd HH:mm:ss,,P1D2H30M)}
```
Returns date/time 1 day, 2 hours, and 30 minutes from now.

## Shift Format Examples

| Format | Description |
|--------|-------------|
| P-1D | Minus 1 day |
| P7D | Plus 7 days |
| P-2H | Minus 2 hours |
| P30M | Plus 30 minutes |
| P1D2H3M4S | Plus 1 day, 2 hours, 3 minutes, 4 seconds |

## Notes
- The shift format uses ISO-8601 duration format (P prefix).
- Negative values are supported for shifting to the past.
- If the base date is omitted, current time is used.
- Locale can be specified for language-specific date formatting.

## Since
3.3

## Reference
- [Apache JMeter - __timeShift](https://jmeter.apache.org/usermanual/functions.html#__timeShift)
