
# HTTP Request

## 说明
This sampler lets you send an HTTP/HTTPS request to a web server. It also lets you control whether or not JMeter parses HTML files for images and other embedded resources and sends HTTP requests to retrieve them.

## 参数说明
|Attribute|Description|Required|Example Value|
|---|---|---|---|
|HTTPSampler.protocol|Protocol|No|http or https or file, Default http|
|HTTPSampler.domain|Domain name or IP address of the web server, e.g. www.example.com. [Do not include the http:// prefix.] Note: If the "Host" header is defined in a Header Manager, then this will be used as the virtual host name|No|www.httpbin.org|
|HTTPSampler.port|Port the web server is listening to. Default: 80|No|80|
|HTTPSampler.contentEncoding|Content encoding to be used (for POST, PUT, PATCH and FILE). This is the character encoding to be used, and is not related to the Content-Encoding HTTP header.|No|utf-8|
|HTTPSampler.method|GET, POST, HEAD, TRACE, OPTIONS, PUT, DELETE, PATCH (not supported for JAVA implementation). With HttpClient4, the following methods related to WebDav are also allowed: COPY, LOCK, MKCOL, MOVE, PROPFIND, PROPPATCH, UNLOCK, REPORT, MKCALENDAR, SEARCH.|No|GET、POST、PUT、DELETE、HEAD、OPTIONS、PATCH|
|HTTPSampler.path|The path to resource (for example, /servlets/myServlet). If the resource requires query string parameters, add them below in the `HTTPsampler.Arguments` "Send Parameters With the Request" section.|No|/get|
|HTTPSampler.follow_redirects|This only has any effect if `HTTPSampler.auto_redirects` is `false`. If set, the JMeter sampler will check if the response is a redirect and follow it if so|No|true or false|
|HTTPSampler.auto_redirects|Sets the underlying http protocol handler to automatically follow redirects, so they are not seen by JMeter, and thus will not appear as samples. Should only be used for GET and HEAD requests. The HttpClient sampler will reject attempts to use it for POST or PUT.|No|true or false|
|HTTPSampler.use_keepalive|JMeter sets the Connection: keep-alive header. This does not work properly with the default HTTP implementation, as connection re-use is not under user-control. It does work with the Apache HttpComponents HttpClient implementations.|No|true or false|
|HTTPSampler.DO_MULTIPART_POST|Use a multipart/form-data or application/x-www-form-urlencoded post request.|No|true or false|
|HTTPSampler.BROWSER_COMPATIBLE_MULTIPART|When using multipart/form-data, this suppresses the Content-Type and Content-Transfer-Encoding headers; only the Content-Disposition header is sent.|No|true or false|
|HTTPsampler.Arguments| - `Send Parameters With Request`: The query string will be generated from the list of parameters you provide. Each parameter has a name and value, the options to encode the parameter, and an option to include or exclude an equals sign (some applications don't expect an equals sign when the value is the empty string). The query string will be generated in the correct fashion, depending on the choice of "Method" you made (i.e. if you chose GET or DELETE, the query string will be appended to the URL, if POST or PUT, then it will be sent separately). Also, if you are sending a file using a multipart form, the query string will be created using the multipart form specifications.<br> - `Send JSON Body Data`: Used to send JSON format request data|No|- `Send Parameters With Request`: Parameters must be assembled using `<elementProp name="name" elementType="HTTPArgument"></elementProp>`. <br> - `Send JSON Body Data`: JSON data is only included in `<stringProp name="Argument.value">JSON Body Data</stringProp>`|
|HTTPSampler.postBodyRaw|Should be true if using `Send JSON Body Data` to send data|No|true or false|


## 注意
- `HTTPSampler.domain` is required, unless: it is provided by `HTTP Request Defaults` or a full URL including `scheme`, host and port (scheme://host:port) is set in Path field

## 示例
示例1：使用`Send Parameters With Request`方式发送查询请求
```xml
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="HTTP请求-查询用户" enabled="true">
    <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
        <collectionProp name="Arguments.arguments">
            <elementProp name="name" elementType="HTTPArgument">
                <boolProp name="HTTPArgument.always_encode">false</boolProp>
                <stringProp name="Argument.value">张三</stringProp>
                <stringProp name="Argument.metadata">=</stringProp>
                <boolProp name="HTTPArgument.use_equals">true</boolProp>
                <stringProp name="Argument.name">name</stringProp>
            </elementProp>
            <elementProp name="age" elementType="HTTPArgument">
                <boolProp name="HTTPArgument.always_encode">false</boolProp>
                <stringProp name="Argument.value">23</stringProp>
                <stringProp name="Argument.metadata">=</stringProp>
                <boolProp name="HTTPArgument.use_equals">true</boolProp>
                <stringProp name="Argument.name">age</stringProp>
            </elementProp>
        </collectionProp>
    </elementProp>
    <stringProp name="HTTPSampler.domain">www.httpbin.org</stringProp>
    <stringProp name="HTTPSampler.port"></stringProp>
    <stringProp name="HTTPSampler.protocol">https</stringProp>
    <stringProp name="HTTPSampler.contentEncoding">utf-8</stringProp>
    <stringProp name="HTTPSampler.path">/get</stringProp>
    <stringProp name="HTTPSampler.method">GET</stringProp>
    <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
    <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
    <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
    <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
    <boolProp name="HTTPSampler.BROWSER_COMPATIBLE_MULTIPART">true</boolProp>
    <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
    <stringProp name="HTTPSampler.connect_timeout"></stringProp>
    <stringProp name="HTTPSampler.response_timeout"></stringProp>
</HTTPSamplerProxy>
```
示例2：使用`Send JSON Body Data`方式发送创建请求
```xml
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="HTTP请求-创建用户" enabled="true">
    <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
    <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
        <collectionProp name="Arguments.arguments">
            <elementProp name="" elementType="HTTPArgument">
            <boolProp name="HTTPArgument.always_encode">false</boolProp>
            <stringProp name="Argument.value">{&#xd;
    &quot;name&quot;: &quot;张三&quot;,&#xd;
    &quot;age&quot;: 23,&#xd;
    &quot;address&quot;: &quot;Beijing, China&quot;,&#xd;
    &quot;ip&quot;: &quot;192.168.1.1&quot;&#xd;
    }</stringProp>
            <stringProp name="Argument.metadata">=</stringProp>
            </elementProp>
        </collectionProp>
    </elementProp>
    <stringProp name="HTTPSampler.domain">www.httpbin.org</stringProp>
    <stringProp name="HTTPSampler.port"></stringProp>
    <stringProp name="HTTPSampler.protocol">https</stringProp>
    <stringProp name="HTTPSampler.contentEncoding">utf-8</stringProp>
    <stringProp name="HTTPSampler.path">/post</stringProp>
    <stringProp name="HTTPSampler.method">POST</stringProp>
    <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
    <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
    <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
    <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
    <boolProp name="HTTPSampler.BROWSER_COMPATIBLE_MULTIPART">true</boolProp>
    <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
    <stringProp name="HTTPSampler.connect_timeout"></stringProp>
    <stringProp name="HTTPSampler.response_timeout"></stringProp>
</HTTPSamplerProxy>
```


