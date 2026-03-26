# JMeter 常见错误案例

记录实际开发中遇到的问题，帮助避免重复犯错。

## 案例索引

按组件/场景快速查找：

| 问题类型 | 案例 |
|---------|------|
| 变量引用问题 | Case 1.1 |


## 1. 变量引用问题

### Case 1.1: 跨线程组读取变量取不到数值

❌ **错误示例**
```xml
<ThreadGroup testname="Thread Group 1 - 登录">
  <HTTPSamplerProxy testname="POST_登录"/>
  <JSONPostProcessor testname="提取Token">
    <stringProp name="JSON_POST_PROCESSOR">token</stringProp>
    <stringProp name="REFERENCE_NAMES">token</stringProp>
    <stringProp name="JSON_EXPRESSIONS">$.data.token</stringProp>
  </JSONPostProcessor>
</ThreadGroup>

<ThreadGroup testname="Thread Group 2 - 查询订单">
  <!-- 尝试使用 Thread Group 1 中的 token 变量 -->
  <HeaderManager testname="HTTP Header Manager">
    <elementProp name="Authorization" elementType="Header">
      <stringProp name="Header.value">Bearer ${token}</stringProp>
    </elementProp>
  </HeaderManager>
  <HTTPSamplerProxy testname="GET_查询订单"/>
</ThreadGroup>
```

**问题：**
1. JMeter 中**变量(Variables)** 的作用域仅限于当前线程组
2. Thread Group 1 中提取的 `token` 变量，Thread Group 2 无法读取，值为 `${token}` 字符串本身
3. 请求头变成 `Bearer ${token}` 而不是 `Bearer eyJhbGc...`，导致认证失败

✅ **正确做法**

**方案：使用属性(Properties)传递**

```xml
<ThreadGroup testname="Thread Group 1 - 登录">
  <HTTPSamplerProxy testname="POST_登录"/>
  <JSONPostProcessor testname="提取Token">
    <stringProp name="REFERENCE_NAMES">token</stringProp>
    <stringProp name="JSON_EXPRESSIONS">$.data.token</stringProp>
  </JSONPostProcessor>
  <!-- 将变量转为属性，全局可见 -->
  <JSR223PostProcessor testname="存储Token到属性">
    <stringProp name="script">${__setProperty(token, ${token},)}</stringProp>
  </JSR223PostProcessor>
</ThreadGroup>

<ThreadGroup testname="Thread Group 2 - 查询订单">
  <!-- 使用 __P 函数读取属性 -->
  <HeaderManager testname="HTTP Header Manager">
    <elementProp name="Authorization" elementType="Header">
      <stringProp name="Header.value">Bearer ${__P(token,)}</stringProp>
    </elementProp>
  </HeaderManager>
  <HTTPSamplerProxy testname="GET_查询订单"/>
</ThreadGroup>
```


