---
name: vue-component
description: |
  Vue 3 组件生成器，根据描述快速生成符合最佳实践的 Vue 组件代码。
  当用户提到以下场景时触发：
  - "创建一个 XX 组件"、"生成一个 XX 组件"
  - "帮我写一个 Vue 组件"
  - "新建 XX 组件"
  - 组件名通常以 PascalCase 命名，如 UserList、LoginForm
---

# Vue Component Generator

生成符合 Vue 3 最佳实践的组件代码。

## 何时使用此 Skill

- 用户需要创建新的 Vue 组件
- 需要快速生成组件骨架代码
- 需要符合团队规范的组件模板

## 组件模板

### 基础组件（无状态）

```vue
<script setup lang="ts">
interface Props {
  // 定义 props
}

defineProps<Props>()
</script>

<template>
  <div class="component-name">
    <!-- 组件内容 -->
  </div>
</template>

<style scoped>
.component-name {
  /* 样式 */
}
</style>
```

### 带交互的组件

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  modelValue?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const internalValue = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})
</script>

<template>
  <div class="component-name">
    <!-- 组件内容 -->
  </div>
</template>

<style scoped>
.component-name {
  /* 样式 */
}
</style>
```

## 命名规范

| 类型 | 命名规则 | 示例 |
|-----|---------|------|
| 组件文件 | PascalCase | `UserList.vue` |
| 组件目录 | kebab-case | `user-list/` |
| CSS 类名 | kebab-case | `.user-list` |

## 最佳实践

1. **使用 `<script setup>`**：更简洁的语法
2. **TypeScript 类型**：用 `interface` 定义 Props
3. **scoped 样式**：避免样式污染
4. **defineModel**：Vue 3.4+ 推荐用于双向绑定

```vue
<script setup lang="ts">
// Vue 3.4+ 双向绑定简化写法
const model = defineModel<string>()
</script>
```

## 常见组件模式

### 列表组件

```vue
<script setup lang="ts">
interface Item {
  id: string | number
  [key: string]: any
}

interface Props {
  items: Item[]
  loading?: boolean
}

defineProps<Props>()
</script>

<template>
  <div class="list">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="items.length === 0" class="empty">暂无数据</div>
    <div v-else class="list-items">
      <slot name="item" v-for="item in items" :key="item.id" :item="item">
        <!-- 默认渲染 -->
        <div class="list-item">{{ item }}</div>
      </slot>
    </div>
  </div>
</template>
```

### 表单组件

```vue
<script setup lang="ts">
import { reactive } from 'vue'

interface FormData {
  email: string
  password: string
}

const formData = reactive<FormData>({
  email: '',
  password: ''
})

const emit = defineEmits<{
  submit: [data: FormData]
}>()

const handleSubmit = () => {
  emit('submit', formData)
}
</script>

<template>
  <form class="form" @submit.prevent="handleSubmit">
    <slot :data="formData" />
  </form>
</template>
```

### 卡片组件

```vue
<script setup lang="ts">
interface Props {
  title: string
  image?: string
  description?: string
}

defineProps<Props>()

const emit = defineEmits<{
  click: []
}>()
</script>

<template>
  <div class="card" @click="emit('click')">
    <img v-if="image" :src="image" class="card__image" />
    <div class="card__content">
      <h3 class="card__title">{{ title }}</h3>
      <p v-if="description" class="card__desc">{{ description }}</p>
      <slot />
    </div>
  </div>
</template>

<style scoped>
.card {
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
  cursor: pointer;
}
.card__image {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
}
.card__content {
  padding: 16px;
}
.card__title {
  margin: 0 0 8px;
  font-size: 16px;
}
.card__desc {
  margin: 0;
  color: #666;
  font-size: 14px;
}
</style>
```

### 模态框/弹窗组件

```vue
<script setup lang="ts">
import { watch } from 'vue'

interface Props {
  visible: boolean
  title?: string
  closable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  closable: true,
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
  close: []
}>()

const close = () => {
  emit('update:visible', false)
  emit('close')
}

// 锁定滚动
watch(
  () => props.visible,
  (val) => {
    document.body.style.overflow = val ? 'hidden' : ''
  }
)
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-overlay" @click.self="close">
        <div class="modal">
          <header v-if="title || closable" class="modal__header">
            <h3 class="modal__title">{{ title }}</h3>
            <button v-if="closable" class="modal__close" @click="close">×</button>
          </header>
          <div class="modal__body">
            <slot />
          </div>
          <footer v-if="$slots.footer" class="modal__footer">
            <slot name="footer" />
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal {
  background: #fff;
  border-radius: 8px;
  max-width: 480px;
  width: 90%;
  max-height: 80vh;
  overflow: auto;
}
.modal__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
}
.modal__title {
  margin: 0;
  font-size: 16px;
}
.modal__close {
  border: none;
  background: none;
  font-size: 20px;
  cursor: pointer;
}
.modal__body {
  padding: 16px;
}
.modal__footer {
  padding: 16px;
  border-top: 1px solid #eee;
}
/* 动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
```

### 递归组件（树形结构）

```vue
<script setup lang="ts">
import { computed } from 'vue'

interface TreeNode {
  id: string | number
  label: string
  children?: TreeNode[]
  expanded?: boolean
}

interface Props {
  nodes: TreeNode[]
  level?: number
}

const props = withDefaults(defineProps<Props>(), {
  level: 0,
})

const emit = defineEmits<{
  select: [node: TreeNode]
  toggle: [node: TreeNode]
}>()

const indent = computed(() => props.level * 16 + 'px')

const handleToggle = (node: TreeNode) => {
  node.expanded = !node.expanded
  emit('toggle', node)
}

const handleSelect = (node: TreeNode) => {
  emit('select', node)
}
</script>

<template>
  <ul class="tree">
    <li v-for="node in nodes" :key="node.id" class="tree-node">
      <div
        class="tree-node__content"
        :style="{ paddingLeft: indent }"
        @click="handleSelect(node)"
      >
        <span
          v-if="node.children?.length"
          class="tree-node__toggle"
          @click.stop="handleToggle(node)"
        >
          {{ node.expanded ? '▼' : '▶' }}
        </span>
        <span class="tree-node__label">{{ node.label }}</span>
      </div>
      <!-- 递归渲染子节点 -->
      <Tree
        v-if="node.children?.length && node.expanded"
        :nodes="node.children"
        :level="level + 1"
        @select="(n) => emit('select', n)"
        @toggle="(n) => emit('toggle', n)"
      />
    </li>
  </ul>
</template>

<style scoped>
.tree {
  list-style: none;
  padding: 0;
  margin: 0;
}
.tree-node__content {
  display: flex;
  align-items: center;
  padding: 8px;
  cursor: pointer;
}
.tree-node__content:hover {
  background: #f5f5f5;
}
.tree-node__toggle {
  width: 16px;
  font-size: 10px;
  color: #999;
}
</style>
```

### 异步组件

```vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

// 异步加载重型组件
const HeavyChart = defineAsyncComponent(() =>
  import('./HeavyChart.vue')
)
</script>

<template>
  <Suspense>
    <template #default>
      <HeavyChart />
    </template>
    <template #fallback>
      <div class="loading">加载中...</div>
    </template>
  </Suspense>
</template>
```

或使用懒加载 + 加载状态：

```vue
<script setup lang="ts">
import { ref, onMounted, defineAsyncComponent } from 'vue'

const AsyncComponent = defineAsyncComponent({
  loader: () => import('./HeavyComponent.vue'),
  loadingComponent: () => import('./LoadingSpinner.vue'),
  delay: 200,
  timeout: 10000,
})
</script>

<template>
  <AsyncComponent />
</template>
```

## Slots 与 Attributes 最佳实践

### 透传属性 (v-bind="$attrs")

```vue
<script setup lang="ts">
// 禁止自动继承，手动控制透传
defineOptions({
  inheritAttrs: false,
})

const attrs = useAttrs()
</script>

<template>
  <div class="input-wrapper">
    <input v-bind="attrs" class="custom-input" />
  </div>
</template>
```

### 插槽使用

```vue
<script setup lang="ts">
const slots = useSlots()

// 判断插槽是否存在
const hasHeader = computed(() => !!slots.header)
</script>

<template>
  <div class="card">
    <header v-if="hasHeader" class="card__header">
      <slot name="header" />
    </header>
    <div class="card__body">
      <slot>
        <!-- 默认插槽内容 -->
        <p>暂无内容</p>
      </slot>
    </div>
    <footer v-if="$slots.footer" class="card__footer">
      <slot name="footer" :data="{ /* 作用域数据 */ }" />
    </footer>
  </div>
</template>
```

### 作用域插槽

```vue
<!-- 父组件使用 -->
<ListComponent :items="items">
  <template #default="{ item, index }">
    <span>{{ index + 1 }}. {{ item.name }}</span>
  </template>
</ListComponent>

<!-- 子组件定义 -->
<template>
  <div v-for="(item, index) in items" :key="item.id">
    <slot :item="item" :index="index" />
  </div>
</template>
```

## 组件文档规范

### 使用 JSDoc 注释

```vue
<script setup lang="ts">
/**
 * 用户卡片组件
 * @description 展示用户头像和基本信息，支持点击事件
 * @example
 * <UserCard
 *   :user="currentUser"
 *   :avatar-size="64"
 *   @click="handleUserClick"
 * />
 */

interface User {
  id: string
  name: string
  avatar?: string
  email?: string
}

interface Props {
  /** 用户信息对象 */
  user: User
  /** 头像尺寸（像素） */
  avatarSize?: number
  /** 是否显示邮箱 */
  showEmail?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  avatarSize: 48,
  showEmail: false,
})

const emit = defineEmits<{
  /** 点击用户卡片时触发 */
  click: [user: User]
}>()
</script>
```

### defineOptions 配置

```vue
<script setup lang="ts">
defineOptions({
  name: 'UserCard',           // 组件名
  inheritAttrs: false,        // 控制 attrs 透传
  // Vue 3.3+ 支持
})
</script>
```

## 注意事项

- 组件名避免单字命名（如 `Button` → `UiButton`）
- Props 尽量提供默认值
- 复杂逻辑抽取为 composable
- 样式优先使用 UnoCSS/Tailwind 原子类
- 大型组件使用 `defineAsyncComponent` 懒加载
- 递归组件确保有终止条件
