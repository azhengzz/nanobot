# __samplerName

## Function Name
`__samplerName`

## Category
Information

## Description
Get the sampler name (label). This function returns the name/label of the current sampler.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Variable Name | A reference name - `refName` - for reusing the value created by this function. Stored values are of the form `${refName}`. | No |

## Usage Examples

### Basic Usage
```
${__samplerName}
```
Returns the name of the current sampler.

### In HTTP Request
```
/path?source=${__samplerName}
```
Includes the sampler name as a parameter.

## Notes
- Useful for tracking which sampler is currently being executed.

## Since
2.5

## Reference
- [Apache JMeter - __samplerName](https://jmeter.apache.org/usermanual/functions.html#__samplerName)
