# Vue 动态页面渲染方案

基于接口配置动态渲染组件的页面开发指南。

## 方案概述

### 核心架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   接口配置数据   │ -> │  Section 映射表   │ -> │  动态组件渲染    │
│  (API Response) │    │  (Type→Component) │    │  <component :is>│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 技术要点

1. **Vue 动态组件**：使用 `<component :is="xxx">` 实现动态渲染
2. **接口驱动**：页面结构由后端接口配置决定
3. **组件映射**：sectionType 与组件一一对应
4. **统一接口**：所有区块组件接收相同的 Props 接口

## 实现示例

### 容器页面

参考项目：`/src/pages/home/index_v3.vue`

```vue
<template>
  <div class="page">
    <component
      :is="getComponent(item.sectionType)"
      v-for="(item, index) in homeDatas"
      :key="'home-components' + index"
      :title="item.sectionName"
      :section-data="item.sectionDetailVoList"
      :enable-com-setting="item.enableComSetting"
      :section-id="item.sectionId"
      @toItem="toItem"
      @addToCart="addToCart"
    />
  </div>
</template>

<script>
// 组件懒加载导入
const QuickEntry = () => import('component/home/QuickEntry.vue')
const Message = () => import('component/home/Message.vue')
const CommunityActivity = () => import('component/home/CommunityActivity.vue')
const Services = () => import('component/home/Services.vue')
const LifeServices = () => import('component/home/LifeServices.vue')
const DecorationService = () => import('component/home/DecorationService.vue')
const Health = () => import('component/home/Health.vue')
const HomeService = () => import('component/home/HomeService.vue')
const Shop = () => import('component/home/Shop.vue')
const Bill = () => import('component/home/Bill.vue')
const Graphic = () => import('component/home/Graphic.vue')
const CommonEntry = () => import('component/home/CommonEntry')

export default {
  components: {
    QuickEntry, Message, CommunityActivity, Services,
    LifeServices, DecorationService, Health, HomeService,
    Shop, Bill, Graphic, CommonEntry
  },
  methods: {
    getComponent(sectionType) {
      const components = [
        'QuickEntry',      // 1
        'Message',         // 2
        'CommunityActivity', // 3
        'CommunityHot',    // 4
        'Services',        // 5
        'LifeServices',    // 6
        'DecorationService', // 7
        'Shop',            // 8
        'Health',          // 9
        'HomeService',     // 10
        'Bill',            // 11
        'Graphic',         // 12
        'CommonEntry'      // 13
      ]
      if (sectionType >= 1 && sectionType <= components.length && sectionType !== 4) {
        return components[sectionType - 1]
      }
      return ''
    }
  }
}
</script>
```

### 区块组件示例

```vue
<!-- QuickEntry.vue - 快捷入口组件 -->
<template>
  <div class="quick-entry">
    <div class="quick-entry__content scrollX">
      <div
        v-for="(item, index) in sectionData"
        :key="'quick-entry' + index"
        class="entry-item"
        @click="toItem(item)"
      >
        <img v-lazy="$root.lazyPic(item.iconUrl, 2)" />
        <div>{{ item.sectionDetailName }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuickEntry',
  props: {
    sectionData: {
      type: Array,
      default: () => []
    }
  },
  setup(props, { emit }) {
    const toItem = (item) => {
      emit('toItem', item)
    }
    return { toItem }
  }
}
</script>
```

## Section 类型对照表

| sectionType | 组件名 | 功能说明 | 数据结构 |
|-------------|--------|----------|----------|
| 1 | QuickEntry | 快捷入口 | `{ iconUrl, sectionDetailName, h5URL }` |
| 2 | Message | 消息中心 | `{ title, content, time }` |
| 3 | CommunityActivity | 社区活动 | 活动列表数据 |
| 4 | CommunityHot | 社区热点 | - |
| 5 | Services | 基础服务 | `{ iconUrl, sectionDetailName }` |
| 6 | LifeServices | 生活服务六宫格 | 宫格数据 |
| 7 | DecorationService | 装修服务三宫格 | 宫格数据 |
| 8 | Shop | 商品栏 | `{ image, price, name }` |
| 9 | Health | 健康四宫格 | 宫格数据 |
| 10 | HomeService | 到家服务 | 服务列表 |
| 11 | Bill | 账单组件 | `{ amount, status }` |
| 12 | Graphic | 图文通知 | `{ title, content, image }` |
| 13 | CommonEntry | 通用入口 | 可配置的入口列表 |

## 接口数据格式

### 请求

```ts
// 接口：/homePageSchema/getHomePageSchemaList
interface RequestParams {
  projectId: string
  isNeedCheckCustomerAudit: number
  versionType: number
}
```

### 响应

```ts
interface Response {
  systemSet: number           // 是否系统设置
  homePageSchemaList: Section[]
}

interface Section {
  sectionType: number           // 区块类型
  sectionId: string             // 区块ID
  sectionName: string           // 区块名称
  enableComSetting: number      // 是否可配置
  sectionDetailVoList: any[]    // 区块详情数据
}
```

## 最佳实践

### 1. 统一 Props 接口

```ts
interface SectionProps {
  title?: string              // 区块标题
  sectionData: any[]          // 区块数据
  sectionId?: string          // 区块ID
  enableComSetting?: number   // 是否可配置
}
```

### 2. 组件懒加载

```ts
// 推荐：按需加载，减少首屏体积
const QuickEntry = () => import('component/home/QuickEntry.vue')
```

### 3. 事件处理统一

```ts
const toItem = ({ sectionDetailType, h5URL, targetID }) => {
  switch (sectionDetailType) {
    case 1: // 第三方链接
      location.href = h5URL
      break
    case 2: // 活动
      router.push(`/activity/${targetID}`)
      break
    case 4: // 商品详情
      router.push(`/product/${targetID}`)
      break
    // ...
  }
}
```

### 4. 骨架屏

```vue
<template>
  <div v-if="loading">
    <SkeletonTop />
    <SkeletonBanner />
  </div>
  <component v-else ... />
</template>
```

## 扩展新组件

### 步骤

1. 创建组件文件 `src/components/home/NewSection.vue`
2. 在容器页面导入组件
3. 在 `getComponent` 方法中添加映射
4. 后端配置新增 sectionType

```js
// 1. 导入
const NewSection = () => import('component/home/NewSection.vue')

// 2. 注册
components: { ..., NewSection }

// 3. 映射
getComponent(sectionType) {
  const components = [..., 'NewSection']  // 新增
}
```

## Skill 使用说明

当需要创建动态配置页面时，使用 `vue-dynamic-page` skill：

```
/vue-dynamic-page
```

或描述需求：

```
帮我创建一个根据接口配置动态渲染的首页
生成一个包含快捷入口、轮播图、商品列表的动态页面
```

---

> 该文档基于 `/Users/saqqdy/www/wojiayun/wj/webapp/static/vue_wj` 项目分析生成
