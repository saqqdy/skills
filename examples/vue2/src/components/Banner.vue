<template>
  <div class="banner">
    <div class="banner__container" ref="containerRef">
      <div
        class="banner__track"
        :style="trackStyle"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
        @mouseenter="stopAutoplay"
        @mouseleave="startAutoplay"
      >
        <div
          v-for="(item, index) in sectionData"
          :key="item.id || index"
          class="banner__slide"
          @click="handleClick(item)"
        >
          <slot name="slide" :item="item" :index="index">
            <img :src="item.imageUrl" :alt="item.title || ''" loading="lazy" />
          </slot>
        </div>
      </div>
    </div>

    <!-- 指示器 -->
    <div v-if="showIndicators && sectionData.length > 1" class="banner__indicators">
      <span
        v-for="(_, index) in sectionData"
        :key="index"
        class="indicator"
        :class="{ active: currentIndex === index }"
        @click="goTo(index)"
      />
    </div>
  </div>
</template>

<script>
/**
 * 轮播图组件
 * @description 支持自动播放、手势滑动、指示器的轮播图组件
 * @example
 * <Banner
 *   :section-data="bannerList"
 *   :autoplay="3000"
 *   :show-indicators="true"
 *   @action="handleBannerClick"
 * />
 */
export default {
  name: 'Banner',

  props: {
    /** 区块标题 */
    title: {
      type: String,
      default: '',
    },
    /** 轮播图数据列表 */
    sectionData: {
      type: Array,
      default: () => [],
    },
    /** 自动播放间隔（毫秒），0 表示不自动播放 */
    autoplay: {
      type: Number,
      default: 3000,
    },
    /** 是否显示底部指示器 */
    showIndicators: {
      type: Boolean,
      default: true,
    },
    /** 区块 ID */
    sectionId: {
      type: String,
      default: '',
    },
  },

  data() {
    return {
      currentIndex: 0,
      autoplayTimer: null,
      touchStartX: 0,
      touchEndX: 0,
    }
  },

  computed: {
    trackStyle() {
      return {
        transform: `translateX(-${this.currentIndex * 100}%)`,
        transition: 'transform 0.3s ease',
      }
    },
  },

  mounted() {
    this.startAutoplay()
  },

  beforeDestroy() {
    this.stopAutoplay()
  },

  watch: {
    sectionData() {
      this.currentIndex = 0
      this.stopAutoplay()
      this.startAutoplay()
    },
  },

  methods: {
    /**
     * 开始自动播放
     */
    startAutoplay() {
      if (this.autoplay > 0 && this.sectionData.length > 1) {
        this.autoplayTimer = setInterval(() => {
          this.next()
        }, this.autoplay)
      }
    },

    /**
     * 停止自动播放
     */
    stopAutoplay() {
      if (this.autoplayTimer) {
        clearInterval(this.autoplayTimer)
        this.autoplayTimer = null
      }
    },

    /**
     * 下一张
     */
    next() {
      const newIndex = (this.currentIndex + 1) % this.sectionData.length
      this.currentIndex = newIndex
      this.$emit('change', newIndex)
    },

    /**
     * 上一张
     */
    prev() {
      const newIndex =
        this.currentIndex === 0
          ? this.sectionData.length - 1
          : this.currentIndex - 1
      this.currentIndex = newIndex
      this.$emit('change', newIndex)
    },

    /**
     * 跳转到指定索引
     * @param {number} index 目标索引
     */
    goTo(index) {
      this.currentIndex = index
      this.$emit('change', index)
    },

    /**
     * 触摸开始
     * @param {TouchEvent} e 触摸事件
     */
    handleTouchStart(e) {
      this.touchStartX = e.touches[0].clientX
      this.stopAutoplay()
    },

    /**
     * 触摸移动
     * @param {TouchEvent} e 触摸事件
     */
    handleTouchMove(e) {
      this.touchEndX = e.touches[0].clientX
    },

    /**
     * 触摸结束
     */
    handleTouchEnd() {
      const diff = this.touchStartX - this.touchEndX
      const threshold = 50

      if (Math.abs(diff) > threshold) {
        if (diff > 0) {
          this.next()
        } else {
          this.prev()
        }
      }
      this.startAutoplay()
    },

    /**
     * 处理点击事件
     * @param {Object} item 轮播项数据
     */
    handleClick(item) {
      this.$emit('action', item)
    },
  },
}
</script>

<style scoped>
.banner {
  position: relative;
  width: 100%;
  margin-bottom: 12px;
}

.banner__container {
  width: 100%;
  overflow: hidden;
  border-radius: 8px;
}

.banner__track {
  display: flex;
  width: 100%;
}

.banner__slide {
  flex: 0 0 100%;
  width: 100%;
  cursor: pointer;
}

.banner__slide img {
  width: 100%;
  height: auto;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  display: block;
}

.banner__indicators {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 6px;
}

.indicator {
  width: 6px;
  height: 6px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s;
}

.indicator.active {
  width: 16px;
  background: #fff;
}
</style>
