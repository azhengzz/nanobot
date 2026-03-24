# __counter

## Function Name
`__counter`

## Category
Calculation

## Description
Generate an incrementing number. The counter generates a new number each time it is called, starting with 1 and incrementing by +1 each time. The counter can be configured to keep each simulated user's values separate (per-thread) or use the same counter for all users (global).

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | First argument | `TRUE` if you wish each simulated user's counter to be kept independent and separate from the other users. `FALSE` for a global counter. | Yes |
| 2 | Second argument | A reference name for reusing the value created by this function. Stored values are of the form `${refName}`. This allows you to keep one counter and refer to its value in multiple places. | No |

## Usage Examples

### Per-thread counter
```
${__counter(TRUE)}
```
Each user gets their own counter (1, 2, 3...).

### Global counter
```
${__counter(FALSE)}
```
All users share the same counter (user1=1, user2=2, user3=3...).

### Store in variable
```
${__counter(FALSE,requestNum)}
Request Number: ${requestNum}
```

### In loop controller
```
${__counter(TRUE,iteration)}
Iteration: ${iteration}
```
Tracks iterations per user.

## Notes
- The counter uses an integer variable with a maximum of 2,147,483,647.
- Counter function instances are completely independent.
- Multiple `__counter` function calls in the same iteration won't increment the value further.
- For a count that increments for each sample, use the function in a Pre-Processor.
- Each `__counter` instance maintains its own global counter when `FALSE` is used.

## Important
Multiple `__counter` function calls in the same iteration won't increment the value further. If you want to have a count that increments for each sample, use the function in a Pre-Processor such as User Parameters.

## Since
1.X

## Reference
- [Apache JMeter - __counter](https://jmeter.apache.org/usermanual/functions.html#__counter)
