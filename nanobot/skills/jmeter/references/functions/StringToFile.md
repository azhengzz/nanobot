# __StringToFile

## Function Name
`__StringToFile`

## Category
Input

## Description
Write a string to a file. This function writes a string to a specified file. Useful for recording data during test execution.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Path to file | Path to the file name.(The path is absolute) | Yes |
| 2 | String to write | The string to write to the file. If you need to insert a line break in your content, use `\n` in your string. | Yes |
| 3 | Append to file? | The way to write the string, `true` means append, `false` means overwrite. If not specified, the default append is `true`. | No |
| 4 | File encoding if not UTF-8 | The encoding to be used to write to the file. If not specified, the default encoding is `UTF-8`. | No |

## Usage Examples

### Basic usage
```
${__StringToFile(output.txt,Hello World)}
```
Writes "Hello World" to output.txt (overwrites).

### Append to file
```
${__StringToFile(log.txt,Request: ${url},UTF-8,true)}
```
Appends request info to log file.

### Store response data
```
${__StringToFile(responses/${__threadNum}.txt,${response})}
```
Writes each thread's response to separate file.

### Record timestamp
```
${__StringToFile(timestamps.txt,${__time(dd/MM/yyyy HH:mm:ss)},UTF-8,true)}
```
Appends timestamps to a file.

### With variable data
```
${__StringToFile(results.csv,${userId},${productId},${status},UTF-8,true)}
```
Appends CSV row with test data.

## Notes
- Creates parent directories if they don't exist.
- Useful for debugging and data collection.
- Append mode allows building logs/CSV files during test.
- Each write operation opens and closes the file.

## Since
5.2

## Reference
- [Apache JMeter - __StringToFile](https://jmeter.apache.org/usermanual/functions.html#__StringToFile)
