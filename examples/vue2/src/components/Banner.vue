<template>
  <div class="banner">
    <div class="banner__container" ref="containerRef">
      <div
        class="banner__track"
        :style="trackStyle"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
      >
        <div
          v-for="(item, index) in sectionData"
          :key="item.id || index"
          class="banner__slide"
          @click="handleClick(item)"
        >
          <img :src="item.imageUrl" :alt="item.title || ''" loading="lazy" />
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
export default {
  name: 'Banner',
  props: {
    title: {
      type: String,
      default: '',
    },
    sectionData: {
      type: Array,
      default: () => [],
    },
    autoplay: {
      type: Number,
      default: 3000,
    },
    showIndicators: {
      type: Boolean,
      default: true,
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
    startAutoplay() {
      if (this.autoplay > 0 && this.sectionData.length > 1) {
        this.autoplayTimer = setInterval(() => {
          this.next()
        }, this.autoplay)
      }
    },
    stopAutoplay() {
      if (this.autoplayTimer) {
        clearInterval(this.autoplayTimer)
        this.autoplayTimer = null
      }
    },
    next() {
      this.currentIndex = (this.currentIndex + 1) % this.sectionData.length
    },
    prev() {
      this.currentIndex =
        this.currentIndex === 0
          ? this.sectionData.length - 1
          : this.currentIndex - 1
    },
    goTo(index) {
      this.currentIndex = index
    },
    handleTouchStart(e) {
      this.touchStartX = e.touches[0].clientX
      this.stopAutoplay()
    },
    handleTouchMove(e) {
      this.touchEndX = e.touches[0].clientX
    },
    handleTouchEnd() {
      const diff = this.touchStartX - this.touchEndX
      if (Math.abs(diff) > 50) {
        if (diff > 0) {
          this.next()
        } else {
          this.prev()
        }
      }
      this.startAutoplay()
    },
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
