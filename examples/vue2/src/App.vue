<template>
  <div id="app">
    <DynamicHomePage
      ref="pageRef"
      @action="handleAction"
      @loaded="handleLoaded"
      @error="handleError"
    />
  </div>
</template>

<script>
import DynamicHomePage from './components/DynamicHomePage.vue'

/**
 * 根组件
 * @description 动态首页演示应用
 */
export default {
  name: 'App',
  components: {
    DynamicHomePage,
  },
  methods: {
    handleAction(item) {
      console.log('Action:', item)
    },
    handleLoaded(data) {
      console.log('Page loaded:', data.length, 'sections')
    },
    handleError(error) {
      console.error('Page error:', error)
    },
  },
}
</script>

<style>
#app {
  min-height: 100vh;
}
</style>
