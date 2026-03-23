<template>
  <div class="dynamic-home">
    <!-- 骨架屏 -->
    <template v-if="loading">
      <div class="skeleton skeleton-quick-entry">
        <div class="skeleton-title"></div>
        <div class="skeleton-grid">
          <div v-for="i in 10" :key="i" class="skeleton-item">
            <div class="skeleton-icon"></div>
            <div class="skeleton-text"></div>
          </div>
        </div>
      </div>
      <div class="skeleton skeleton-banner"></div>
      <div class="skeleton skeleton-products">
        <div class="skeleton-title"></div>
        <div class="skeleton-grid">
          <div v-for="i in 4" :key="i" class="skeleton-card">
            <div class="skeleton-image"></div>
            <div class="skeleton-lines">
              <div class="skeleton-line"></div>
              <div class="skeleton-line short"></div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 动态内容 -->
    <template v-else>
      <component
        v-for="(section, index) in validSections"
        :is="getComponent(section.sectionType)"
        :key="section.sectionId || index"
        :title="section.sectionName"
        :section-data="section.sectionDetailVoList"
        :section-id="section.sectionId"
        :enable-com-setting="section.enableComSetting"
        :config="section.config"
        @action="handleAction"
        @add-to-cart="handleAddToCart"
      />
    </template>

    <!-- 错误状态 -->
    <div v-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchPageData">重试</button>
    </div>
  </div>
</template>

<script>
import QuickEntry from './QuickEntry.vue'
import Banner from './Banner.vue'
import ProductList from './ProductList.vue'
import { getMockPageData } from '../mock'

// 组件映射
const COMPONENT_MAP = {
  1: QuickEntry,    // 快捷入口
  2: Banner,        // 轮播图
  3: ProductList,   // 商品列表
}

export default {
  name: 'DynamicHomePage',
  components: {
    QuickEntry,
    Banner,
    ProductList,
  },
  data() {
    return {
      loading: true,
      error: null,
      pageData: [],
    }
  },
  computed: {
    validSections() {
      return this.pageData.filter((section) =>
        COMPONENT_MAP[section.sectionType]
      )
    },
  },
  mounted() {
    this.fetchPageData()
  },
  methods: {
    getComponent(sectionType) {
      return COMPONENT_MAP[sectionType] || null
    },
    async fetchPageData() {
      this.loading = true
      this.error = null

      try {
        // 模拟网络延迟
        await new Promise((resolve) => setTimeout(resolve, 800))
        const response = getMockPageData()
        this.pageData = response.homePageSchemaList
      } catch (e) {
        this.error = '加载失败，请稍后重试'
        console.error('Failed to fetch page schema:', e)
      } finally {
        this.loading = false
      }
    },
    handleAction(item) {
      console.log('Action:', item)
      if (item.url) {
        alert(`跳转到: ${item.url}`)
      }
    },
    handleAddToCart(item) {
      console.log('Add to cart:', item)
      alert(`加入购物车: ${item.name}`)
    },
    refresh() {
      this.fetchPageData()
    },
  },
}
</script>

<style scoped>
.dynamic-home {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 12px;
}

/* 骨架屏样式 */
.skeleton {
  background: #fff;
  margin-bottom: 12px;
  padding: 16px;
  border-radius: 8px;
}

.skeleton-title {
  width: 100px;
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin-bottom: 16px;
  border-radius: 4px;
}

.skeleton-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.skeleton-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: calc(20% - 13px);
}

.skeleton-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 50%;
  margin-bottom: 8px;
}

.skeleton-text {
  width: 40px;
  height: 12px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-banner {
  height: 180px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  padding: 0;
}

.skeleton-card {
  width: calc(50% - 5px);
  border-radius: 8px;
  overflow: hidden;
  background: #f8f8f8;
}

.skeleton-image {
  width: 100%;
  aspect-ratio: 1;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton-lines {
  padding: 8px;
}

.skeleton-line {
  height: 12px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 6px;
}

.skeleton-line.short {
  width: 60%;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

/* 错误状态 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #999;
}

.error-state button {
  margin-top: 12px;
  padding: 8px 24px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
