<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container-fluid">
        <router-link to="/" class="navbar-brand">🍕 Food Delivery</router-link>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <router-link to="/" class="nav-link">Home</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/eta-predictor" class="nav-link">ETA Predictor</router-link>
            </li>
            <li v-if="isAuthenticated" class="nav-item">
              <router-link to="/cart" class="nav-link">
                🛒 Cart <span v-if="cartCount" class="badge bg-danger">{{ cartCount }}</span>
              </router-link>
            </li>
            <li v-if="isAuthenticated" class="nav-item">
              <router-link to="/orders" class="nav-link">My Orders</router-link>
            </li>
            <li v-if="isAdmin" class="nav-item">
              <router-link to="/admin" class="nav-link">Admin</router-link>
            </li>
            <li v-if="!isAuthenticated" class="nav-item">
              <router-link to="/login" class="nav-link">Login</router-link>
            </li>
            <li v-if="!isAuthenticated" class="nav-item">
              <router-link to="/register" class="nav-link">Register</router-link>
            </li>
            <li v-if="isAuthenticated" class="nav-item">
              <a href="#" @click.prevent="logout" class="nav-link">Logout</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <main class="container-fluid py-4">
      <router-view />
    </main>

    <footer class="bg-dark text-white text-center py-3 mt-5">
      <p>&copy; 2024 Food Delivery App. All rights reserved.</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      isAuthenticated: false,
      isAdmin: false,
      cartCount: 0
    }
  },
  created() {
    this.checkAuth()
    this.updateCartCount()
    // Listen for cart changes
    window.addEventListener('cartChanged', this.updateCartCount)
  },
  destroyed() {
    window.removeEventListener('cartChanged', this.updateCartCount)
  },
  methods: {
    checkAuth() {
      const token = localStorage.getItem('auth_token')
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      this.isAuthenticated = !!token
      this.isAdmin = user.roles?.includes('Admin') || false
    },
    updateCartCount() {
      const cart = JSON.parse(localStorage.getItem('cart') || '[]')
      this.cartCount = cart.reduce((sum, item) => sum + (item.quantity || 0), 0)
    },
    logout() {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      localStorage.removeItem('cart')
      this.isAuthenticated = false
      this.isAdmin = false
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}

footer {
  margin-top: auto;
}
</style>
