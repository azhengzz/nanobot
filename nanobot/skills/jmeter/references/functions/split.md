# __split

## Function Name
`__split`

## Category
Variables

## Description
Split a string into variables. This function splits a string based on a delimiter and stores the parts into separate variables.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | String to split | A delimited string, e.g. "a\|b\|c" | Yes |
| 2 | Name of variable | A reference name for reusing the value computed by this function. | Yes |
| 3 | Delimiter | The delimiter character, e.g. `|`. If omitted, `,` is used. Note that `,` would need to be specified as `\,`. | No |

## Usage Examples

### Basic usage (comma delimiter)
```
${__split(a,b,c,items)}
```
Creates: items_1=a, items_2=b, items_3=c, items_count=3

### Custom delimiter
```
${__split(A|B|C,parts,|)}
```
Creates: parts_1=A, parts_2=B, parts_3=C, parts_count=3

### Space delimiter
```
${__split(word1 word2 word3,words, )}
```
Creates: words_1=word1, words_2=word2, words_3=word3

### From variable
```
${__split(${csvData},row,,)}
```

### Using the split values
```
${__split(1,2,3,nums)}
First: ${nums_1}
Count: ${nums_count}
```

## Generated Variables

After splitting, the following variables are created:
- `{name}_1`, `{name}_2`, ... - Individual parts (1-indexed)
- `{name}_count` - Number of parts
- `{name}` - The original string

## Notes
- Variables are 1-indexed (_1, _2, _3, ...).
- Default delimiter is comma (`,`).
- The `_count` variable contains the number of parts.
- Useful for parsing CSV data or delimited strings.
- Does not work on the Test Plan.

## Since
2.0.2

## Reference
- [Apache JMeter - __split](https://jmeter.apache.org/usermanual/functions.html#__split)
