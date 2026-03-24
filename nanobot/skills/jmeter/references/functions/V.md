# __V

## Function Name
`__V`

## Category
Variables

## Description
Evaluate a variable name. This function evaluates a variable name that is itself constructed from variables. It allows for nested variable references.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Variable name | The variable to be evaluated. | Yes |
| 2 | Default value | The default value in case no variable found, if it's empty and no variable found function returns the variable name | No |

## Usage Examples

### Basic nested variable
```
# Assume: prefix=user and N=1
${__V(${prefix}_${N})}
```
Returns the value of `user_1`

### Loop through variables
```
# With counter: i=1,2,3...
${__V(item_${i})}
```
Returns item_1, item_2, item_3... as i increments

### Dynamic column reference
```
# col=2, row_1=A, row_2=B
${__V(row_${col})}
```
Returns: "B"

### Complex nesting
```
# base=data, type=csv, num=1
${__V(${base}_${type}_${num})}
```
Returns value of `data_csv_1`

## Notes
- Solves the problem that `${Var${N}}` doesn't work.
- Essential for dynamic variable names.
- Commonly used with loops/counters.
- The parameter should be a variable reference construction.
- Works on the Test Plan.

## Since
2.3RC3

## Reference
- [Apache JMeter - __V](https://jmeter.apache.org/usermanual/functions.html#__V)
