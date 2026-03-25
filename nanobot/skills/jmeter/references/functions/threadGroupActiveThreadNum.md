# __threadGroupActiveThreadNum

## Function Name
`__threadGroupActiveThreadNum`

## Category
Information

## Description
Get the number of active threads in the current thread group. Optionally rounds up to the nearest multiple of a step value.

## Parameters

| # | Attribute | Description | Required |
|---|-----------|-------------|----------|
| 1 | Step | Round up the thread count to this multiple (optional) | No |

## Usage Examples

### Get current active thread count
```
${__threadGroupActiveThreadNum}
```
Returns the exact number of active threads in current thread group.

### Round up to nearest 10
```
${__threadGroupActiveThreadNum(10)}
```
If actual threads is 23, returns 30.

### Round up to nearest 5
```
${__threadGroupActiveThreadNum(5)}
```
If actual threads is 13, returns 15.

### In request parameter
```
/endpoint?threadCount=${__threadGroupActiveThreadNum}
```

### For load calculation
```
Load per thread: ${__threadGroupActiveThreadNum(10)}
```

## Notes
- Returns current thread group's active thread count (not global JMeter threads)
- Without step parameter, returns exact thread count
- With step parameter, rounds up to nearest multiple of step
- Useful for dynamic test scenarios based on thread count
- Can be used for per-thread data allocation
- Step value must be a positive integer

## Since
5.1.1 (Custom Extension)

## Reference
- [JMeter 二次开发源码](https://gitee.com/azhengzz/JmeterSecondaryDevelopmentForIDEA/blob/master/JMeter_5.1.1/src/extension/com/gitee/qa/jmeter/functions/ThreadGroupActiveThreadNum.java)
