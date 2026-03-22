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
import { useForm } from 'vue-use-form-helpers' // 示例

interface FormData {
  email: string
  password: string
}

const formData = ref<FormData>({
  email: '',
  password: ''
})

const emit = defineEmits<{
  submit: [data: FormData]
}>()

const handleSubmit = () => {
  emit('submit', formData.value)
}
</script>

<template>
  <form class="form" @submit.prevent="handleSubmit">
    <slot :data="formData" />
  </form>
</template>
```

## 注意事项

- 组件名避免单字命名（如 `Button` → `UiButton`）
- Props 尽量提供默认值
- 复杂逻辑抽取为 composable
- 样式优先使用 UnoCSS/Tailwind 原子类
