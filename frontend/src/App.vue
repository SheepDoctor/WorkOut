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
  background-color: #020617;
  color: #f8fafc;
  overflow: hidden;
}

#app {
  width: 100vw;
  height: 100vh;
}
</style>

