# Source Map 还原指南

生产环境的前端代码经过压缩和混淆，错误堆栈中的文件名和行号无法直接对应源码。Source Map 文件（`.map`）记录了压缩代码到源码的映射关系。

---

## 一、Source Map 工作原理

```
编译前：src/components/UserList.vue:25
                    ↓  构建工具生成 .map 文件
编译后：dist/assets/UserList.abc123.js:1:23456
                    ↑  运行时堆栈指向此处
```

Source Map 文件结构：
```json
{
  "version": 3,
  "file": "UserList.abc123.js",
  "sourceRoot": "",
  "sources": ["../../src/components/UserList.vue"],
  "sourcesContent": ["<template>...</template>..."],
  "names": ["renderList", "items", "user"],
  "mappings": "AAAA;AACA;..."
}
```

---

## 二、还原方法

### 2.1 使用 Node.js source-map 库

```javascript
const { SourceMapConsumer } = require('source-map');
const fs = require('fs');

async function resolvePosition(sourceMapPath, line, column) {
  const rawSourceMap = JSON.parse(fs.readFileSync(sourceMapPath, 'utf8'));
  const consumer = await new SourceMapConsumer(rawSourceMap);

  const pos = consumer.originalPositionFor({
    line: line,
    column: column
  });

  console.log(`压缩位置 ${line}:${column} → 源码 ${pos.source}:${pos.line}:${pos.column}`);
  console.log(`函数名: ${pos.name || '(匿名)'}`);

  consumer.destroy();
  return pos;
}

// 示例：还原 main.abc123.js 第 1 行第 23456 列
resolvePosition('./dist/assets/main.abc123.js.map', 1, 23456);
```

### 2.2 使用 Python 脚本（本 skill 附带）

```bash
python scripts/resolve_stacktrace.py \
  --sourcemap-dir ./dist \
  --stacktrace '{"frames":[{"filename":"main.abc123.js","lineno":1,"colno":23456}]}'
```

### 2.3 在线工具

- [Sentry Source Map 工具](https://sentry.io/resources/source-maps/)
- [Source Map Visualizer](https://sokra.github.io/source-map-visualization/)
- Chrome DevTools → Sources → 右键 → Add source map

---

## 三、完整堆栈还原流程

### 3.1 从 GlitchTip Event 提取堆栈

```bash
# 获取 Event 数据
EVENT=$(curl -s -H "Authorization: Bearer ${GLITCHTIP_TOKEN}" \
  "${GLITCHTIP_URL}/api/0/issues/${ISSUE_ID}/events/latest/")

# 提取堆栈帧
FRAMES=$(echo $EVENT | jq '.entries[] | select(.type=="exception") | .data.values[0].stacktrace.frames')
```

### 3.2 还原每个堆栈帧

```bash
# 对每个帧执行还原
echo $FRAMES | jq -c '.[]' | while read frame; do
  FILENAME=$(echo $frame | jq -r '.filename')
  LINENO=$(echo $frame | jq -r '.lineno')
  COLNO=$(echo $frame | jq -r '.colno')

  # 找到对应的 .map 文件
  MAP_FILE=$(find ./dist -name "$(basename $FILENAME .js).*.map" | head -1)

  if [ -n "$MAP_FILE" ]; then
    python scripts/resolve_stacktrace.py \
      --sourcemap "$MAP_FILE" \
      --line "$LINENO" \
      --column "$COLNO"
  fi
done
```

### 3.3 生成还原后的堆栈

还原前：
```
Error: Cannot read properties of undefined
  at n (main.abc123.js:1:23456)
  at o (main.abc123.js:1:12345)
  at t (vendor.def456.js:2:67890)
```

还原后：
```
Error: Cannot read properties of undefined
  at renderUserList (src/components/UserList.vue:25:18)
  at processOrder (src/utils/orderProcessor.ts:142:12)
  at dispatch (node_modules/vuex/dist/vuex.esm.js:345:8)
```

---

## 四、Source Map 部署注意事项

### 4.1 GlitchTip 自动还原

如果将 Source Map 上传到 GlitchTip，它会自动还原堆栈：

```bash
# 使用 sentry-cli 上传 Source Map
npx @sentry/cli sourcemaps upload \
  --org my-team \
  --project web-app \
  --release v2.3.1 \
  --url-prefix "~/assets/" \
  ./dist/assets
```

### 4.2 构建配置

**Vite：**
```javascript
// vite.config.ts
export default defineConfig({
  build: {
    sourcemap: 'hidden',  // 生成 .map 文件但不引用
  }
})
```

**Webpack：**
```javascript
module.exports = {
  devtool: 'hidden-source-map',  // 生成 .map 但不加注释
}
```

**Nuxt：**
```javascript
// nuxt.config.ts
export default defineNuxtConfig({
  vite: {
    build: {
      sourcemap: 'hidden',
    }
  }
})
```

### 4.3 安全注意事项

| 策略 | 说明 | 推荐度 |
|------|------|--------|
| `hidden` | 生成 .map 但 JS 中无注释，不上传到 CDN | ⭐⭐⭐⭐⭐ |
| 上传到 GlitchTip | 服务端还原，不暴露源码 | ⭐⭐⭐⭐⭐ |
| `.map` 随部署发布 | 任何人都可下载源码 | ❌ |
| `.map` 放内网服务器 | 需要时手动下载 | ⭐⭐⭐ |

---

## 五、常见问题

### Q: 还原后行号仍然不精确？

**原因**：Source Map 版本与实际部署版本不一致。

**解决**：
1. 确认 Event 的 `release` tag 与 Source Map 上传的 `--release` 一致
2. 确认 `--url-prefix` 与实际资源 URL 匹配
3. 每次部署都上传新的 Source Map

### Q: 找不到对应的 .map 文件？

**排查步骤**：
1. 检查构建是否生成了 `.map` 文件
2. 检查构建产物是否被 CI 清理
3. 建议将 `.map` 文件归档到制品库（如 S3）

### Q: Vue SFC 还原后指向 `<template>` 而非 `<script>`？

**原因**：Vue SFC 的 Source Map 映射到整个 `.vue` 文件，行号跨越 template + script + style。

**解决**：根据行号区间推断属于哪个区块：
- 1~N 行：template 区域
- N+1~M 行：script 区域
- M+1~末尾：style 区域

---

## 六、脚本使用详情

参见 `scripts/resolve_stacktrace.py`，支持：

```bash
# 单帧还原
python scripts/resolve_stacktrace.py \
  --sourcemap ./dist/assets/main.abc123.js.map \
  --line 1 \
  --column 23456

# 批量还原（从 GlitchTip 导出的 JSON）
python scripts/resolve_stacktrace.py \
  --sourcemap-dir ./dist/assets \
  --stacktrace-file ./events/latest.json

# 只输出关键帧（inApp=true）
python scripts/resolve_stacktrace.py \
  --sourcemap-dir ./dist/assets \
  --stacktrace-file ./events/latest.json \
  --app-only
```
