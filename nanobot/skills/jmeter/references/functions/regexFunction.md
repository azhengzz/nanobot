# __regexFunction

## Function Name
`__regexFunction`

## Category
String

## Description
Parse previous response using a regular expression. This function parses the previous response (or the value of a variable) using a regular expression and returns matched values.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | First argument | The first argument is the regular expression to be applied to the response data. It will grab all matches. Any parts of this expression that you wish to use in your template string, be sure to surround in parentheses. Example: `<a href="(.*)">`. This will grab the value of the link and store it as the first group (there is only 1 group). Another example: `<input type="hidden" name="(.*)" value="(.*)">`. This will grab the name as the first group, and the value as the second group. These values can be used in your template string | Yes |
| 2 | Second argument | This is the template string that will replace the function at run-time. To refer to a group captured in the regular expression, use the syntax: `$[group_number]$`. I.e.: `$1$`, or `$2$`. Your template can be any string. | Yes |
| 3 | Third argument | The third argument tells JMeter which match to use. Your regular expression might find numerous matches. You have four choices: <br>- An integer - Tells JMeter to use that match. '1' for the first found match, '2' for the second, and so on<br>- `RAND` - Tells JMeter to choose a match at random.<br>- `ALL` - Tells JMeter to use all matches, and create a template string for each one and then append them all together. This option is little used.<br>- A float number between 0 and 1 - tells JMeter to find the Xth match using the formula: (number_of_matches_found * float_number) rounded to nearest integer. | No, default=1 |
| 4 | Fourth argument | If `ALL` was selected for the above argument value, then this argument will be inserted between each appended copy of the template value. | No |
| 5 | Fifth argument | Default value returned if no match is found | No |
| 6 | Sixth argument | A reference name for reusing the values parsed by this function. Stored values are `${refName}` (the replacement template string) and `${refName_g#}` where "#" is the group number from the regular expression ("0" can be used to refer to the entire match). | No |
| 7 | Seventh argument | Input variable name. If specified, then the value of the variable is used as the input instead of using the previous sample result. | No |

## Usage Examples

### Basic extraction
```
${__regexFunction(<a href="(.*)">",$1$)}
```
Extracts URL from anchor tag.

### Store for reuse
```
${__regexFunction(<input name="(.*)" value="(.*)"/>,$1$,,,$2$,2,refName)}
```
Creates:
- `${refName}` = template result
- `${refName_g0}` = full match
- `${refName_g1}` = first group
- `${refName_g2}` = second group
- `${refName_matchNr}` = number of matches

### Random match
```
${__regexFunction(<item>(.+?)</item>,$1$,RAND)}
```

### All matches
```
${__regexFunction(<value>(.+?)</value>,$1$,ALL,|)}
```
Returns all matches separated by `|`.

### From variable
```
${__regexFunction(pattern,$1$,1,,,refName,inputVar)}
```

### With default
```
${__regexFunction(id=(\d+),$1$,,,not_found,id)}
```

## Template Syntax

| Template | Description |
|----------|-------------|
| $1$ | First captured group |
| $2$ | Second captured group |
| $0$ | Entire match (g0) |

## Generated Variables

When a reference name is provided:
- `{refName}` - The template result
- `{refName}_g0` - Entire match
- `{refName}_g1` - First group
- `{refName}_g2` - Second group
- `{refName}_gn` - nth group
- `{refName}_matchNr` - Number of matches

## Notes
- Parentheses `()` capture groups for extraction.
- Consider using Regular Expression Extractor post-processor as an alternative.
- For distributed testing, ensure proper mode is set in jmeter.properties.

## Since
1.X

## Reference
- [Apache JMeter - __regexFunction](https://jmeter.apache.org/usermanual/functions.html#__regexFunction)
