<template>
  <div class="orders-page">
    <div class="container-lg">
      <h1 class="mb-4">My Orders</h1>

      <div class="filters mb-4">
        <select v-model="selectedStatus" class="form-select w-25" @change="loadOrders">
          <option value="">All Status</option>
          <option value="Pending">Pending</option>
          <option value="Confirmed">Confirmed</option>
          <option value="Preparing">Preparing</option>
          <option value="Out for Delivery">Out for Delivery</option>
          <option value="Delivered">Delivered</option>
          <option value="Cancelled">Cancelled</option>
        </select>
      </div>

      <div v-if="loading" class="alert alert-info">Loading orders...</div>
      <div v-else-if="orders.length === 0" class="alert alert-warning">No orders found</div>
      <div v-else class="row g-3">
        <div v-for="order in orders" :key="order.id" class="col-md-12">
          <div class="card order-card">
            <div class="card-body">
              <div class="row align-items-center">
                <div class="col-md-6">
                  <h5 class="card-title">Order #{{ order.id }}</h5>
                  <p class="text-muted">{{ order.restaurant_name }}</p>
                  <p class="text-muted small">{{ formatDate(order.created_at) }}</p>
                </div>
                <div class="col-md-3">
                  <div>
                    <p class="mb-1">
                      <span class="badge" :class="getStatusBadgeClass(order.status)">
                        {{ order.status }}
                      </span>
                    </p>
                    <p class="text-muted small">
                      <span v-if="order.estimated_delivery_time">
                        ⏱ {{ order.estimated_delivery_time }} min
                      </span>
                    </p>
                  </div>
                </div>
                <div class="col-md-3 text-end">
                  <h5>${{ order.total_price.toFixed(2) }}</h5>
                  <router-link
                    :to="`/order/${order.id}`"
                    class="btn btn-sm btn-primary mt-2"
                  >
                    View Details
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <nav v-if="totalPages > 1" class="mt-4">
        <ul class="pagination justify-content-center">
          <li v-for="page in totalPages" :key="page" :class="['page-item', { active: currentPage === page }]">
            <a @click="currentPage = page" class="page-link" href="#">{{ page }}</a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MyOrders',
  data() {
    return {
      orders: [],
      loading: false,
      selectedStatus: '',
      currentPage: 1,
      totalPages: 1
    }
  },
  created() {
    this.loadOrders()
  },
  watch: {
    currentPage() {
      this.loadOrders()
    }
  },
  methods: {
    async loadOrders() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          per_page: 10
        }
        if (this.selectedStatus) params.status = this.selectedStatus

        const response = await this.$axios.get('/orders/user/my-orders', { params })
        this.orders = response.data.orders
        this.totalPages = response.data.pages
      } catch (error) {
        alert('Failed to load orders')
      } finally {
        this.loading = false
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
.order-card {
  transition: transform 0.2s;
}

.order-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
</style>
