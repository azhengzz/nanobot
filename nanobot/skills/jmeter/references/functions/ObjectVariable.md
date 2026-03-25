# __O

## Function Name
`__O`

## Category
String

## Description
Extract values from object variables using JsonPath expressions. Supports extracting data from JSON objects, arrays, and nested structures stored in JMeter variables.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Object.JsonPath | The object variable name followed by JsonPath expression (e.g., `objVarName.name`) | Yes |
| 2 | Variable Name | A reference name for storing the extracted object. | No |

## Usage Examples

### Extract string value
```
${__O(response.name)}
```
Returns the value of `name` field from `response` object.

### Extract nested value
```
${__O(apiResponse.data.user.id)}
```

### Extract from array
```
${__O(items[0].name)}
```
Returns the `name` field from the first item in `items` array.

### Extract entire array
```
${__O(result.data.items)}
```
Returns JSON string of the items array.

### Store in variable
```
${__O(userInfo.data,userData)}
userData: ${userData}
```

### Get entire object
```
${__O(response)}
```
Returns the entire `response` object as JSON string.

### Filter array
```
${__O(products[?(@.price > 100)].name)}
```
Returns names of products with price > 100.

### Multiple fields
```
${__O(obj.data[0,1,2])}
```
Returns first 3 items from data array.

## JsonPath Examples

| Usage | JsonPath Executed | Description |
|-------|-------------------|-------------|
| `${__O(obj.name)}` | `$.name` | Root level `name` field |
| `${__O(obj.data.user.id)}` | `$.data.user.id` | Nested `id` field |
| `${__O(obj[0])}` | `$[0]` | First element of array |
| `${__O(obj[0].name)}` | `$[0].name` | `name` from first array element |
| `${__O(obj[*].id)}` | `$[*].id` | All `id` values from array |
| `${__O(obj[?(@.active==true)])}` | `$[?(@.active==true)]` | Filter items where `active` is true |
| `${__O(obj.data.*)}` | `$.data.*` | All values in `data` object |

## Notes
- Works with object variables stored in JMeter context
- Returns null if object doesn't exist or JsonPath is invalid
- Works with String, List, and Map objects
- No need to prefix with `$` - just use dot notation after variable name

## Since
5.1.1 (Custom Extension)

## Reference
- [JMeter 二次开发源码](https://gitee.com/azhengzz/JmeterSecondaryDevelopmentForIDEA/blob/master/JMeter_5.1.1/src/extension/com/gitee/qa/jmeter/functions/ObjectVariable.java)
- [JsonPath Syntax](https://github.com/json-path/JsonPath#path-examples)
