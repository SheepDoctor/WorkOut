<template>
  <div id="app" class="h-screen flex items-center justify-center bg-slate-950">
    <main class="w-full h-full flex items-center justify-center">
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

body {
  font-family: 'Inter', sans-serif;
  margin: 0;
  padding: 0;
  background-color: #050b18;
  color: #e2e8f0;
  overflow: hidden;
}

#app {
  width: 100vw;
  height: 100vh;
  background: radial-gradient(circle at top right, #1e293b 0%, #050b18 100%);
}
</style>

