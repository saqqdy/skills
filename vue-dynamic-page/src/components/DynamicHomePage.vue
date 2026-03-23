<template>
  <div class="dynamic-home">
    <!-- 骨架屏 -->
    <template v-if="loading">
      <slot name="skeleton">
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
      </slot>
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
      <slot name="error" :error="error" :retry="fetchPageData">
        <p>{{ error }}</p>
        <button @click="fetchPageData">重试</button>
      </slot>
    </div>
  </div>
</template>

<script>
import QuickEntry from './QuickEntry.vue'
import Banner from './Banner.vue'
import ProductList from './ProductList.vue'
import { getMockPageData } from '../mock'

/**
 * 组件映射表
 * @type {Object.<number, Object>}
 */
const COMPONENT_MAP = {
  1: QuickEntry,    // 快捷入口
  2: Banner,        // 轮播图
  3: ProductList,   // 商品列表
}

/**
 * 动态首页组件
 * @description 根据接口配置动态渲染页面区块的容器组件
 * @example
 * <DynamicHomePage
 *   ref="pageRef"
 *   :auto-load="true"
 *   @action="handleAction"
 *   @loaded="handleLoaded"
 *   @error="handleError"
 * >
 *   <template #skeleton>
 *     <CustomSkeleton />
 *   </template>
 * </DynamicHomePage>
 */
export default {
  name: 'DynamicHomePage',

  components: {
    QuickEntry,
    Banner,
    ProductList,
  },

  props: {
    /** 是否自动加载数据 */
    autoLoad: {
      type: Boolean,
      default: true,
    },
  },

  data() {
    return {
      loading: true,
      error: null,
      pageData: [],
    }
  },

  computed: {
    /**
     * 过滤有效的区块
     * @returns {Array} 有效区块列表
     */
    validSections() {
      return this.pageData.filter(
        (section) => COMPONENT_MAP[section.sectionType]
      )
    },
  },

  mounted() {
    if (this.autoLoad) {
      this.fetchPageData()
    }
  },

  methods: {
    /**
     * 根据 sectionType 获取组件
     * @param {number} sectionType 区块类型
     * @returns {Object|null} 组件或 null
     */
    getComponent(sectionType) {
      return COMPONENT_MAP[sectionType] || null
    },

    /**
     * 获取页面数据
     */
    async fetchPageData() {
      this.loading = true
      this.error = null

      try {
        // 模拟网络延迟
        await new Promise((resolve) => setTimeout(resolve, 800))
        const response = getMockPageData()
        this.pageData = response.homePageSchemaList
        this.$emit('loaded', this.pageData)
      } catch (e) {
        this.error = '加载失败，请稍后重试'
        this.$emit('error', e)
        console.error('Failed to fetch page schema:', e)
      } finally {
        this.loading = false
      }
    },

    /**
     * 统一事件处理
     * @param {Object} item 区块项数据
     */
    handleAction(item) {
      this.$emit('action', item)

      const actionType = this.getActionType(item)

      // 根据类型分发处理
      switch (actionType) {
        case 'link':
          if (item.url) {
            alert(`跳转到: ${item.url}`)
          }
          break
        case 'product':
          console.log('Navigate to product:', item.id)
          break
        case 'activity':
          console.log('Navigate to activity:', item.id)
          break
        default:
          console.log('Unknown action:', item)
      }
    },

    /**
     * 加入购物车处理
     * @param {Object} item 商品数据
     */
    handleAddToCart(item) {
      this.$emit('add-to-cart', item)
    },

    /**
     * 获取动作类型
     * @param {Object} item 区块项数据
     * @returns {string} 动作类型
     */
    getActionType(item) {
      if (item.url && item.url.startsWith('http')) {
        return 'link'
      }
      if (item.sectionDetailType === 4) {
        return 'product'
      }
      if (item.sectionDetailType === 2) {
        return 'activity'
      }
      return 'link'
    },

    /**
     * 刷新页面数据
     */
    refresh() {
      this.fetchPageData()
    },

    /**
     * 获取当前页面数据
     * @returns {Array} 页面数据
     */
    getPageData() {
      return this.pageData
    },

    /**
     * 获取加载状态
     * @returns {boolean} 是否加载中
     */
    isLoading() {
      return this.loading
    },

    /**
     * 获取错误信息
     * @returns {string|null} 错误信息
     */
    getError() {
      return this.error
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
