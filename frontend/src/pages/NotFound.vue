<template>
  <div class="not-found">
    <div class="container text-center">
      <h1 class="display-1">404</h1>
      <h2 class="mb-4">Page Not Found</h2>
      <p class="text-muted mb-4">Sorry, the page you're looking for doesn't exist.</p>
      <router-link to="/" class="btn btn-primary btn-lg">Go Back Home</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  text-align: center;
}
</style>
