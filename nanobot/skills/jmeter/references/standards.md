# JMeter 脚本编写规范

本文档定义了编写高质量 JMeter 测试脚本的标准规范和最佳实践。

## 1. 命名规范

### 1.1 组件命名原则

所有组件必须使用**清晰、有意义、描述性**的名称，避免使用默认名称。

| 组件类型 | 不推荐命名 | 推荐命名 |
|---------|-----------|---------|
| Thread Group | `线程组` | `用户登录场景-100并发` |
| HTTP Request | `HTTP请求` | `POST_用户登录` |
| JSR223 Sampler | `JSR223 Sampler` | `提取Token并存入变量` |
| CSV Data Set Config | `CSV Data Set Config` | `读取用户数据` |

### 1.2 命名格式建议

- **动作开头**：`GET_`, `POST_`, `PUT_`, `DELETE_`
- **功能描述**：简要说明组件作用
- **参数标识**：如需要可包含关键参数

示例：
```
POST_创建订单
GET_查询订单详情_${orderId}
提取响应JSON中的userId
断言_响应状态码为200
```

## 2. 脚本语言选择

### 2.1 优先使用 JSR223 + Groovy

对于需要编写脚本的场景，**必须**使用 JSR223 系列元件并选择 **Groovy** 语言。

**原因对比：**

| 特性 | JSR223 + Groovy | BeanShell |
|------|----------------|-----------|
| 性能 | 快（脚本编译缓存） | 慢（每次解释执行） |
| 并发安全 | 安全 | 存在安全隐患 |
| 语法 | 现代 Java 语法 | 过时语法 |
| 维护性 | 社区活跃推荐 | 逐步淘汰 |

### 2.2 JSR223 元件选择

| 元件 | 用途 |
|------|------|
| JSR223 Sampler | 编写请求逻辑、数据处理 |
| JSR223 PreProcessor | 请求前预处理（参数计算、签名） |
| JSR223 PostProcessor | 响应后处理（数据提取、断言） |
| JSR223 Listener | 自定义结果收集 |

### 2.3 Groovy 脚本示例

```groovy
// JSR223 PreProcessor - 生成时间戳
import java.time.Instant

long timestamp = Instant.now().toEpochMilli()
vars.put("timestamp", timestamp.toString())

// JSR223 PostProcessor - 提取JSON数据
import groovy.json.JsonSlurper

def response = new JsonSlurper().parseText(prev.getResponseDataAsString())
vars.put("userId", response.data.user.id.toString())
```

## 3. 模块复用

### 3.1 使用 Test Fragment 封装重复模块

对于多个测试计划中**重复使用**的业务流程或逻辑模块，应封装为 Test Fragment。

**适用场景：**
- 用户登录/登出流程
- 通用的请求头设置
- 公共的参数提取逻辑
- 重复的业务操作组合

### 3.2 Test Fragment + Module Controller 模式

```
测试计划
├── Test Fragment: 登录模块
│   ├── HTTP Request: 登录接口
│   ├── JSON Extractor: 提取Token
│   └── Cookie Manager
├── Thread Group: 业务场景A
│   ├── Module Controller: 引用登录模块
│   └── HTTP Request: 业务接口A
└── Thread Group: 业务场景B
    ├── Module Controller: 引用登录模块
    └── HTTP Request: 业务接口B
```

**优势：**
- 避免重复配置
- 统一维护，一处修改全局生效
- 提高脚本可读性和可维护性

## 4. 其他最佳实践

### 4.1 参数化

- 使用 **CSV Data Set Config** 进行数据参数化
- 变量名使用小写加下划线：`${user_name}`, `${order_id}`
- CSV 文件放在 `data/` 目录下

### 4.2 断言

- 每个关键请求必须添加断言
- 优先使用 **JSON Assertion** 或 **Response Assertion**
- 断言命名清晰：`断言_状态码200`, `断言_包含success字段`

### 4.3 关联

- 使用 **JSON Extractor** 或 **Regular Expression Extractor** 提取动态数据
- 提取器命名清晰：`提取_订单ID`, `提取_Token`
- 变量作用域合理设置（主线程/子线程）

### 4.4 思考时间

- 模拟真实用户行为，添加适当的思考时间
- 使用 **Flow Control Action** 或 **Uniform Random Timer**

### 4.5 结果收集

- 生产环境压测时禁用图形结果监听器
- 只保留必要的 **Summary Report** 或 **Aggregate Report**
- 使用 `-l` 参数输出结果文件，非GUI模式执行
