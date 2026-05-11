<template>
  <div class="admin-dashboard">
    <div class="container-lg">
      <h1 class="mb-4">Admin Dashboard</h1>

      <ul class="nav nav-tabs mb-4" role="tablist">
        <li class="nav-item" role="presentation">
          <button
            class="nav-link active"
            id="orders-tab"
            data-bs-toggle="tab"
            data-bs-target="#orders-panel"
            type="button"
            role="tab"
          >
            Orders
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button
            class="nav-link"
            id="restaurants-tab"
            data-bs-toggle="tab"
            data-bs-target="#restaurants-panel"
            type="button"
            role="tab"
          >
            Restaurants
          </button>
        </li>
      </ul>

      <div class="tab-content">
        <!-- Orders Tab -->
        <div class="tab-pane fade show active" id="orders-panel" role="tabpanel">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">All Orders</h5>

              <div class="filters mb-3 row g-2">
                <div class="col-md-4">
                  <select v-model="orderFilter.status" class="form-select" @change="loadOrders">
                    <option value="">All Status</option>
                    <option value="Pending">Pending</option>
                    <option value="Confirmed">Confirmed</option>
                    <option value="Preparing">Preparing</option>
                    <option value="Out for Delivery">Out for Delivery</option>
                    <option value="Delivered">Delivered</option>
                  </select>
                </div>
              </div>

              <div v-if="ordersLoading" class="alert alert-info">Loading orders...</div>
              <div v-else-if="orders.length === 0" class="alert alert-warning">No orders found</div>
              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-dark">
                    <tr>
                      <th>Order ID</th>
                      <th>Customer</th>
                      <th>Restaurant</th>
                      <th>Total</th>
                      <th>Status</th>
                      <th>Created</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="order in orders" :key="order.id">
                      <td><strong>#{{ order.id }}</strong></td>
                      <td>{{ order.customer_email }}</td>
                      <td>{{ order.restaurant_name }}</td>
                      <td>${{ order.total_price.toFixed(2) }}</td>
                      <td>
                        <span class="badge" :class="getStatusBadgeClass(order.status)">
                          {{ order.status }}
                        </span>
                      </td>
                      <td><small>{{ formatDate(order.created_at) }}</small></td>
                      <td>
                        <router-link :to="`/order/${order.id}`" class="btn btn-sm btn-info">
                          Details
                        </router-link>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Restaurants Tab -->
        <div class="tab-pane fade" id="restaurants-panel" role="tabpanel">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">Restaurants</h5>

              <div v-if="restaurantsLoading" class="alert alert-info">Loading restaurants...</div>
              <div v-else-if="restaurants.length === 0" class="alert alert-warning">No restaurants found</div>
              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-dark">
                    <tr>
                      <th>Name</th>
                      <th>Cuisine</th>
                      <th>Location</th>
                      <th>Rating</th>
                      <th>Status</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="restaurant in restaurants" :key="restaurant.id">
                      <td><strong>{{ restaurant.name }}</strong></td>
                      <td>{{ restaurant.cuisine }}</td>
                      <td><small>{{ restaurant.location }}</small></td>
                      <td>⭐ {{ restaurant.rating }}</td>
                      <td>
                        <span v-if="restaurant.is_active" class="badge bg-success">Active</span>
                        <span v-else class="badge bg-danger">Inactive</span>
                      </td>
                      <td>
                        <button
                          @click="toggleRestaurantStatus(restaurant.id, restaurant.is_active)"
                          :class="['btn btn-sm', restaurant.is_active ? 'btn-warning' : 'btn-info']"
                        >
                          {{ restaurant.is_active ? 'Deactivate' : 'Activate' }}
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
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
  name: 'AdminDashboard',
  data() {
    return {
      orders: [],
      restaurants: [],
      ordersLoading: false,
      restaurantsLoading: false,
      orderFilter: {
        status: ''
      }
    }
  },
  created() {
    this.loadOrders()
    this.loadRestaurants()
  },
  methods: {
    async loadOrders() {
      this.ordersLoading = true
      try {
        const params = {}
        if (this.orderFilter.status) params.status = this.orderFilter.status

        const response = await this.$axios.get('/orders', { params })
        this.orders = response.data.orders
      } catch (error) {
        alert('Failed to load orders')
      } finally {
        this.ordersLoading = false
      }
    },
    async loadRestaurants() {
      this.restaurantsLoading = true
      try {
        const response = await this.$axios.get('/restaurants')
        this.restaurants = response.data.restaurants
      } catch (error) {
        alert('Failed to load restaurants')
      } finally {
        this.restaurantsLoading = false
      }
    },
    async toggleRestaurantStatus(restaurantId, currentStatus) {
      try {
        await this.$axios.put(`/restaurants/${restaurantId}`, {
          is_active: !currentStatus
        })
        this.loadRestaurants()
      } catch (error) {
        alert('Failed to update restaurant status')
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
.admin-dashboard {
  padding: 20px 0;
}
</style>
