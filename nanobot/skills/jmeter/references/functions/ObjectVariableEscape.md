# __Oe

## Function Name
`__Oe`

## Category
String

## Description
Extract value from an object variable using JsonPath expression and escape special characters (backslashes and quotes). This function is useful when you need to use extracted values in JSON strings.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Object.JsonPath | The object variable name followed by JsonPath expression (e.g., `objVarName.name`) | Yes |
| 2 | Variable Name | A reference name for reusing the escaped value. | No |

## Usage Examples

### Extract and escape string value
```
${__Oe(userInfo.name)}
```
Returns escaped string value from `userInfo` object at `name` field.

### Store in variable
```
${__Oe(responseObj.data.token,escapedToken)}
Token: ${escapedToken}
```

### Use in JSON body
```
{"username": "${__Oe(userObj.name)}", "id": "${__Oe(userObj.id)}"}
```

### Extract nested value
```
${__Oe(apiResponse.result.data[0].value)}
```

### Extract from list
```
${__Oe(itemsList[0].name)}
```

## Notes
- Escapes backslashes (`\` → `\\`) and quotes (`"` → `\"`)
- Works with object variables stored in JMeter context
- Returns null if object or JsonPath is invalid
- Object must be a String, List, or Map type
- No need to prefix with `$` - just use dot notation after variable name
- Useful for embedding extracted values in JSON request bodies
- Extension of `__O` function with automatic escaping

## Since
5.1.1 (Custom Extension)

## Reference
- [JMeter 二次开发源码](https://gitee.com/azhengzz/JmeterSecondaryDevelopmentForIDEA/blob/master/JMeter_5.1.1/src/extension/com/gitee/qa/jmeter/functions/ObjectVariableEscape.java)
- [JsonPath - GitHub](https://github.com/json-path/JsonPath)
