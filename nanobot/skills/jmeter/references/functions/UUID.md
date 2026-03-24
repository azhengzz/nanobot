# __UUID

## Function Name
`__UUID`

## Category
Calculation

## Description
Generate a random type 4 UUID. This function generates a random Universally Unique Identifier (UUID) following the UUID version 4 specification.

## Parameters

No parameters.

## Usage Examples

### Basic usage
```
${__UUID}
```
Returns a random UUID like: "550e8400-e29b-41d4-a716-446655440000"

### Store in variable
```
${__UUID(sessionId)}
Session ID: ${sessionId}
```

### In HTTP request
```
/headers?X-Request-ID=${__UUID}
```

### For tracking
```
/tracking?id=${__UUID}&user=${userId}
```

### In JSON body
```
{"id": "${__UUID}", "name": "test"}
```

## Notes
- Generates a version 4 (random) UUID.
- Format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
- Each call generates a new unique identifier.
- Useful for generating unique IDs, session tokens, etc.
- No parameters required.

## Since
2.9

## Reference
- [Apache JMeter - __UUID](https://jmeter.apache.org/usermanual/functions.html#__UUID)
