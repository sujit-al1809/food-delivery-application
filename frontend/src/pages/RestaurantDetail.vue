<template>
  <div class="restaurant-detail">
    <div class="container-lg">
      <div v-if="loading" class="alert alert-info">Loading restaurant...</div>
      <div v-else-if="restaurant">
        <div class="restaurant-header mb-4">
          <h1>{{ restaurant.name }}</h1>
          <p class="text-muted">{{ restaurant.cuisine }} • {{ restaurant.location }}</p>
          <p>
            <span class="badge bg-success">⭐ {{ restaurant.rating }}</span>
            <span class="badge bg-info">📞 {{ restaurant.phone }}</span>
            <span class="badge bg-primary">🕐 {{ restaurant.hours_open }}</span>
          </p>
        </div>

        <div class="row">
          <div class="col-md-8">
            <h3 class="mb-3">Menu</h3>
            
            <div class="menu-filters mb-3">
              <select v-model="selectedCategory" class="form-select w-25" @change="filterMenu">
                <option value="">All Categories</option>
                <option value="Appetizer">Appetizer</option>
                <option value="Main">Main Course</option>
                <option value="Dessert">Dessert</option>
                <option value="Drinks">Drinks</option>
                <option value="Salad">Salad</option>
              </select>
            </div>

            <div class="row g-3">
              <div v-for="item in filteredMenu" :key="item.id" class="col-md-6">
                <div class="card menu-item-card">
                  <div class="card-body">
                    <h5 class="card-title">{{ item.name }}</h5>
                    <p class="card-text text-muted small">{{ item.description }}</p>
                    <p class="card-text">
                      <strong>${{ item.price.toFixed(2) }}</strong>
                      <br>
                      <small class="text-muted">⏱ {{ item.preparation_time }} min</small>
                    </p>
                    <div class="input-group mb-2" style="width: 100px">
                      <button
                        class="btn btn-outline-secondary btn-sm"
                        @click="decrementQty(item.id)"
                        type="button"
                      >
                        -
                      </button>
                      <input
                        type="text"
                        class="form-control form-control-sm text-center"
                        :value="getItemQty(item.id)"
                        readonly
                      >
                      <button
                        class="btn btn-outline-secondary btn-sm"
                        @click="incrementQty(item.id, item)"
                        type="button"
                      >
                        +
                      </button>
                    </div>
                    <button
                      @click="addToCart(item)"
                      :disabled="getItemQty(item.id) === 0"
                      class="btn btn-primary btn-sm w-100"
                    >
                      Add to Cart
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-4">
            <div class="card sticky-top" style="top: 20px">
              <div class="card-body">
                <h5 class="card-title">Cart Summary</h5>
                <div v-if="cart.length === 0" class="text-muted">Your cart is empty</div>
                <div v-else>
                  <div v-for="item in cart" :key="item.id" class="mb-2 pb-2 border-bottom">
                    <div class="d-flex justify-content-between">
                      <span>{{ item.name }} x {{ item.quantity }}</span>
                      <span>${{ (item.price * item.quantity).toFixed(2) }}</span>
                    </div>
                  </div>
                  <div class="mt-3">
                    <h6>Total: ${{ cartTotal.toFixed(2) }}</h6>
                    <router-link to="/cart" class="btn btn-success w-100">
                      Proceed to Checkout
                    </router-link>
                  </div>
                </div>
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
  name: 'RestaurantDetail',
  data() {
    return {
      restaurant: null,
      loading: false,
      selectedCategory: '',
      cart: [],
      quantities: {}
    }
  },
  computed: {
    filteredMenu() {
      if (!this.restaurant) return []
      let items = this.restaurant.menu_items

      if (this.selectedCategory) {
        items = items.filter(item => item.category === this.selectedCategory)
      }

      return items
    },
    cartTotal() {
      return this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    }
  },
  created() {
    this.loadRestaurant()
    this.loadCart()
  },
  methods: {
    async loadRestaurant() {
      this.loading = true
      try {
        const response = await this.$axios.get(`/restaurants/${this.$route.params.id}`)
        this.restaurant = response.data
      } catch (error) {
        alert('Failed to load restaurant')
      } finally {
        this.loading = false
      }
    },
    loadCart() {
      const saved = localStorage.getItem('cart')
      this.cart = saved ? JSON.parse(saved) : []
    },
    saveCart() {
      localStorage.setItem('cart', JSON.stringify(this.cart))
      window.dispatchEvent(new Event('cartChanged'))
    },
    addToCart(item) {
      const qty = this.getItemQty(item.id)
      if (qty > 0) {
        const cartItem = this.cart.find(c => c.id === item.id)
        if (cartItem) {
          cartItem.quantity += qty
        } else {
          this.cart.push({
            ...item,
            quantity: qty,
            restaurant_id: this.restaurant.id
          })
        }
        this.quantities[item.id] = 0
        this.saveCart()
      }
    },
    incrementQty(itemId, item) {
      this.quantities[itemId] = (this.quantities[itemId] || 0) + 1
    },
    decrementQty(itemId) {
      if ((this.quantities[itemId] || 0) > 0) {
        this.quantities[itemId]--
      }
    },
    getItemQty(itemId) {
      return this.quantities[itemId] || 0
    },
    filterMenu() {
      // Reactive computed property will handle this
    }
  }
}
</script>

<style scoped>
.menu-item-card {
  transition: transform 0.2s;
}

.menu-item-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
</style>
