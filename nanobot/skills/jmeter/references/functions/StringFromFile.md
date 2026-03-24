# __StringFromFile

## Function Name
`__StringFromFile`

## Category
Input

## Description
Read a line from a file. This function reads a line from a text file and returns its contents. Each time it's called, it reads the next line. When the end of file is reached, it wraps around to the beginning.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | File Name | Path to the file name. (The path can be relative to the JMeter launch directory) If using optional sequence numbers, the path name should be suitable for passing to DecimalFormat. See below for examples. | Yes |
| 2 | Variable Name | A reference name - `refName` - for reusing the value created by this function. Stored values are of the form `${refName}`. Defaults to "`StringFromFile_`". | No |
| 3 | Start sequence number | Initial Sequence number (if omitted, the End sequence number is treated as a loop count) | No |
| 4 | End sequence number | Final sequence number (if omitted, sequence numbers can increase without limit) | No |

## Usage Examples

### Basic usage
```
${__StringFromFile(data.txt)}
```
Reads a line from data.txt.

### Store in variable
```
${__StringFromFile(users.txt,user)}
```
Reads a line and stores in variable `${user}`.

### Multiple files (sequential)
```
${__StringFromFile(data.txt,,1,2)}
```
Will read from data1.txt, then data2.txt.

### With full path
```
${__StringFromFile(/opt/jmeter/data/testdata.txt,line)}
```
Reads from absolute path.

### Using comma in filename (must escape)
```
${__StringFromFile(file\,name.txt)}
```

## Notes
- The file is opened/closed on each read, which may affect performance.
- When end of file is reached, it starts over from the beginning.
- File names can contain comma-separated lists for file rotation.
- If using file lists, the function will cycle through files sequentially.
- Each thread maintains its own file position.

## Since
1.9

## Reference
- [Apache JMeter - __StringFromFile](https://jmeter.apache.org/usermanual/functions.html#__StringFromFile)
