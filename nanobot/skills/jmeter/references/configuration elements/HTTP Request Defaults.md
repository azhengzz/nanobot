
# HTTP Request Defaults

## Description
The `HTTP Request Defaults` element is a configuration element that sets default values for `HTTP Request` samplers. This allows you to avoid repeating the same values for multiple `HTTP Request` samplers. Any `HTTP Request` sampler that uses this configuration element will inherit the default values. If a parameter is specified in both the `HTTP Request Defaults` and the `HTTP Request` sampler, the value in the `HTTP Request` sampler takes precedence.

This element is particularly useful when testing a single application, where all or most of the `HTTP requests` use the same server, port, protocol, or other common parameters.

## Parameters
|Attribute|Description|Required|Example Value|
|---|---|---|---|
|HTTPSampler.protocol|Protocol|No|http or https or file, Default http|
|HTTPSampler.domain|Domain name or IP address of the web server. E.g. www.example.com. Do not include the http:// prefix.|No|www.httpbin.org|
|HTTPSampler.port|Port the web server is listening to.|No|80 or 443|
|HTTPSampler.contentEncoding|The encoding to be used for the request.|No|utf-8|
|HTTPSampler.path|The default path to resource. Individual samplers can override this value.|No|/api|
|HTTPsampler.Arguments| - `Send Parameters With Request`: The query string will be generated from the list of parameters you provide. Each parameter has a name and value. The query string will be generated in the correct fashion, depending on the choice of "Method" you made (i.e. if you chose GET, the query string will be appended to the URL, if POST, then it will be sent separately). Also, if you are sending a file using a multipart form, the query string will be created using the multipart form specifications.<br> - `Send Files With Request`: Default files to be sent with each request.|No|See examples below|
|HTTPSampler.postBodyRaw|Should be true if using `Send JSON Body Data` to send data by default|No|true or false|


## Notes
- HTTP Request Defaults only provides default values. Individual HTTP Request samplers can override any of these values.
- This element should be placed at the same level or higher in the test plan tree than the HTTP Request samplers that need to use it.
- The most common use case is to set the server name/domain, port, protocol, and encoding once, rather than for each HTTP Request sampler.
- If you need different defaults for different groups of requests, you can use multiple HTTP Request Defaults elements by scoping them appropriately.

## Examples

Example 1: Basic HTTP Request Defaults configuration
```xml
<ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement" testname="HTTP Request Defaults" enabled="true">
  <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
    <collectionProp name="Arguments.arguments"/>
  </elementProp>
  <stringProp name="HTTPSampler.domain">www.httpbin.org</stringProp>
  <stringProp name="HTTPSampler.port">443</stringProp>
  <stringProp name="HTTPSampler.protocol">https</stringProp>
  <stringProp name="HTTPSampler.contentEncoding">utf-8</stringProp>
  <stringProp name="HTTPSampler.path"></stringProp>
  <stringProp name="HTTPSampler.concurrentPool">6</stringProp>
  <stringProp name="HTTPSampler.connect_timeout"></stringProp>
  <stringProp name="HTTPSampler.response_timeout"></stringProp>
</ConfigTestElement>
<hashTree/>
```

Example 2: HTTP Request Defaults with default parameters
```xml
<ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement" testname="HTTP Request Defaults - With Parameters" enabled="true">
  <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
    <collectionProp name="Arguments.arguments">
      <elementProp name="token" elementType="HTTPArgument">
        <boolProp name="HTTPArgument.always_encode">false</boolProp>
        <stringProp name="Argument.value">default-token-value</stringProp>
        <stringProp name="Argument.metadata">=</stringProp>
        <boolProp name="HTTPArgument.use_equals">true</boolProp>
        <stringProp name="Argument.name">token</stringProp>
      </elementProp>
      <elementProp name="api_key" elementType="HTTPArgument">
        <boolProp name="HTTPArgument.always_encode">false</boolProp>
        <stringProp name="Argument.value">your-api-key</stringProp>
        <stringProp name="Argument.metadata">=</stringProp>
        <boolProp name="HTTPArgument.use_equals">true</boolProp>
        <stringProp name="Argument.name">api_key</stringProp>
      </elementProp>
    </collectionProp>
  </elementProp>
  <stringProp name="HTTPSampler.domain">api.example.com</stringProp>
  <stringProp name="HTTPSampler.port">443</stringProp>
  <stringProp name="HTTPSampler.protocol">https</stringProp>
  <stringProp name="HTTPSampler.contentEncoding">utf-8</stringProp>
  <stringProp name="HTTPSampler.path">/api/v1</stringProp>
  <stringProp name="HTTPSampler.concurrentPool">6</stringProp>
  <stringProp name="HTTPSampler.connect_timeout"></stringProp>
  <stringProp name="HTTPSampler.response_timeout"></stringProp>
</ConfigTestElement>
<hashTree/>
```


## Use Cases

1. **Single Server Testing**: Set the server name/IP, port, and protocol once when all requests are sent to the same server
2. **Unified Timeout Settings**: Set uniform connection and response timeouts for all HTTP requests
3. **Default Headers**: While HTTP Request Defaults doesn't directly set headers, it can be used with HTTP Header Manager to achieve default headers
4. **Default Encoding**: Set a uniform character encoding (such as UTF-8) to avoid setting it for each request

## Best Practices
- Place HTTP Request Defaults at a high level in the test plan (e.g., directly under Thread Group) so its scope covers all required requests
- Only set truly common parameters in HTTP Request Defaults to avoid over-configuration
- Use meaningful names to identify HTTP Request Defaults elements for easier maintenance
- For multi-environment testing (dev/test/production), consider using properties to configure server addresses

