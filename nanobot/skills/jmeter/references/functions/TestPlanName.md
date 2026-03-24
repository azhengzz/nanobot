# __TestPlanName

## Function Name
`__TestPlanName`

## Category
String

## Description
Return name of current test plan. This function returns the name of the current JMeter test plan.

## Parameters

| # | Parameter | Description | Required |
|---|-----------|-------------|----------|
| - | - | No parameters required. | - |

## Usage Examples

### Basic usage
```
${__TestPlanName}
```
Returns the name of the current test plan.

### In log
```
${__log(Running test plan: ${__TestPlanName})}
```

### In file output
```
results_${__TestPlanName}_${__time(YMD)}.csv
```

### Conditional logic
```
${__TestPlanName} == "My Test Plan"
```

### Store in variable
```
${__TestPlanName}
```
Just returns the test plan name.

## Notes
- Returns the name as displayed in the Test Plan element.
- No parameters required.
- Useful for logging and conditional test logic.
- Can be used to differentiate between test plans.

## Since
2.6

## Reference
- [Apache JMeter - __TestPlanName](https://jmeter.apache.org/usermanual/functions.html#__TestPlanName)
