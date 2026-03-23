<template>
  <div id="app">
    <DynamicHomePage ref="pageRef" />
  </div>
</template>

<script>
import DynamicHomePage from './components/DynamicHomePage.vue'

export default {
  name: 'App',
  components: {
    DynamicHomePage,
  },
}
</script>

<style>
#app {
  min-height: 100vh;
}
</style>
