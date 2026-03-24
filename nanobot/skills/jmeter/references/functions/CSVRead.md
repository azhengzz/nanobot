# __CSVRead

## Function Name
`__CSVRead`

## Category
Input

## Description
Read from CSV delimited file. This function reads a specific cell from a CSV file and returns its contents.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | File Name | The file (or `*ALIAS`) to read from | Yes |
| 2 | Column number | The column number in the file. `0` = first column, `1` = second etc.<br>"`next`" - go to next line of file.<br>`*ALIAS` - open a file and assign it to the alias | Yes |

## Usage Examples

### Read from specific column
```
${__CSVRead(data.txt,0)}
```
Reads the first column (column 0) of the next row.

### Read next value from column
```
${__CSVRead(data.txt,1)}
${__CSVRead(data.txt,next)}
```
Reads from column 1, then moves to next row for subsequent calls.

### Using column alias
```
${__CSVRead(user.txt,username)}  # Column alias defined in file header
${__CSVRead(user.txt,next)}
```

### Multiple columns
```
username=${__CSVRead(users.txt,0)}
password=${__CSVRead(users.txt,1)}
${__CSVRead(users.txt,next)}
```
Reads username from column 0, password from column 1, then moves to next row.

## CSV File Format
The file should be a simple text file with values separated by the delimiter (default is comma).

Example users.txt:
```
user1,pass1
user2,pass2
user3,pass3
```

## Notes
- Column numbering is 0-based.
- The `*next` special value moves to the next row after reading all columns.
- Each thread/group has its own file pointer.
- When end of file is reached, it wraps to the beginning.
- Aliases can be used if the first line contains headers.

## Since
1.9

## Reference
- [Apache JMeter - __CSVRead](https://jmeter.apache.org/usermanual/functions.html#__CSVRead)
