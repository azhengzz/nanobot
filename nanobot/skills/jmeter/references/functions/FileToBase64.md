# __FileToBase64

## Function Name
`__FileToBase64`

## Category
File

## Description
Read a file and convert its contents to Base64 encoded string. Useful for uploading files as base64 in API requests.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | File Path | Full path to the file to be read | Yes |
| 2 | Variable Name | A reference name for reusing the base64 value. | No |

## Usage Examples

### Basic file to base64
```
${__FileToBase64(/path/to/file.pdf)}
```
Returns Base64 encoded string of the file.

### Store in variable
```
${__FileToBase64(/tmp/image.png,base64Data)}
Content: ${base64Data}
```

### In JSON request body
```
{
  "fileName": "test.pdf",
  "fileContent": "${__FileToBase64(/tmp/test.pdf)}"
}
```

### For image upload
```
{
  "image": "${__FileToBase64(C:/images/photo.jpg)}"
}
```

### Multiple files
```
{
  "file1": "${__FileToBase64(/path/file1.txt)}",
  "file2": "${__FileToBase64(/path/file2.txt)}"
}
```

### Store then use
```
${__FileToBase64(/tmp/data.json,jsonBase64)}
{"data": "${jsonBase64}"}
```

## Notes
- Returns `**ERR**` if file cannot be read
- File must exist and be readable
- Reads entire file into memory (not suitable for very large files)
- Base64 encoding increases size by ~33%
- Useful for API testing with file uploads via base64
- Works with binary files (images, PDFs, etc.)

## Since
5.1.1 (Custom Extension)

## Reference
- [JMeter 二次开发源码](https://gitee.com/azhengzz/JmeterSecondaryDevelopmentForIDEA/blob/master/JMeter_5.1.1/src/extension/com/gitee/qa/jmeter/functions/FileToBase64.java)
- [Base64 Encoding](https://en.wikipedia.org/wiki/Base64)
