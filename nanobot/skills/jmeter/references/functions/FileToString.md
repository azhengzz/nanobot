# __FileToString

## Function Name
`__FileToString`

## Category
Input

## Description
Read an entire file. This function reads the entire contents of a file and returns it as a string. Unlike `__StringFromFile` which reads line by line, this reads the whole file at once.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | File Name | Path to the file name. (The path can be relative to the JMeter launch directory) | Yes |
| 2 | File encoding if not the platform default | The encoding to be used to read the file. If not specified, the platform default is used. | No |
| 3 | Variable Name | A reference name - `refName` - for reusing the value created by this function. Stored values are of the form `${refName}`. | No |

## Usage Examples

### Basic usage
```
${__FileToString(payload.json)}
```
Reads entire payload.json file.

### Store in variable
```
${__FileToSend(request.xml,xmlContent)}
```
Stores file content in variable `${xmlContent}`.

### With encoding
```
${__FileToSend(data.txt,content,UTF-8)}
```
Reads file with UTF-8 encoding.

### In HTTP Request body
```
${__FileToSend(/path/to/template.json)}
```
Uses entire file as HTTP request body.

### For POST data
```
${__FileToString(${__P(data.path)},payload,UTF-8)}
```
Reads from property-defined path.

## Notes
- Reads the entire file, not line by line.
- Useful for loading JSON/XML payloads for API testing.
- File is read each time the function is called.
- Consider file size and performance implications.
- Returns the entire file content as a string.

## Since
2.4

## Reference
- [Apache JMeter - __FileToString](https://jmeter.apache.org/usermanual/functions.html#__FileToString)
