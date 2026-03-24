# __XPath

## Function Name
`__XPath`

## Category
Input

## Description
Use an XPath expression to read from a file. This function parses an XML file and extracts values using XPath expressions.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | XML file to parse | a XML file to parse | Yes |
| 2 | XPath | a XPath expression to match nodes in the XML file | Yes |

## Usage Examples

### Basic usage
```
${__XPath(data.xml,//book/title)}
```
Extracts the title of a book element.

### Get attribute
```
${__XPath(data.xml,//book/@id)}
```
Extracts the id attribute of book elements.

### Get specific element
```
${__XPath(config.xml,/config/setting[@name='timeout']/value)}
```
Gets a specific setting value.

### Store in variable
```
${__XPath(users.xml,//user[1]/name,userName)}
```

### From property path
```
${__XPath(${__P(xml.file)},//root/value)}
```
Reads file path from property.

## Notes
- The file must contain valid XML.
- XPath expressions must be valid.
- Returns the text content of the matched element(s).
- If multiple matches exist, only the first is returned.
- File is parsed each time the function is called.

## Since
2.0.3

## Reference
- [Apache JMeter - __XPath](https://jmeter.apache.org/usermanual/functions.html#__XPath)
