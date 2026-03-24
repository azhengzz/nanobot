# __RandomDate

## Function Name
`__RandomDate`

## Category
Calculation

## Description
Generate random date within a specific date range. This function returns a random date between two given dates in a specified format.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Time format | Format string for DateTimeFormatter (default `yyyy-MM-dd`) | No |
| 2 | Start date | The start date, the default is *now* | No |
| 3 | End date | The end date | Yes |
| 4 | Locale to use for format | The string format of a locale. The language code must be lowercase. The country code must be uppercase. The separator must be an underscore, e.g. `en_EN`. See http://www.oracle.com/technetwork/java/javase/javase7locales-334809.html. If omitted, by default the function uses the Apache JMeter locale one. | No |
| 5 | Name of variable | The name of the variable to set. | No |

## Usage Examples

### Basic usage
```
${__RandomDate(yyyy-MM-dd,2026-01-01,2026-12-31)}
```
Returns a random date in 2026.

### Store in variable
```
${__RandomDate(dd/MM/yyyy,01/01/2026,31/12/2026,randomDate)}
Date: ${randomDate}
```

### With locale
```
${__RandomDate(MMM dd, yyyy,Jan 01, 2026,Dec 31, 2026,,en)}
```

### For testing date ranges
```
/records?date=${__RandomDate(yyyy-MM-dd,2026-01-01,2026-03-31)}
```

### With time
```
${__RandomDate(yyyy-MM-dd HH:mm:ss,2026-01-01 00:00:00,2026-12-31 23:59:59)}
```

## Notes
- The date format must be valid for SimpleDateFormat.
- Start date must be before end date.
- Locale can be specified for language-specific date handling.
- Returns a formatted string, not a Date object.

## Since
3.3

## Reference
- [Apache JMeter - __RandomDate](https://jmeter.apache.org/usermanual/functions.html#__RandomDate)
