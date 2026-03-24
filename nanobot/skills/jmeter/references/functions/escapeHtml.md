# __escapeHtml

## Function Name
`__escapeHtml`

## Category
String

## Description
Encode strings using HTML encoding. This function escapes special characters in a string to their HTML entity equivalents.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | String to escape | The string to be escaped. | Yes |

## Usage Examples

### Basic usage
```
${__escapeHtml(<div>Hello</div>)}
```
Returns: "&lt;div&gt;Hello&lt;/div&gt;"

### Special characters
```
${__escapeHtml(AT&T)}
```
Returns: "AT&amp;T"

### Quotes
```
${__escapeHtml("Hello" she said)}
```
Returns: "&quot;Hello&quot; she said"

### With variable
```
${__escapeHtml(${userInput})}
```

### In JSON body
```
{"html": "${__escapeHtml(${content})}"}
```

## Character Mappings

| Character | Escaped As |
|-----------|------------|
| < | &lt; |
| > | &gt; |
| & | &amp; |
| " | &quot; |
| ' | &#39; or &apos; |

## Notes
- Escapes <, >, &, ", and other special characters.
- Useful for preventing XSS in HTML contexts.
- Use before inserting user input into HTML.

## Since
2.3.3

## Reference
- [Apache JMeter - __escapeHtml](https://jmeter.apache.org/usermanual/functions.html#__escapeHtml)
