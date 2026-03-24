# __threadGroupName

## Function Name
`__threadGroupName`

## Category
Information

## Description
The thread group name function simply returns the name of the thread group being executed.

## Parameters

There are no arguments for this function.

## Usage Examples

### Basic Usage
```
${__threadGroupName}
```
Returns the name of the current thread group.

### In Log Output
```
${__log(Thread Group: ${__threadGroupName})}
```
Logs the current thread group name.

## Notes
- This function does not work in any Configuration elements (e.g. User Defined Variables) as these are run from a separate thread.
- Does not make sense to use it on the Test Plan.

## Since
4.1

## Reference
- [Apache JMeter - __threadGroupName](https://jmeter.apache.org/usermanual/functions.html#__threadGroupName)
