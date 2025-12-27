import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../core/composables/useAuth.js'

import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import ControllersView from '../views/ControllersView.vue'
import DevicesView from '../views/DevicesView.vue'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { guest: true },
  },
  {
    path: '/',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true },
  },
  {
    path: '/controllers',
    name: 'controllers',
    component: ControllersView,
    meta: { requiresAuth: true },
  },
  {
    path: '/devices',
    name: 'devices',
    component: DevicesView,
    meta: { requiresAuth: true },
  },
  {
    path: '/devices/:controllerId',
    name: 'devices-controller',
    component: DevicesView,
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const { isAuthenticated, loading, initialize } = useAuth()

  await initialize()

  if (to.meta.requiresAuth && !isAuthenticated.value) {
    next({ name: 'login' })
  } else if (to.meta.guest && isAuthenticated.value) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
