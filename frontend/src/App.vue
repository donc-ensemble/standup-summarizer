<template>
  <div id="app">
    <Navbar />
    <router-view/>
  </div>
</template>

<script>
import Navbar from '@/components/Navbar.vue';
import { onUnmounted } from 'vue'
import { eventBus } from './eventBus'

export default {
  name: 'App',
  components: {
    Navbar
  },
  setup() {
    onUnmounted(() => {
      eventBus.closeAllConnections()
    })
  }
};
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Arial', sans-serif;
  background-color: #f5f5f5;
  color: #333;
  line-height: 1.6;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>