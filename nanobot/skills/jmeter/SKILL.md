---
name: jmeter
description: Read this skill for any JMeter script (.jmx) operations: create, modify, edit, update, delete, or execute
metadata: {"nanobot":{"emoji":"🛠","requires":{"bins":["jmeter"]},"os":["linux","darwin","win32"]}}
---

# JMeter Skill

## Basic Information

Test scripts are generated for JMeter 5.1.1+ (compatible with most JMeter versions).

## Workflow

1. **Requirements Analysis**
   - Understand test objectives: performance testing, load testing, stress testing, or functional testing
   - Identify business scenarios and key interfaces
   - Define performance metrics (TPS, response time, concurrent users)

2. **Script Structure Design**
   - Design thread group structure (user count, ramp-up time, loop count)
   - Plan request sequence and dependencies
   - Determine parameterization and data sources

3. **Generate JMX Script**
   - Generate XML structure compliant with JMeter DTD
   - Follow naming conventions with meaningful component names

4. **Validate XML Format**
   ```bash
   # Run validation script
   python scripts/validate_jmx_file.py <jmx file path>
   # Output validation results in JSON format
   python scripts/validate_jmx_file.py <jmx file path> -j
   ```

5. **Execute and Verify**
   - Run jmeter command to execute the script
   - Fix issues based on output and repeat until successful
   ```bash
   # Non-GUI execution
   jmeter -n -t <jmx file path> -l <results-file> -j <log-file>
   ```

6. **Output Script Structure**
   - Display component tree structure in Markdown for user understanding

## Components

### Thread Group
- `Thread Group`: [View Thread Group documentation](./references/thread%20group/Thread%20Group.md)

### Samplers
- `HTTP Request`: [View HTTP Request documentation](./references/samplers/HTTP%20Request.md)

### Configuration Elements
- `HTTP Request Defaults`: [View HTTP Request Defaults documentation](./references/configuration%20elements/HTTP%20Request%20Defaults.md)

### Functions
- `${__functionName(var1,var2,var3)}`: [View Built-in Functions documentation](./references/functions/Functions.md)

## Standards

See [Standards](./references/standards.md) | [Common Bad Cases](./references/bad-cases.md)

Core principles:
- **Naming Conventions**: All components (thread groups, requests, etc.) must have clear, meaningful names
- **Script Language**: Prefer JSR223 + Groovy over BeanShell (better performance)
- **Module Reuse**: Encapsulate reusable business modules as Test Fragment + Module Controller

## Example

Minimal JMeter script with one HTTP request:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.1.1">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Test Plan" enabled="true">
      <stringProp name="TestPlan.comments"></stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      <ResultCollector guiclass="ViewResultsFullVisualizer" testclass="ResultCollector" testname="View Results Tree" enabled="true">
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
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Thread Group" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
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
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="HTTP Request" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
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
