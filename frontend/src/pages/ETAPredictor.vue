<template>
  <div class="eta-predictor">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-8">
          <div class="card">
            <div class="card-body p-5">
              <h2 class="card-title text-center mb-4">🚚 Delivery Time Estimator</h2>
              <p class="text-center text-muted mb-4">
                Get an AI-powered estimate of your delivery time
              </p>

              <form @submit.prevent="predictETA">
                <div class="mb-3">
                  <label class="form-label">Distance (km) *</label>
                  <input
                    v-model.number="form.distance_km"
                    type="number"
                    step="0.1"
                    min="1"
                    max="50"
                    class="form-control form-control-lg"
                    placeholder="e.g., 5"
                    required
                  >
                  <small class="form-text text-muted">Distance from restaurant to delivery location</small>
                </div>

                <div class="mb-3">
                  <label class="form-label">Number of Items *</label>
                  <input
                    v-model.number="form.order_items"
                    type="number"
                    min="1"
                    max="100"
                    class="form-control form-control-lg"
                    placeholder="e.g., 3"
                    required
                  >
                  <small class="form-text text-muted">Total number of items in the order</small>
                </div>

                <div class="mb-3">
                  <label class="form-label">Hour of Day (24h format) *</label>
                  <input
                    v-model.number="form.hour_of_day"
                    type="number"
                    min="0"
                    max="23"
                    class="form-control form-control-lg"
                    placeholder="e.g., 14"
                    required
                  >
                  <small class="form-text text-muted">Current hour (0-23). Note: peak hours (11-2pm, 6-9pm) may take longer</small>
                </div>

                <div v-if="error" class="alert alert-danger">{{ error }}</div>

                <button type="submit" class="btn btn-primary btn-lg w-100" :disabled="loading">
                  {{ loading ? 'Calculating...' : 'Estimate Delivery Time' }}
                </button>
              </form>

              <div v-if="result" class="mt-5 p-4 bg-light rounded">
                <h4 class="text-center mb-4">📊 Prediction Result</h4>
                <div class="result-box text-center mb-4 p-4 bg-white rounded border-2 border-success">
                  <h1 class="text-success">{{ result.estimated_minutes }} <span class="small">minutes</span></h1>
                  <p class="text-muted mt-2">Estimated delivery time from restaurant</p>
                </div>

                <div class="row g-2 mt-3">
                  <div class="col-md-4 text-center">
                    <p class="text-muted mb-1">Distance</p>
                    <p class="fw-bold">{{ result.distance_km }} km</p>
                  </div>
                  <div class="col-md-4 text-center">
                    <p class="text-muted mb-1">Items</p>
                    <p class="fw-bold">{{ result.order_items }}</p>
                  </div>
                  <div class="col-md-4 text-center">
                    <p class="text-muted mb-1">Time</p>
                    <p class="fw-bold">{{ formatHour(result.hour_of_day) }}</p>
                  </div>
                </div>

                <div v-if="result.note" class="alert alert-info mt-3">
                  <small>{{ result.note }}</small>
                </div>
              </div>

              <div class="mt-5 pt-3 border-top">
                <h6 class="mb-3">ℹ️ How It Works</h6>
                <ul class="small text-muted">
                  <li>Our AI model trained on thousands of deliveries</li>
                  <li>Considers distance, order complexity, and time of day</li>
                  <li>Peak hours (11am-2pm, 6pm-9pm) may have longer estimates</li>
                  <li>Actual time may vary based on real-time conditions</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ETAPredictor',
  data() {
    return {
      form: {
        distance_km: 5,
        order_items: 3,
        hour_of_day: new Date().getHours()
      },
      result: null,
      loading: false,
      error: null
    }
  },
  methods: {
    async predictETA() {
      this.loading = true
      this.error = null
      this.result = null

      try {
        const response = await this.$axios.post('/predict-eta', this.form)
        this.result = response.data
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to predict ETA'
      } finally {
        this.loading = false
      }
    },
    formatHour(hour) {
      const period = hour >= 12 ? 'PM' : 'AM'
      const displayHour = hour % 12 || 12
      return `${displayHour}:00 ${period}`
    }
  }
}
</script>

<style scoped>
.eta-predictor {
  min-height: 100vh;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 0;
}

.card {
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  border: none;
}

.result-box {
  border-width: 3px !important;
}
</style>
