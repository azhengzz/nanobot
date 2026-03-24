# __escapeXml

## Function Name
`__escapeXml`

## Category
String

## Description
Encode strings using XML encoding. This function escapes special characters in a string to their XML entity equivalents.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | String to escape | The string to be escaped. | Yes |

## Usage Examples

### Basic usage
```
${__escapeXml(<tag>value</tag>)}
```
Returns: "&lt;tag&gt;value&lt;/tag&gt;"

### Special characters
```
${__escapeXml(AT&T)}
```
Returns: "AT&amp;T"

### Quotes
```
${__escapeXml(AT&T's "store")}
```
Returns: "AT&amp;T&apos;s &quot;store&quot;"

### With variable
```
${__escapeXml(${userInput})}
```

### In XML body
```
<data>${__escapeXml(${content})}</data>
```

## Character Mappings

| Character | Escaped As |
|-----------|------------|
| < | &lt; |
| > | &gt; |
| & | &amp; |
| " | &quot; |
| ' | &apos; |

## Notes
- Escapes <, >, &, ", and ' characters.
- Similar to `__escapeHtml` but more appropriate for XML.
- Use before inserting values into XML documents.
- Prevents XML injection attacks.

## Since
3.2

## Reference
- [Apache JMeter - __escapeXml](https://jmeter.apache.org/usermanual/functions.html#__escapeXml)
