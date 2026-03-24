# __unescapeHtml

## Function Name
`__unescapeHtml`

## Category
String

## Description
Decode HTML-encoded strings. This function converts HTML entities back to their original characters.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | String to unescape | The string to be unescaped. | Yes |

## Usage Examples

### Basic usage
```
${__unescapeHtml(&lt;div&gt;Hello&lt;/div&gt;)}
```
Returns: "<div>Hello</div>"

### Decode ampersand
```
${__unescapeHtml(AT&amp;T)}
```
Returns: "AT&T"

### Decode quotes
```
${__unescapeHtml(&quot;Hello&quot;)}
```
Returns: "\"Hello\""

### With variable
```
${__unescapeHtml(${htmlResponse})}
```

### Process API response
```
${__unescapeHtml(${response})}
```

## Entity Conversions

| Entity | Character |
|--------|-----------|
| &lt; | < |
| &gt; | > |
| &amp; | & |
| &quot; | " |
| &apos; | ' |
| &#39; | ' |
| &#nnn; | ASCII character nnn |
| &#xHHH; | Unicode character HHH |

## Notes
- Converts HTML entities to their character equivalents.
- Inverse of `__escapeHtml`.
- Handles numeric entities (&#nnn; and &#xHHH;).
- Useful for processing HTML responses.

## Since
2.3.3

## Reference
- [Apache JMeter - __unescapeHtml](https://jmeter.apache.org/usermanual/functions.html#__unescapeHtml)
