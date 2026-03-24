# __time

## Function Name
`__time`

## Category
Information

## Description
Return current time in various formats. This function returns the current time in milliseconds (total milliseconds since January 1, 1970 UTC) or in a specified format.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Format | The format to be passed to DateTimeFormatter. The function supports various shorthand aliases, see below. If omitted, the function returns the current time in milliseconds since the epoch. | No |
| 2 | Name of variable | The name of the variable to set. | No |

## Usage Examples

### Get time in milliseconds
```
${__time}
```
Returns current time in milliseconds (e.g., 1698765432123).

### Get time in YMD format
```
${__time(YMD)}
```
Returns date in YYYYMMDD format (e.g., 20260324).

### Custom format
```
${__time(yyyy-MM-dd HH:mm:ss)}
```
Returns formatted date (e.g., 2026-03-24 14:30:45).

### Store in variable
```
${__time(yyyy-MM-dd,timeVar)}
${timeVar}
```
Stores formatted time in variable `timeVar`.

### Format with comma (escape required)
```
${__time(EEE\, d MMM yyyy)}
```
Returns day with comma (e.g., Fri, 24 Mar 2026).

## Common Format Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| YMD | Year Month Day | 20260324 |
| HMS | Hour Minute Second | 143045 |
| yyyy-MM-dd | ISO Date | 2026-03-24 |
| HH:mm:ss | Time | 14:30:45 |
| EEE, d MMM yyyy | Day with comma | Fri, 24 Mar 2026 |

## Notes
- If format contains a comma, it must be escaped with backslash.
- The time returned is in the local timezone of the JMeter machine.

## Since
2.2

## Reference
- [Apache JMeter - __time](https://jmeter.apache.org/usermanual/functions.html#__time)
