<template>
  <div class="auth-page">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card">
            <div class="card-body p-5">
              <h2 class="card-title text-center mb-4">Register</h2>
              
              <form @submit.prevent="register">
                <div class="mb-3">
                  <label class="form-label">First Name</label>
                  <input
                    v-model="form.first_name"
                    type="text"
                    class="form-control"
                  >
                </div>

                <div class="mb-3">
                  <label class="form-label">Last Name</label>
                  <input
                    v-model="form.last_name"
                    type="text"
                    class="form-control"
                  >
                </div>

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

                <div class="mb-3">
                  <label class="form-label">Role</label>
                  <select v-model="form.role" class="form-select">
                    <option value="Customer">Customer</option>
                    <option value="RestaurantOwner">Restaurant Owner</option>
                    <option value="DeliveryAgent">Delivery Agent</option>
                  </select>
                </div>

                <div v-if="error" class="alert alert-danger">{{ error }}</div>

                <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                  {{ loading ? 'Registering...' : 'Register' }}
                </button>
              </form>

              <p class="text-center mt-3">
                Already have an account?
                <router-link to="/login">Login here</router-link>
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
  name: 'Register',
  data() {
    return {
      form: {
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        role: 'Customer'
      },
      loading: false,
      error: null
    }
  },
  methods: {
    async register() {
      this.loading = true
      this.error = null

      try {
        const response = await this.$axios.post('/auth/register', this.form)
        alert('Registration successful! Please login.')
        this.$router.push('/login')
      } catch (error) {
        this.error = error.response?.data?.message || 'Registration failed'
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
