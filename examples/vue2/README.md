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

## 功能特性

- **动态渲染**：根据接口配置动态渲染组件
- **骨架屏**：加载时显示骨架屏占位
- **手势滑动**：轮播图支持手势滑动
- **响应式**：适配移动端显示

## 扩展新组件

1. 创建组件 `src/components/NewSection.vue`
2. 在 `DynamicHomePage.vue` 中导入并注册
3. 在 `COMPONENT_MAP` 中添加映射
4. 在 `mock.js` 中添加对应的 sectionType 数据
