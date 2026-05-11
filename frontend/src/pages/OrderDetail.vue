<template>
  <div class="order-detail">
    <div class="container-lg">
      <h1 class="mb-4">Order Details</h1>

      <div v-if="loading" class="alert alert-info">Loading order...</div>
      <div v-else-if="order">
        <div class="row">
          <div class="col-md-8">
            <div class="card mb-3">
              <div class="card-body">
                <h5 class="card-title">Order #{{ order.id }}</h5>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <p><strong>Restaurant:</strong> {{ order.restaurant_name }}</p>
                    <p><strong>Status:</strong></p>
                    <p>
                      <span class="badge" :class="getStatusBadgeClass(order.status)">
                        {{ order.status }}
                      </span>
                    </p>
                  </div>
                  <div class="col-md-6">
                    <p><strong>Created:</strong> {{ formatDate(order.created_at) }}</p>
                    <p><strong>Last Updated:</strong> {{ formatDate(order.updated_at) }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="card mb-3">
              <div class="card-body">
                <h5 class="card-title">Order Items</h5>
                <table class="table table-sm">
                  <thead>
                    <tr>
                      <th>Item</th>
                      <th>Qty</th>
                      <th>Price</th>
                      <th>Subtotal</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in order.items" :key="item.id">
                      <td>{{ item.name }}</td>
                      <td>{{ item.quantity }}</td>
                      <td>${{ item.price.toFixed(2) }}</td>
                      <td>${{ item.subtotal.toFixed(2) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div class="card">
              <div class="card-body">
                <h5 class="card-title">Delivery Information</h5>
                <p><strong>Address:</strong> {{ order.delivery_address }}</p>
                <p v-if="order.special_instructions">
                  <strong>Special Instructions:</strong> {{ order.special_instructions }}
                </p>
                <p v-if="order.estimated_delivery_time">
                  <strong>Estimated Delivery Time:</strong> {{ order.estimated_delivery_time }} minutes
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-4">
            <div class="card sticky-top" style="top: 20px">
              <div class="card-body">
                <h5 class="card-title">Summary</h5>
                <div class="d-flex justify-content-between mb-2">
                  <span>Subtotal:</span>
                  <span>${{ subtotal.toFixed(2) }}</span>
                </div>
                <div class="d-flex justify-content-between mb-3 fs-5 border-top pt-2">
                  <strong>Total:</strong>
                  <strong>${{ order.total_price.toFixed(2) }}</strong>
                </div>

                <div class="alert alert-info mb-3">
                  <h6>Order Status Timeline</h6>
                  <small>
                    <div>📋 Pending</div>
                    <div v-if="['Confirmed', 'Preparing', 'Out for Delivery', 'Delivered'].includes(order.status)">
                      ✓ Confirmed
                    </div>
                    <div v-if="['Preparing', 'Out for Delivery', 'Delivered'].includes(order.status)">
                      ✓ Preparing
                    </div>
                    <div v-if="['Out for Delivery', 'Delivered'].includes(order.status)">
                      ✓ Out for Delivery
                    </div>
                    <div v-if="order.status === 'Delivered'">
                      ✓ Delivered
                    </div>
                  </small>
                </div>

                <button v-if="order.status !== 'Delivered' && order.status !== 'Cancelled'" @click="cancelOrder" class="btn btn-danger w-100">
                  Cancel Order
                </button>
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
  name: 'OrderDetail',
  data() {
    return {
      order: null,
      loading: false
    }
  },
  computed: {
    subtotal() {
      if (!this.order) return 0
      return this.order.items.reduce((sum, item) => sum + item.subtotal, 0)
    }
  },
  created() {
    this.loadOrder()
  },
  methods: {
    async loadOrder() {
      this.loading = true
      try {
        const response = await this.$axios.get(`/orders/${this.$route.params.id}`)
        this.order = response.data
      } catch (error) {
        alert('Failed to load order')
      } finally {
        this.loading = false
      }
    },
    async cancelOrder() {
      if (confirm('Are you sure you want to cancel this order?')) {
        try {
          await this.$axios.put(`/orders/${this.order.id}/status`, {
            status: 'Cancelled'
          })
          this.order.status = 'Cancelled'
          alert('Order cancelled successfully')
        } catch (error) {
          alert('Failed to cancel order')
        }
      }
    },
    getStatusBadgeClass(status) {
      const classes = {
        'Pending': 'bg-warning',
        'Confirmed': 'bg-info',
        'Preparing': 'bg-primary',
        'Out for Delivery': 'bg-warning text-dark',
        'Delivered': 'bg-success',
        'Cancelled': 'bg-danger'
      }
      return classes[status] || 'bg-secondary'
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
    }
  }
}
</script>

<style scoped>
.order-detail {
  padding: 20px 0;
}
</style>
