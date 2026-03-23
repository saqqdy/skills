# Vue Dynamic Page Demo

基于 Vue 2 + Vite 的动态页面演示项目。

## 快速开始

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 项目结构

```
src/
├── main.js                    # Vue 入口
├── App.vue                    # 根组件
├── mock.js                    # Mock 数据
└── components/
    ├── DynamicHomePage.vue    # 动态页面容器
    ├── QuickEntry.vue         # 快捷入口组件
    ├── Banner.vue             # 轮播图组件
    └── ProductList.vue        # 商品列表组件
```

## 组件特性

### DynamicHomePage

动态页面容器，根据配置渲染不同区块。

| Props | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| autoLoad | Boolean | true | 是否自动加载数据 |

| Events | 参数 | 说明 |
|--------|------|------|
| action | item | 区块项点击事件 |
| loaded | data | 数据加载完成 |
| error | error | 数据加载错误 |

| Methods | 说明 |
|---------|------|
| refresh() | 刷新页面数据 |
| getPageData() | 获取当前数据 |
| isLoading() | 获取加载状态 |
| getError() | 获取错误信息 |

### QuickEntry

快捷入口宫格导航组件。

| Props | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| title | String | '' | 区块标题 |
| sectionData | Array | [] | 入口数据 |
| columns | Number | 5 | 每行数量 |

| Slots | 说明 |
|-------|------|
| extra | 标题右侧扩展 |
| item | 自定义入口项（作用域插槽） |

### Banner

轮播图组件，支持自动播放和手势滑动。

| Props | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| sectionData | Array | [] | 轮播数据 |
| autoplay | Number | 3000 | 自动播放间隔 |
| showIndicators | Boolean | true | 显示指示器 |

| Events | 参数 | 说明 |
|--------|------|------|
| action | item | 点击事件 |
| change | index | 切换事件 |

### ProductList

商品列表组件。

| Props | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| title | String | '' | 区块标题 |
| sectionData | Array | [] | 商品数据 |
| columns | Number | 2 | 每行数量 |
| loading | Boolean | false | 加载状态 |
| config | Object | {} | 扩展配置 |

| Slots | 说明 |
|-------|------|
| header-extra | 标题右侧扩展 |
| loading | 加载状态 |
| empty | 空状态 |
| item | 自定义商品卡片 |

## 扩展新组件

1. 创建组件 `src/components/NewSection.vue`
2. 在 `DynamicHomePage.vue` 中导入并注册
3. 在 `COMPONENT_MAP` 中添加映射
4. 在 `mock.js` 中添加对应的 sectionType 数据
