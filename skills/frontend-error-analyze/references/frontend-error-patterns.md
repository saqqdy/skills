# 前端错误模式库

本文档整理了前端开发中常见的错误模式，包含错误特征、根因分析、修复方案和防御策略。

---

## 一、JS 运行时错误

### 1.1 TypeError: Cannot read properties of undefined

**错误特征**：
```
TypeError: Cannot read properties of undefined (reading 'map')
TypeError: Cannot read properties of undefined (reading 'name')
TypeError: Cannot read property 'length' of undefined
```

**常见触发场景**：

| 场景 | 示例代码 | 说明 |
|------|----------|------|
| 异步数据未到就渲染 | `<div>{user.name}</div>` | 接口返回前 user 为 undefined |
| 解构嵌套对象 | `const { data: { list } } = response` | data 为 null 时解构失败 |
| 数组方法调用 | `items.map(item => ...)` | items 为 undefined |
| 链式属性访问 | `config.theme.primary` | 中间属性缺失 |

**根因分析流程**：
1. 从堆栈位置找到出错表达式
2. 向上追溯变量的赋值来源
3. 确认数据流中哪一步产生了 undefined
4. 检查是否存在异步时序问题

**修复方案**：

```javascript
// 方案一：可选链（推荐）
const name = user?.name
const list = response?.data?.list ?? []

// 方案二：默认值守卫
const UserList = ({ items = [] }) => items.map(item => <li>{item.name}</li>)

// 方案三：条件渲染
{user && <div>{user.name}</div>}

// 方案四：加载态守卫
if (!data) return <Skeleton />
return <Content data={data} />
```

**防御策略**：
- TypeScript strictNullChecks + 接口返回类型定义
- React/Vue 组件 Props 必填校验
- zod / joi 对接口响应做 runtime 校验
- ESLint 规则 `no-unsafe-optional-chaining`

---

### 1.2 TypeError: xxx is not a function

**错误特征**：
```
TypeError: router.push is not a function
TypeError: Object(...)(...) is not a function
TypeError: (0 , _utils.formatDate) is not a function
```

**常见触发场景**：

| 场景 | 说明 |
|------|------|
| 动态导入失败 | `import()` 返回 undefined |
| 包版本不匹配 | 升级后 API 变更 |
| 命名导出入口错误 | `import { foo } from 'bar'` 但 foo 不存在 |
| this 绑定丢失 | 回调函数中 this 不是期望的对象 |
| 运行时类型变化 | 期望函数但收到其他类型 |

**修复方案**：

```javascript
// 动态导入守卫
const module = await import('./module').catch(() => null)
if (module?.default) {
  module.default()
}

// this 绑定修复
class Component {
  // 箭头函数自动绑定 this
  handleClick = () => { this.setState(...) }
}

// 运行时类型校验
if (typeof callback === 'function') {
  callback()
}
```

---

### 1.3 Unhandled Promise Rejection

**错误特征**：
```
UnhandledRejection: Error: Request failed with status code 500
UnhandledRejection: TypeError: Network request failed
```

**常见遗漏位置**：

| 场景 | 遗漏代码 | 修复 |
|------|----------|------|
| fetch 缺少 .catch() | `fetch(url).then(r => r.json())` | 加 `.catch()` |
| async 函数未 try-catch | `async function load() { const res = await fetch() }` | 包裹 try-catch |
| Promise.all 无个体容错 | `Promise.all(requests)` | 改用 `Promise.allSettled` |
| 事件回调中 reject | `new Promise((_, reject) => { el.onerror = reject })` | 添加 `.catch()` |

**修复方案**：

```javascript
// 方案一：async/await + try-catch
async function loadData() {
  try {
    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (error) {
    console.error('加载失败:', error)
    return null
  }
}

// 方案二：Promise.allSettled 容错
const results = await Promise.allSettled(requests)
const succeeded = results.filter(r => r.status === 'fulfilled').map(r => r.value)
const failed = results.filter(r => r.status === 'rejected').map(r => r.reason)

// 方案三：全局兜底
window.addEventListener('unhandledrejection', (event) => {
  console.error('未处理的 Promise 拒绝:', event.reason)
  event.preventDefault()
})
```

---

## 二、网络错误

### 2.1 CORS 跨域错误

**错误特征**：
```
Access to XMLHttpRequest at 'https://api.example.com/data' from origin 'https://app.example.com'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present.
```

**诊断清单**：

| 检查项 | 工具/方法 |
|--------|-----------|
| 响应头是否包含 CORS 头 | 浏览器 DevTools → Network → Response Headers |
| Origin 是否在允许列表中 | 服务端 Access-Control-Allow-Origin 配置 |
| 预检请求是否通过 | 检查 OPTIONS 请求的响应 |
| Credentials 模式冲突 | `withCredentials: true` 时不能用通配符 `*` |
| Nginx/CDN 是否覆盖了 CORS 头 | 检查多层代理的 header 配置 |

**修复方案**：

```nginx
# Nginx 配置示例
location /api/ {
    add_header Access-Control-Allow-Origin $http_origin always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
    add_header Access-Control-Allow-Credentials true always;

    if ($request_method = OPTIONS) {
        return 204;
    }
    proxy_pass http://backend;
}
```

---

### 2.2 ChunkLoadError / 资源加载失败

**错误特征**：
```
ChunkLoadError: Loading chunk 5 failed.
(missing: https://cdn.example.com/assets/chunk-5.abc123.js)
SyntaxError: Unexpected token '<'
```

**根因**：

部署新版本后，用户浏览器缓存了旧 HTML，旧 HTML 引用的 JS/CSS chunk 已被新版本删除。

**修复方案**：

```javascript
// 方案一：路由级错误边界（Vue）
const router = createRouter({...})
router.onError((error) => {
  if (/chunk.*failed/i.test(error.message)) {
    window.location.reload() // 刷新加载最新版本
  }
})

// 方案二：React Error Boundary
class ChunkErrorBoundary extends React.Component {
  componentDidCatch(error) {
    if (/chunk.*failed/i.test(error.message)) {
      window.location.reload()
    }
  }
}

// 方案三：版本检测定时轮询
setInterval(async () => {
  const res = await fetch('/version.json?' + Date.now())
  const { version } = await res.json()
  if (version !== __APP_VERSION__) {
    // 提示用户刷新
  }
}, 60000)
```

**防御策略**：
- CDN 设置 HTML 不缓存，JS/CSS 长缓存 + 内容哈希文件名
- 部署时保留旧版本 chunk 至少 N 小时
- Service Worker 更新策略避免缓存旧 HTML

---

## 三、框架特定错误

### 3.1 Vue 常见错误

| 错误 | 特征 | 原因 | 修复 |
|------|------|------|------|
| `v-if / v-for 优先级` | 编译警告 | 同元素上同时使用 | 用 computed 过滤后再 v-for |
| `Avoid mutating prop` | 运行时警告 | 直接修改 props | emit 事件让父组件修改 |
| `Maximum recursive updates` | 无限循环 | watch/computed 互相触发 | 检查依赖链，加条件守卫 |
| `Invalid watch source` | 运行时报错 | watch 监听非响应式数据 | 确保 ref/reactive 包裹 |
| `Template ref not working` | ref 为 null | 组件挂载时机问题 | 在 onMounted 中访问 |

### 3.2 React 常见错误

| 错误 | 特征 | 原因 | 修复 |
|------|------|------|------|
| Hydration mismatch | SSR/CSR 不一致 | 服务端客户端数据不同 | 使用 `suppressHydrationWarning` 或 `useEffect` 客户端渲染 |
| Invalid hook call | 运行时报错 | 条件/循环中调用 Hook | Hook 只在顶层调用 |
| Max update depth | 无限渲染 | setState 在 render 中调用 | 检查 effect 依赖 |
| Can't perform state update on unmounted | 内存泄漏 | 组件卸载后异步更新 | 用 ref 标记或 AbortController |

---

## 四、内存泄漏模式

### 4.1 常见泄漏源

```javascript
// 泄漏模式一：未清除的定时器
useEffect(() => {
  const timer = setInterval(() => { ... }, 1000)
  // ❌ 缺少 cleanup
}, [])

// 修复
useEffect(() => {
  const timer = setInterval(() => { ... }, 1000)
  return () => clearInterval(timer) // ✅
}, [])

// 泄漏模式二：未移除的事件监听
mounted() {
  window.addEventListener('resize', this.handleResize)
}
beforeUnmount() {
  window.removeEventListener('resize', this.handleResize) // ✅
}

// 泄漏模式三：闭包持有大对象引用
function createHandler() {
  const hugeData = loadHugeData() // 100MB
  return () => {
    console.log(hugeData.length) // 闭包引用 hugeData
  }
}
// 修复：只保留需要的字段
function createHandler() {
  const { count } = loadHugeData()
  return () => console.log(count) // ✅
}
```

### 4.2 内存泄漏诊断方法

1. Chrome DevTools → Memory → Heap Snapshot
2. 对比两次快照，关注 Delta 列
3. 查看 Retainers 链路找到 GC 根
4. 重点关注：Detached DOM nodes、Event listeners、Closure variables

---

## 五、第三方脚本错误

### 5.1 隔离策略

```javascript
// 方案一：try-catch 包裹第三方调用
function trackEvent(event) {
  try {
    analytics.track(event)
  } catch (error) {
    console.warn('分析 SDK 报错:', error.message)
  }
}

// 方案二：全局错误过滤器
Sentry.init({
  beforeSend(event) {
    // 过滤第三方脚本错误
    if (event.exception?.values?.[0]?.stacktrace?.frames?.some(
      f => f.filename?.includes('third-party.com')
    )) {
      return null // 不上报
    }
    return event
  }
})

// 方案三：iframe 沙箱隔离第三方广告
// 广告脚本运行在 iframe 中，不影响主应用
```

---

## 六、错误模式诊断流程

```
收到错误
  │
  ├─ 有堆栈？ ─── 否 ──→ 搜索错误消息关键词
  │                       │
  │ 是                    └─→ 定位出错表达式
  │
  ├─ 堆栈可还原？ ─── 否 ──→ 检查 Source Map 配置
  │                          │
  │ 是                       └─→ 手动在构建产物中查找
  │
  ├─ 有 OpenReplay 关联？ ─── 否 ──→ 按时间窗口搜索会话
  │                              │
  │ 是                            └─→ 还原用户操作路径
  │
  ├─ 可复现？ ─── 否 ──→ 检查环境变量、AB 实验、用户特征
  │                     │
  │ 是                   └─→ 本地复现调试
  │
  └─ 生成修复 → 加入防御策略 → 更新模式库
```
