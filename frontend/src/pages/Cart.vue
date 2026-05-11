<template>
  <div class="cart-page">
    <div class="container-lg">
      <h1 class="mb-4">Your Cart</h1>

      <div v-if="!cart || cart.length === 0" class="alert alert-info">
        Your cart is empty.
        <router-link to="/">Continue Shopping</router-link>
      </div>
      <div v-else class="row">
        <div class="col-md-8">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">Order Items</h5>
              <div v-for="item in cart" :key="item.id" class="cart-item mb-3 pb-3 border-bottom">
                <div class="row align-items-center">
                  <div class="col-md-6">
                    <h6>{{ item.name }}</h6>
                    <small class="text-muted">From restaurant ID: {{ item.restaurant_id }}</small>
                  </div>
                  <div class="col-md-3">
                    <div class="input-group" style="width: 120px">
                      <button
                        class="btn btn-sm btn-outline-secondary"
                        @click="decrementQty(item.id)"
                        type="button"
                      >
                        -
                      </button>
                      <input
                        type="text"
                        class="form-control form-control-sm text-center"
                        :value="item.quantity"
                        readonly
                      >
                      <button
                        class="btn btn-sm btn-outline-secondary"
                        @click="incrementQty(item.id)"
                        type="button"
                      >
                        +
                      </button>
                    </div>
                  </div>
                  <div class="col-md-2 text-end">
                    <strong>${{ (item.price * item.quantity).toFixed(2) }}</strong>
                  </div>
                  <div class="col-md-1 text-end">
                    <button
                      class="btn btn-sm btn-danger"
                      @click="removeFromCart(item.id)"
                      type="button"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <div class="card sticky-top" style="top: 20px">
            <div class="card-body">
              <h5 class="card-title">Order Summary</h5>
              
              <div class="mb-3">
                <label class="form-label">Delivery Address *</label>
                <textarea
                  v-model="orderForm.delivery_address"
                  class="form-control"
                  rows="3"
                  required
                ></textarea>
              </div>

              <div class="mb-3">
                <label class="form-label">Special Instructions</label>
                <textarea
                  v-model="orderForm.special_instructions"
                  class="form-control"
                  rows="2"
                ></textarea>
              </div>

              <div class="d-flex justify-content-between mb-2">
                <span>Subtotal:</span>
                <span>${{ subtotal.toFixed(2) }}</span>
              </div>
              <div class="d-flex justify-content-between mb-3 fs-5 border-top pt-2">
                <strong>Total:</strong>
                <strong>${{ subtotal.toFixed(2) }}</strong>
              </div>

              <button
                @click="placeOrder"
                :disabled="!orderForm.delivery_address || loading"
                class="btn btn-success w-100 btn-lg"
              >
                {{ loading ? 'Placing Order...' : 'Place Order' }}
              </button>

              <router-link to="/" class="btn btn-outline-secondary w-100 mt-2">
                Continue Shopping
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Cart',
  data() {
    return {
      cart: [],
      orderForm: {
        delivery_address: '',
        special_instructions: ''
      },
      loading: false
    }
  },
  computed: {
    subtotal() {
      return this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    }
  },
  created() {
    this.loadCart()
  },
  methods: {
    loadCart() {
      const saved = localStorage.getItem('cart')
      this.cart = saved ? JSON.parse(saved) : []
    },
    saveCart() {
      localStorage.setItem('cart', JSON.stringify(this.cart))
      window.dispatchEvent(new Event('cartChanged'))
    },
    incrementQty(itemId) {
      const item = this.cart.find(c => c.id === itemId)
      if (item) item.quantity++
      this.saveCart()
    },
    decrementQty(itemId) {
      const item = this.cart.find(c => c.id === itemId)
      if (item && item.quantity > 1) item.quantity--
      this.saveCart()
    },
    removeFromCart(itemId) {
      this.cart = this.cart.filter(c => c.id !== itemId)
      this.saveCart()
    },
    async placeOrder() {
      if (!this.orderForm.delivery_address) {
        alert('Please enter delivery address')
        return
      }

      this.loading = true
      try {
        // For now, we'll place an order with the first restaurant
        // In production, handle multiple restaurants
        const restaurantId = this.cart[0]?.restaurant_id

        const payload = {
          restaurant_id: restaurantId,
          items: this.cart.map(item => ({
            menuitem_id: item.id,
            quantity: item.quantity
          })),
          delivery_address: this.orderForm.delivery_address,
          special_instructions: this.orderForm.special_instructions
        }

        const response = await this.$axios.post('/orders', payload)
        
        // Clear cart
        localStorage.removeItem('cart')
        window.dispatchEvent(new Event('cartChanged'))

        alert('Order placed successfully!')
        this.$router.push(`/order/${response.data.order_id}`)
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to place order')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.cart-item {
  padding: 10px 0;
}
</style>
