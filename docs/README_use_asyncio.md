# asyncio 使用经验总结

基于实际项目开发经验整理的 asyncio 使用指南。

## 目录
- [事件循环基础](#事件循环基础)
- [获取事件循环](#获取事件循环)
- [线程与事件循环](#线程与事件循环)
- [常见错误与解决](#常见错误与解决)
- [最佳实践](#最佳实践)

---

## 事件循环基础

### 什么是事件循环

事件循环是 Python 异步编程的核心，负责：
- **任务调度**：管理和调度所有协程的执行
- **I/O 多路复用**：监听多个 I/O 事件，完成后自动唤醒对应协程
- **并发执行**：通过在等待时切换任务实现单线程并发

### 事件循环的状态

```python
import asyncio

loop = asyncio.new_event_loop()
print(f"初始状态: {loop.is_running()}")  # False
print(f"是否关闭: {loop.is_closed()}")    # True
```

**何时 `is_running=True`：**
- 调用 `loop.run_until_complete()` 期间
- 调用 `loop.run_forever()` 期间
- `asyncio.run()` 执行期间
- 任何协程函数执行期间

---

## 获取事件循环

### 两种核心方法对比

| 方法 | 用途 | 线程安全 | 获取条件 |
|------|------|---------|---------|
| `asyncio.get_running_loop()` | 获取正在运行的循环 | 是 | 必须在运行的循环中调用 |
| `asyncio.get_event_loop()` | 获取当前循环（不要求运行） | 否 | 主线程自动创建，子线程报错 |

### 使用示例

```python
import asyncio

async def inside_coro():
    # ✅ 在协程内使用 get_running_loop()
    loop = asyncio.get_running_loop()
    print(f"运行中的循环: {loop.is_running()}")  # True

def outside_coro():
    # ✅ 在普通函数中使用 get_event_loop()
    loop = asyncio.get_event_loop()
    print(f"循环: {loop.is_running()}")  # False

# 运行
asyncio.run(inside_coro())
outside_coro()
```

### 检查事件循环是否存在

```python
import asyncio

def check_event_loop():
    """检查当前是否有事件循环"""
    try:
        loop = asyncio.get_running_loop()
        return {"status": "running", "loop": loop}
    except RuntimeError:
        loop = asyncio.get_event_loop()
        return {"status": "stopped", "loop": loop}
```

---

## 线程与事件循环

### 重要原则

❌ **事件循环不是线程安全的**

- 每个线程有自己独立的事件循环
- 不要跨线程共享事件循环
- 不要在子线程中操作主线程的循环

### 正确的跨线程使用

```python
import asyncio
import threading

def worker_in_thread():
    # ✅ 子线程创建自己的循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(asyncio.sleep(1))
    finally:
        loop.close()

def main():
    # 主线程
    asyncio.run(main_task())

    # 启动子线程
    thread = threading.Thread(target=worker_in_thread)
    thread.start()
    thread.join()
```

### 线程间通信

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def main_task():
    """主线程的异步任务"""
    print("异步任务执行")

def blocking_task():
    """子线程的同步任务"""
    print("同步任务执行")

async def run_all():
    loop = asyncio.get_running_loop()

    # 在事件循环中运行线程池任务
    await loop.run_in_executor(None, blocking_task)

    # 并行执行异步任务
    await main_task()

asyncio.run(run_all())
```

### 跨线程安全调用

```python
import asyncio
import threading

def thread_safe_schedule(loop, coro):
    """从其他线程安全地调度协程"""
    asyncio.run_coroutine_threadsafe(coro, loop)

async def main():
    loop = asyncio.get_running_loop()
    # 可以在子线程中调用 thread_safe_schedule(loop, some_coro())
```

---

## 常见错误与解决

### 错误1: "This event loop is already running"

**原因**：在循环运行时再次调用 `run_until_complete()` 或 `run_forever()`

```python
# ❌ 错误示例
import asyncio

async def inner():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.sleep(1))  # 报错！

async def outer():
    await inner()

asyncio.run(outer())
```

**解决方案**：直接使用 `await`

```python
# ✅ 正确做法
async def inner():
    await asyncio.sleep(1)  # 直接 await

async def outer():
    await inner()

asyncio.run(outer())
```

### 错误2: "There is no current event loop in thread"

**原因**：子线程不会自动创建事件循环

```python
# ❌ 错误示例
import asyncio
import threading

def worker():
    loop = asyncio.get_event_loop()  # 报错！

thread = threading.Thread(target=worker)
thread.start()
```

**解决方案**：子线程显式创建循环

```python
# ✅ 正确做法
def worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # 使用 loop...
```

### 错误3: "no running event loop"

**原因**：在非异步上下文中调用 `asyncio.get_running_loop()`

```python
# ❌ 错误示例
import asyncio

loop = asyncio.get_running_loop()  # 报错！
```

**解决方案**：使用 `get_event_loop()` 或在异步上下文中调用

```python
# ✅ 正确做法
async def get_loop():
    return asyncio.get_running_loop()

asyncio.run(get_loop())
```

---

## 最佳实践

### 1. 启动事件循环

```python
# 推荐：使用 asyncio.run() (Python 3.7+)
async def main():
    # 你的异步代码
    await asyncio.gather(task1(), task2())

asyncio.run(main())
```

### 2. 并发执行多个任务

```python
import asyncio

async def task_a():
    await asyncio.sleep(1)
    return "A done"

async def task_b():
    await asyncio.sleep(2)
    return "B done"

async def main():
    # 方式1: gather
    results = await asyncio.gather(task_a(), task_b())

    # 方式2: create_task
    # create_task() 会立即将任务加入事件循环，开始并发执行
    # await 会等待任务完成
    t1 = asyncio.create_task(task_a())  # ← 立刻调度执行
    t2 = asyncio.create_task(task_b())  # ← 立刻调度执行，与 t1 并发
    await t1  # ← 等待 t1 完成（此时 t2 可能已执行完，也可能还在执行）
    await t2  # ← 等待 t2 完成

asyncio.run(main())
```

### 3. 超时控制

```python
import asyncio

async def with_timeout():
    try:
        result = await asyncio.wait_for(some_task(), timeout=5.0)
    except asyncio.TimeoutError:
        print("任务超时")
```

### 4. 优雅关闭

```python
import asyncio

class MyService:
    def __init__(self):
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def _run(self):
        while self._running:
            # 执行任务
            await asyncio.sleep(1)

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
```

### 5. 项目中的实际应用

参考 `nanobot/channels/manager.py`：

```python
class ChannelManager:
    """管理多个频道的启动和停止"""

    async def start_all(self) -> None:
        """启动所有频道"""
        # 创建分发任务
        self._dispatch_task = asyncio.create_task(self._dispatch_outbound())

        # 并发启动所有频道
        tasks = []
        for name, channel in self.channels.items():
            tasks.append(asyncio.create_task(self._start_channel(name, channel)))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def stop_all(self) -> None:
        """停止所有频道"""
        # 取消分发任务
        if self._dispatch_task:
            self._dispatch_task.cancel()
            try:
                await self._dispatch_task
            except asyncio.CancelledError:
                pass

        # 停止所有频道
        for channel in self.channels.values():
            await channel.stop()
```

---

## 参考资料

- [Python asyncio 官方文档](https://docs.python.org/3/library/asyncio.html)
- [Real Python: Async IO in Python](https://realpython.com/async-io-python/)

---

*最后更新: 2026-03-06*
