
# Thread Group

## 说明
Thread Group（线程组）是 JMeter 测试计划的起点，用于定义虚拟用户数量、循环次数和测试执行行为。每个线程代表一个虚拟用户，线程组可以控制并发用户的加载方式、执行持续时间、启动延迟等核心测试参数，支持性能测试、压力测试、负载测试等多种场景


## 参数说明
|Attribute|Required|Description|Not Null|Example Value|
|---|---|---|---|---|
|ThreadGroup.on_sample_error|Yes|Determines what happens if a sampler error occurs, either because the sample itself failed or an assertion failed.|No|`continue` - ignore the error and continue with the test<br>`startnextloop` - ignore the error, start next loop and continue with the test<br>`stopthread` - current thread exits<br>`stoptest` - the entire test is stopped at the end of any current samples<br>`stoptestnow` - the entire test is stopped abruptly. Any current samplers are interrupted if possible.|
|ThreadGroup.num_threads|Yes|Number of users to simulate|Yes|`10` (虚拟用户数)|
|ThreadGroup.ramp_time|Yes|How long JMeter should take to get all the threads started. If there are 10 threads and a ramp-up time of 100 seconds, then each thread will begin 10 seconds after the previous thread started, for a total time of 100 seconds to get the test fully up to speed.|Yes|`5` (启动间隔时间)|
|LoopController.continue_forever|Yes|Loop Forever|No|`false`|
|LoopController.loops|Yes|Loop Count|Yes|`-1` 永久循环<br>`10` (循环次数)|
|ThreadGroup.scheduler|Yes|If `true`, confines Thread operation time to the given bounds|No|`true` or `false` (是否启用调度器)|
|ThreadGroup.delayedStart|Yes|If `true`, threads are created only when the appropriate proportion of the ramp-up time has elapsed. This is most appropriate for tests with a ramp-up time that is significantly longer than the time to execute a single thread. I.e. where earlier threads finish before later ones start.<br>If `false`, all threads are created when the test starts (they then pause for the appropriate proportion of the ramp-up time). This is the original default, and is appropriate for tests where threads are active throughout most of the test.|Yes|`true` or `false` (是否启用调度器)|
|ThreadGroup.duration|Yes|If the scheduler is `true`, one can choose a relative end time. JMeter will use this to calculate the End Time.|No|`60` (持续时间)|
|ThreadGroup.delay|Yes|If the scheduler is `true`, one can choose a relative startup delay. JMeter will use this to calculate the Start Time.|No|`0` (启动延迟)|


### 线程组类型
|类型|说明|
|---|---|
|ThreadGroup|普通线程组，用于常规性能测试|
|SetupThreadGroup|前置线程组，在主测试前执行，用于初始化环境|
|PostThreadGroup|后置线程组，在主测试后执行，用于清理环境|

### 调度器配置
当 `ThreadGroup.scheduler` 为 `true` 时，可以设置以下参数：
- **Duration**：测试持续时间（秒）
- **Startup Delay**：启动延迟时间（秒），测试计划开始后等待多长时间再启动线程组

示例1：基本线程组配置
```xml
<ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="线程组-用户登录" enabled="true">
    <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
    <stringProp name="ThreadGroup.num_threads">10</stringProp>
    <stringProp name="ThreadGroup.ramp_time">5</stringProp>
    <boolProp name="ThreadGroup.delayedStart">false</boolProp>
    <boolProp name="ThreadGroup.scheduler">false</boolProp>
    <stringProp name="ThreadGroup.duration"></stringProp>
    <stringProp name="ThreadGroup.delay"></stringProp>
    <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
        <boolProp name="LoopController.continue_forever">false</boolProp>
        <stringProp name="LoopController.loops">10</stringProp>
    </elementProp>
</ThreadGroup>
```

示例2：使用调度器的线程组
```xml
<ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="线程组-持续压测" enabled="true">
    <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
    <stringProp name="ThreadGroup.num_threads">50</stringProp>
    <stringProp name="ThreadGroup.ramp_time">30</stringProp>
    <boolProp name="ThreadGroup.delayedStart">false</boolProp>
    <boolProp name="ThreadGroup.scheduler">true</boolProp>
    <stringProp name="ThreadGroup.duration">300</stringProp>
    <stringProp name="ThreadGroup.delay">10</stringProp>
    <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
        <boolProp name="LoopController.continue_forever">true</boolProp>
        <stringProp name="LoopController.loops">-1</stringProp>
    </elementProp>
</ThreadGroup>
```

示例3：setup Thread Group（前置线程组）
```xml
<SetupThreadGroup guiclass="SetupThreadGroupGui" testclass="SetupThreadGroup" testname="setUp线程组-初始化数据" enabled="true">
    <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
    <stringProp name="ThreadGroup.num_threads">1</stringProp>
    <stringProp name="ThreadGroup.ramp_time">1</stringProp>
    <boolProp name="ThreadGroup.delayedStart">false</boolProp>
    <boolProp name="ThreadGroup.scheduler">false</boolProp>
    <stringProp name="ThreadGroup.duration"></stringProp>
    <stringProp name="ThreadGroup.delay"></stringProp>
    <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
        <boolProp name="LoopController.continue_forever">false</boolProp>
        <stringProp name="LoopController.loops">1</stringProp>
    </elementProp>
</SetupThreadGroup>
```

示例4：tearDown Thread Group（后置线程组）
```xml
<PostThreadGroup guiclass="PostThreadGroupGui" testclass="PostThreadGroup" testname="tearDown线程组-清理数据" enabled="true">
    <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
    <stringProp name="ThreadGroup.num_threads">1</stringProp>
    <stringProp name="ThreadGroup.ramp_time">1</stringProp>
    <boolProp name="ThreadGroup.delayedStart">false</boolProp>
    <boolProp name="ThreadGroup.scheduler">false</boolProp>
    <stringProp name="ThreadGroup.duration"></stringProp>
    <stringProp name="ThreadGroup.delay"></stringProp>
    <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
        <boolProp name="LoopController.continue_forever">false</boolProp>
        <stringProp name="LoopController.loops">1</stringProp>
    </elementProp>
</PostThreadGroup>
```

### 参数说明详解

**Number of Threads (users)**
- 虚拟用户数量，每个线程独立运行测试计划
- 建议值：根据实际业务并发需求设置

**Ramp-Up Period (seconds)**
- 所有线程启动完成所需时间
- 计算方式：Ramp-Up Period ÷ Number of Threads = 每个线程启动间隔
- 例如：10个线程，Ramp-Up为5秒，则每0.5秒启动一个线程

**Loop Count**
- 每个线程执行测试计划的次数
- 勾选"循环 forever"则持续执行，直到手动停止或达到调度器设置的持续时间

**Scheduler**
- 启用后可精确控制测试持续时间
- 常用于长时间稳定性测试

**Same user on next iteration**
- 控制下次迭代是否使用相同的用户会话
- 影响Cookie管理、会话保持等行为

## 注意
- `setup Thread Group（前置线程组）`和 `tearDown Thread Group（后置线程组）` 组件不支持参数 `ThreadGroup.delayedStart`

