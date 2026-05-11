import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../pages/Home.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../pages/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../pages/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/restaurant/:id',
    name: 'RestaurantDetail',
    component: () => import('../pages/RestaurantDetail.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('../pages/Cart.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/orders',
    name: 'MyOrders',
    component: () => import('../pages/MyOrders.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/order/:id',
    name: 'OrderDetail',
    component: () => import('../pages/OrderDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/eta-predictor',
    name: 'ETAPredictor',
    component: () => import('../pages/ETAPredictor.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('../pages/AdminDashboard.vue'),
    meta: { requiresAuth: true, requiredRole: 'Admin' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../pages/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard for auth checks
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('auth_token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.requiredRole && !user.roles?.includes(to.meta.requiredRole)) {
    next('/')
  } else {
    next()
  }
})

export default router
