<template>
  <div class="auth-page">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card">
            <div class="card-body p-5">
              <h2 class="card-title text-center mb-4">Login</h2>
              
              <form @submit.prevent="login">
                <div class="mb-3">
                  <label class="form-label">Email</label>
                  <input
                    v-model="form.email"
                    type="email"
                    class="form-control"
                    required
                  >
                </div>

                <div class="mb-3">
                  <label class="form-label">Password</label>
                  <input
                    v-model="form.password"
                    type="password"
                    class="form-control"
                    required
                  >
                </div>

                <div v-if="error" class="alert alert-danger">{{ error }}</div>

                <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                  {{ loading ? 'Logging in...' : 'Login' }}
                </button>
              </form>

              <p class="text-center mt-3">
                Don't have an account?
                <router-link to="/register">Register here</router-link>
              </p>

              <hr>
              <p class="text-center text-muted small">
                Demo credentials:<br>
                Email: admin@fooddelivery.com<br>
                Password: admin123456
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      form: {
        email: '',
        password: ''
      },
      loading: false,
      error: null
    }
  },
  methods: {
    async login() {
      this.loading = true
      this.error = null

      try {
        const response = await this.$axios.post('/auth/login', this.form)
        
        // Store token and user info
        localStorage.setItem('auth_token', response.data.token)
        localStorage.setItem('user', JSON.stringify(response.data.user))

        // Redirect to home
        this.$router.push('/')
      } catch (error) {
        this.error = error.response?.data?.message || 'Login failed'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card {
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}
</style>
