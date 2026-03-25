---
name: jmeter
description: 编写、修改、执行JMeter脚本文件(.jmx).
metadata: {"nanobot":{"emoji":"🛠","requires":{"bins":["jmeter"]},"os":["linux","darwin","win32"]}}
---

# JMeter Skill


## 基本信息
- JMeter Version：5.1.1

## 工作流程

1. **需求分析与拆解**
   - 理解测试目标：性能测试、压力测试、功能测试？
   - 确定业务场景和关键接口
   - 明确性能指标（TPS、响应时间、并发数）

2. **脚本结构设计**
   - 设计线程组结构（用户数、ramp-up时间、循环次数）
   - 规划请求顺序和依赖关系
   - 确定参数化和数据来源

3. **生成JMX脚本**
   - 根据设计生成符合 JMeter DTD 的 XML 结构
   - 遵循命名规范，使用有意义的组件名称

4. **校验XML格式**
   ```bash
   # 执行校验脚本
   python scripts/validate_jmx_file.py <jmx file path>
   # 以json格式输出校验结果
   python scripts/validate_jmx_file.py <jmx file path> -j
   ```

5. **执行验证**
   - 运行jmeter命令执行脚本进行测试
   - 根据输出结果修复脚本，并重复以上工作流程直到执行成功
   ```bash
   # 非Gui方式执行脚本
   jmeter -n -t <jmx file path> -l <results-file> -j <log-file>
   ```

6. **输出脚本结构**
   - 使用 Markdown 输出组件树结构，便于用户理解

## 组件

### Thread Group
- `Thread Group`：[跳转到 Thread Group 组件说明](./references/thread%20group/Thread%20Group.md)

### Samplers
- `HTTP Request`：[跳转到 HTTP Request 组件说明](./references/samplers/HTTP%20Request.md)

### Configuration Elements
- `HTTP Request Defaults`：[跳转到 HTTP Request Defaults 组件说明](./references/configuration%20elements/HTTP%20Request%20Defaults.md)

### Assertions


### Functions
- `${__functionName(var1,var2,var3)}`：[跳转到内置 Functions 说明](./references/functions/Functions.md)


## 规范
- 命名规范：所有组件（线程组、请求等）必须有清晰、有意义的名称。
- 使用 JSR223 而非 BeanShell：对于复杂的逻辑处理，建议使用 JSR223 Sampler 并选择 Groovy 语言，因为它的性能远优于 BeanShell 。
- 测试片段：对于重复使用的业务模块，建议封装成 Test Fragment 配合 Module Controller 实现复用 。


## 示例
最基本的包含一个HTTP请求的JMeter脚本示例
```xml
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.1.1">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="测试计划" enabled="true">
      <stringProp name="TestPlan.comments"></stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      <ResultCollector guiclass="ViewResultsFullVisualizer" testclass="ResultCollector" testname="察看结果树" enabled="true">
        <boolProp name="ResultCollector.error_logging">false</boolProp>
        <objProp>
          <name>saveConfig</name>
          <value class="SampleSaveConfiguration">
            <time>true</time>
            <latency>true</latency>
            <timestamp>true</timestamp>
            <success>true</success>
            <label>true</label>
            <code>true</code>
            <message>true</message>
            <threadName>true</threadName>
            <dataType>true</dataType>
            <encoding>true</encoding>
            <assertions>true</assertions>
            <subresults>true</subresults>
            <responseData>true</responseData>
            <samplerData>true</samplerData>
            <xml>true</xml>
            <fieldNames>true</fieldNames>
            <responseHeaders>true</responseHeaders>
            <requestHeaders>true</requestHeaders>
            <responseDataOnError>true</responseDataOnError>
            <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
            <assertionsResultsToSave>2</assertionsResultsToSave>
            <bytes>true</bytes>
            <sentBytes>true</sentBytes>
            <url>true</url>
            <fileName>true</fileName>
            <threadCounts>true</threadCounts>
            <sampleCount>true</sampleCount>
            <idleTime>true</idleTime>
            <connectTime>true</connectTime>
          </value>
        </objProp>
        <stringProp name="filename"></stringProp>
      </ResultCollector>
      <hashTree/>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="线程组" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">1</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">1</stringProp>
        <stringProp name="ThreadGroup.ramp_time">1</stringProp>
        <boolProp name="ThreadGroup.scheduler">false</boolProp>
        <stringProp name="ThreadGroup.duration"></stringProp>
        <stringProp name="ThreadGroup.delay"></stringProp>
      </ThreadGroup>
      <hashTree>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="HTTP请求" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true">
            <collectionProp name="Arguments.arguments"/>
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
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout"></stringProp>
          <stringProp name="HTTPSampler.response_timeout"></stringProp>
        </HTTPSamplerProxy>
        <hashTree/>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
```



