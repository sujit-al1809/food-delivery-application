<template>
  <div class="home-page">
    <div class="container-lg">
      <h1 class="mb-4">Welcome to Food Delivery</h1>
      
      <div class="filters mb-4 row g-3">
        <div class="col-md-6">
          <input
            v-model="searchQuery"
            type="text"
            class="form-control"
            placeholder="Search restaurants..."
            @input="searchRestaurants"
          >
        </div>
        <div class="col-md-6">
          <select v-model="selectedCuisine" class="form-select" @change="filterRestaurants">
            <option value="">All Cuisines</option>
            <option value="Italian">Italian</option>
            <option value="American">American</option>
            <option value="Chinese">Chinese</option>
            <option value="Indian">Indian</option>
            <option value="Mexican">Mexican</option>
            <option value="Japanese">Japanese</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="alert alert-info">Loading restaurants...</div>
      <div v-else-if="restaurants.length === 0" class="alert alert-warning">No restaurants found</div>
      <div v-else class="row g-4">
        <div v-for="restaurant in restaurants" :key="restaurant.id" class="col-md-4">
          <div class="card h-100 restaurant-card">
            <div class="card-body">
              <h5 class="card-title">{{ restaurant.name }}</h5>
              <p class="card-text text-muted">{{ restaurant.cuisine }}</p>
              <p class="card-text">
                <small>📍 {{ restaurant.location }}</small>
              </p>
              <p class="card-text">
                <small>⭐ Rating: {{ restaurant.rating }}</small>
              </p>
              <p class="card-text">
                <small>🕐 {{ restaurant.hours_open }}</small>
              </p>
              <router-link
                :to="`/restaurant/${restaurant.id}`"
                class="btn btn-primary btn-sm mt-2"
              >
                View Menu
              </router-link>
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
  name: 'Home',
  data() {
    return {
      restaurants: [],
      loading: false,
      searchQuery: '',
      selectedCuisine: '',
      currentPage: 1,
      totalPages: 1
    }
  },
  created() {
    this.loadRestaurants()
  },
  watch: {
    currentPage() {
      this.loadRestaurants()
    }
  },
  methods: {
    async loadRestaurants() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          per_page: 9
        }
        if (this.selectedCuisine) params.cuisine = this.selectedCuisine
        if (this.searchQuery) params.search = this.searchQuery

        const response = await this.$axios.get('/restaurants', { params })
        this.restaurants = response.data.restaurants
        this.totalPages = response.data.pages
      } catch (error) {
        alert('Failed to load restaurants')
        console.error(error)
      } finally {
        this.loading = false
      }
    },
    searchRestaurants() {
      this.currentPage = 1
      this.loadRestaurants()
    },
    filterRestaurants() {
      this.currentPage = 1
      this.loadRestaurants()
    }
  }
}
</script>

<style scoped>
.restaurant-card {
  transition: transform 0.2s;
  cursor: pointer;
}

.restaurant-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
</style>
