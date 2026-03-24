# __eval

## Function Name
`__eval`

## Category
Variables

## Description
Evaluate a variable expression. This function evaluates a string containing variable references and replaces them with their values.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Variable name | The variable to be evaluated. | Yes |

## Usage Examples

### Basic usage
```
# Assume: path=/api and endpoint=users
${__eval(${path}/${endpoint})}
```
Returns: "/api/users"

### With nested variables
```
# Assume: prefix=user and id=123
${__eval(${prefix}_${id})}
```
Returns: "user_123"

### From stored expression
```
# Assume: expr=${__time(YMD)}_${__threadNum}
${__eval(${expr})}
```

### Dynamic path building
```
# base=/v1, resource=items
${__eval(${base}/${resource})}
```

## Notes
- Unlike `${Var}`, `__eval` processes nested variable references.
- Useful for building dynamic strings from multiple variables.
- The parameter should be a variable name (not a literal string).
- For evaluating variable names, use `__V` instead.

## Since
2.3.1

## Reference
- [Apache JMeter - __eval](https://jmeter.apache.org/usermanual/functions.html#__eval)
