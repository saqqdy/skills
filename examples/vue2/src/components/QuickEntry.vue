<template>
  <div class="quick-entry">
    <div class="quick-entry__title" v-if="title">
      <span class="title-text">{{ title }}</span>
    </div>
    <div class="quick-entry__grid" :style="gridStyle">
      <div
        v-for="(item, index) in sectionData"
        :key="item.id || index"
        class="entry-item"
        @click="handleClick(item)"
      >
        <div class="entry-item__icon">
          <img :src="item.iconUrl" :alt="item.name" loading="lazy" />
          <span v-if="item.badge" class="entry-item__badge">{{ item.badge }}</span>
        </div>
        <span class="entry-item__name">{{ item.name }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuickEntry',
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
      default: 5,
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
    handleClick(item) {
      this.$emit('action', item)
    },
  },
}
</script>

<style scoped>
.quick-entry {
  background: #fff;
  padding: 16px;
  margin-bottom: 12px;
}

.quick-entry__title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.title-text {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.quick-entry__grid {
  display: grid;
  gap: 16px;
}

.entry-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.entry-item:active {
  transform: scale(0.95);
}

.entry-item__icon {
  position: relative;
  width: 48px;
  height: 48px;
  margin-bottom: 8px;
}

.entry-item__icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.entry-item__badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  font-size: 10px;
  line-height: 16px;
  text-align: center;
  color: #fff;
  background: #ff4d4f;
  border-radius: 8px;
}

.entry-item__name {
  font-size: 12px;
  color: #666;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}
</style>
