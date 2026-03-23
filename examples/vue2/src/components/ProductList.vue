<template>
  <div class="product-list">
    <div class="product-list__header" v-if="title">
      <span class="title">{{ title }}</span>
      <a v-if="config && config.moreUrl" class="more" :href="config.moreUrl">
        更多 &gt;
      </a>
    </div>

    <div class="product-list__grid" :style="gridStyle">
      <div
        v-for="(item, index) in sectionData"
        :key="item.id || index"
        class="product-card"
        @click="handleClick(item)"
      >
        <div class="product-card__image">
          <img :src="item.image" :alt="item.name" loading="lazy" />
          <div v-if="item.tags && item.tags.length" class="product-card__tags">
            <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>

        <div class="product-card__info">
          <h4 class="product-card__name">{{ item.name }}</h4>
          <div class="product-card__price">
            <span class="price-current">
              <small>¥</small>{{ item.price }}
            </span>
            <span v-if="item.originalPrice" class="price-original">
              ¥{{ item.originalPrice }}
            </span>
          </div>
          <div v-if="item.sales" class="product-card__sales">
            已售 {{ formatSales(item.sales) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProductList',
  props: {
    title: {
      type: String,
      default: '',
    },
    sectionData: {
      type: Array,
      default: () => [],
    },
    columns: {
      type: Number,
      default: 2,
    },
    config: {
      type: Object,
      default: () => ({}),
    },
  },
  computed: {
    gridStyle() {
      return {
        gridTemplateColumns: `repeat(${this.columns}, 1fr)`,
      }
    },
  },
  methods: {
    formatSales(sales) {
      if (sales >= 10000) {
        return (sales / 10000).toFixed(1) + '万'
      }
      return String(sales)
    },
    handleClick(item) {
      this.$emit('action', item)
    },
  },
}
</script>

<style scoped>
.product-list {
  background: #fff;
  padding: 16px;
  margin-bottom: 12px;
}

.product-list__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.more {
  font-size: 12px;
  color: #999;
  text-decoration: none;
}

.product-list__grid {
  display: grid;
  gap: 10px;
}

.product-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:active {
  transform: scale(0.98);
}

.product-card__image {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
}

.product-card__image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-card__tags {
  position: absolute;
  top: 4px;
  left: 4px;
  display: flex;
  gap: 4px;
}

.tag {
  padding: 2px 4px;
  font-size: 10px;
  color: #fff;
  background: linear-gradient(135deg, #ff6b6b, #ff4757);
  border-radius: 2px;
}

.product-card__info {
  padding: 8px;
}

.product-card__name {
  font-size: 13px;
  font-weight: 400;
  color: #333;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0 0 6px;
}

.product-card__price {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.price-current {
  font-size: 16px;
  font-weight: 600;
  color: #ff4d4f;
}

.price-current small {
  font-size: 12px;
}

.price-original {
  font-size: 11px;
  color: #999;
  text-decoration: line-through;
}

.product-card__sales {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
}
</style>
