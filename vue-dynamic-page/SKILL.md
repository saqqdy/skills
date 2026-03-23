---
name: vue-dynamic-page
description: |
  Vue 动态页面生成器，基于接口配置动态渲染组件的页面开发。
  当用户提到以下场景时触发：
  - "创建一个动态页面"、"生成一个配置化页面"
  - "根据接口配置渲染组件"
  - "动态组件页面"、"section 区块页面"
  - "低代码页面"、"可视化配置页面"
---

# Vue Dynamic Page Generator

基于接口配置动态渲染组件的页面开发指南。

## 核心概念

### 架构模式

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   接口配置数据   │ -> │  Section 映射表   │ -> │  动态组件渲染    │
│  (API Response) │    │  (Type→Component) │    │  <component :is>│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 关键术语

| 术语 | 说明 |
|-----|------|
| sectionType | 区块类型标识，用于映射组件 |
| sectionData | 区块数据，传递给组件的 props |
| Section | 页面区块，一个独立的可配置单元 |
| DynamicPage | 动态页面容器，负责渲染所有 Section |

## 快速开始

### 1. 容器页面模板

```vue
<template>
  <div class="dynamic-page">
    <component
      v-for="(section, index) in pageData"
      :is="getComponent(section.sectionType)"
      :key="section.sectionId || index"
      :title="section.sectionName"
      :section-data="section.sectionDetailVoList"
      :section-id="section.sectionId"
      :config="section.config"
      @action="handleAction"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 组件映射表
const componentMap = {
  1: defineAsyncComponent(() => import('./sections/QuickEntry.vue')),
  2: defineAsyncComponent(() => import('./sections/Message.vue')),
  3: defineAsyncComponent(() => import('./sections/Banner.vue')),
  4: defineAsyncComponent(() => import('./sections/CardList.vue')),
  // ... 更多组件
}

const getComponent = (type: number) => componentMap[type] || null

const pageData = ref([])

const fetchPageData = async () => {
  const res = await fetch('/api/page/schema')
  pageData.value = await res.json()
}

onMounted(fetchPageData)

const handleAction = (payload) => {
  // 处理组件事件
  console.log('Action:', payload)
}
</script>
```

### 2. 区块组件模板

```vue
<template>
  <div class="section-wrapper">
    <div v-if="title" class="section-header">
      <h3>{{ title }}</h3>
      <a v-if="moreUrl" :href="moreUrl">更多</a>
    </div>
    <div class="section-content">
      <!-- 根据数据渲染内容 -->
      <slot :data="sectionData">
        <div v-for="item in sectionData" :key="item.id" @click="$emit('action', item)">
          {{ item.name }}
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
interface SectionItem {
  id: string | number
  name: string
  icon?: string
  url?: string
  [key: string]: any
}

interface Props {
  title?: string
  sectionData: SectionItem[]
  sectionId?: string
  moreUrl?: string
}

defineProps<Props>()

defineEmits<{
  action: [item: SectionItem]
}>()
</script>

<style scoped>
.section-wrapper {
  background: #fff;
  margin-bottom: 12px;
  padding: 16px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
</style>
```

## 组件库

### 常用 Section 类型

| sectionType | 组件名 | 说明 | 数据结构 |
|-------------|--------|------|----------|
| 1 | QuickEntry | 快捷入口/宫格导航 | `{ iconUrl, name, url }` |
| 2 | Message | 消息中心/通知 | `{ title, content, time }` |
| 3 | Banner | 轮播图 | `{ imageUrl, url }` |
| 4 | CardList | 卡片列表 | `{ title, desc, image }` |
| 5 | Services | 服务入口 | `{ iconUrl, name, url }` |
| 6 | LifeServices | 生活服务六宫格 | `{ iconUrl, name, url }` |
| 7 | DecorationService | 装修服务三宫格 | `{ iconUrl, name, url }` |
| 8 | Shop | 商品栏 | `{ image, price, name }` |
| 9 | Health | 健康四宫格 | `{ iconUrl, name, url }` |
| 10 | HomeService | 到家服务 | `{ iconUrl, name, url }` |
| 11 | Bill | 账单组件 | `{ amount, status }` |
| 12 | Graphic | 图文通知 | `{ title, content, image }` |
| 13 | CommonEntry | 通用入口（可配置） | `{ iconUrl, name, url }` |

### 完整组件映射示例

```ts
// components/sectionMap.ts
import { defineAsyncComponent } from 'vue'

export const sectionComponentMap = {
  // 快捷入口
  1: defineAsyncComponent(() => import('./sections/QuickEntry.vue')),

  // 消息中心
  2: defineAsyncComponent(() => import('./sections/Message.vue')),

  // 社区活动
  3: defineAsyncComponent(() => import('./sections/CommunityActivity.vue')),

  // 社区热点
  4: defineAsyncComponent(() => import('./sections/CommunityHot.vue')),

  // 基础服务
  5: defineAsyncComponent(() => import('./sections/Services.vue')),

  // 生活服务
  6: defineAsyncComponent(() => import('./sections/LifeServices.vue')),

  // 装修服务
  7: defineAsyncComponent(() => import('./sections/DecorationService.vue')),

  // 商城
  8: defineAsyncComponent(() => import('./sections/Shop.vue')),

  // 健康
  9: defineAsyncComponent(() => import('./sections/Health.vue')),

  // 到家服务
  10: defineAsyncComponent(() => import('./sections/HomeService.vue')),

  // 账单
  11: defineAsyncComponent(() => import('./sections/Bill.vue')),

  // 图文通知
  12: defineAsyncComponent(() => import('./sections/Graphic.vue')),

  // 通用入口
  13: defineAsyncComponent(() => import('./sections/CommonEntry.vue')),
}

export const getSectionComponent = (type: number | string) => {
  return sectionComponentMap[type] || null
}
```

## 接口数据格式

### 请求参数

```ts
interface PageSchemaParams {
  projectId?: string      // 项目ID
  versionType?: number    // 版本类型
  isNeedCheckCustomerAudit?: number
}
```

### 响应数据

```ts
interface PageSchemaResponse {
  systemSet: number       // 是否系统设置
  homePageSchemaList: SectionSchema[]
}

interface SectionSchema {
  sectionType: number           // 区块类型
  sectionId: string             // 区块ID
  sectionName: string           // 区块名称
  enableComSetting: number      // 是否可配置
  sectionDetailVoList: any[]    // 区块详情数据
}
```

## 高级模式

### 1. 组件懒加载

```ts
// 使用 defineAsyncComponent 实现按需加载
const componentMap = {
  1: () => import('./sections/QuickEntry.vue'),
  2: () => import('./sections/Message.vue'),
}

// 或使用 vite 的 glob 导入
const sections = import.meta.glob('./sections/*.vue')

const getComponent = (type: number) => {
  const name = sectionNames[type]
  return defineAsyncComponent(sections[`./sections/${name}.vue`])
}
```

### 2. 动态注册组件

```vue
<script setup>
import { markRaw, onMounted } from 'vue'
import { getSectionComponent } from './sectionMap'

const dynamicComponents = ref({})

// 动态注册用到的组件
const registerComponents = (sections) => {
  const types = new Set(sections.map(s => s.sectionType))
  types.forEach(type => {
    const comp = getSectionComponent(type)
    if (comp && !dynamicComponents.value[type]) {
      dynamicComponents.value[type] = markRaw(comp)
    }
  })
}
</script>
```

### 3. 配置化事件处理

```ts
// 统一的事件处理器
const actionHandlers = {
  1: (item) => location.href = item.h5URL,      // 外部链接
  2: (item) => router.push(`/activity/${item.id}`), // 活动页
  3: (item) => router.push(`/shop/${item.id}`),     // 商品详情
  4: (item) => router.push(`/product/${item.id}`),  // 商品分类
  7: (item) => openWeapp(item.targetAppId),         // 小程序
}

const handleAction = (item) => {
  const handler = actionHandlers[item.sectionDetailType]
  handler?.(item)
}
```

### 4. 骨架屏占位

```vue
<template>
  <div class="dynamic-page">
    <template v-if="loading">
      <Skeleton v-for="i in 3" :key="i" :type="i" />
    </template>
    <template v-else>
      <component
        v-for="section in pageData"
        :is="getComponent(section.sectionType)"
        :key="section.sectionId"
        v-bind="section"
      />
    </template>
  </div>
</template>
```

## 最佳实践

### 1. 统一 Props 接口

所有 Section 组件应接收统一的 props：

```ts
interface SectionProps {
  title?: string              // 区块标题
  sectionData: any[]          // 区块数据
  sectionId?: string          // 区块ID
  enableComSetting?: number   // 是否可配置
  config?: Record<string, any> // 扩展配置
}
```

### 2. 事件命名规范

```ts
// 推荐的事件命名
emit('action', item)      // 通用点击事件
emit('toItem', item)      // 跳转事件
emit('addToCart', item)   // 业务事件
emit('refresh')           // 刷新事件
```

### 3. 样式隔离

```vue
<style scoped>
/* 每个组件使用独立的根类名 */
.section-quick-entry { }
.section-message { }
.section-banner { }
</style>
```

### 4. 错误处理

```vue
<template>
  <component
    :is="getComponent(section.sectionType)"
    v-for="section in validSections"
    :key="section.sectionId"
  />
</template>

<script setup>
const validSections = computed(() =>
  pageData.value.filter(s => getComponent(s.sectionType))
)
</script>
```

## 扩展指南

### 新增 Section 类型

1. 创建组件文件 `src/components/sections/NewSection.vue`
2. 在映射表中注册
3. 后端配置新增 sectionType

```ts
// 新增映射
componentMap[14] = defineAsyncComponent(() => import('./sections/NewSection.vue'))
```

### 组件开发清单

- [ ] 定义 Props 接口
- [ ] 实现基础渲染
- [ ] 添加点击事件
- [ ] 处理加载状态
- [ ] 添加骨架屏
- [ ] 样式适配（响应式）
- [ ] 单元测试
