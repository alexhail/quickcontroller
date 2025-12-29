import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../core/composables/useAuth.js'
import { initializeApps, getAllApps } from '../apps/framework/index.js'

import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AppLayout from '../apps/framework/AppLayout.vue'

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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Dynamic app route mounting - called after apps are initialized
export async function mountAppRoutes() {
  await initializeApps()
  const apps = getAllApps()

  for (const app of apps) {
    const appRoute = {
      path: `/app/${app.appId}`,
      component: AppLayout,
      meta: { requiresAuth: true, appId: app.appId },
      children: app.routes.map(route => ({
        ...route,
        name: route.name ? `${app.appId}-${route.name}` : undefined,
      }))
    }
    router.addRoute(appRoute)
  }

  // Default redirect: / -> default app
  const defaultApp = apps.find(a => a.defaultApp) || apps[0]
  if (defaultApp) {
    router.addRoute({
      path: '/',
      redirect: `/app/${defaultApp.appId}`,
      meta: { requiresAuth: true }
    })
  }
}

// Navigation guard for auth
router.beforeEach(async (to, from, next) => {
  const { isAuthenticated, loading, initialize } = useAuth()

  await initialize()

  if (to.meta.requiresAuth && !isAuthenticated.value) {
    next({ name: 'login' })
  } else if (to.meta.guest && isAuthenticated.value) {
    // Redirect to default app instead of 'dashboard'
    const apps = getAllApps()
    const defaultApp = apps.find(a => a.defaultApp) || apps[0]
    if (defaultApp) {
      next(`/app/${defaultApp.appId}`)
    } else {
      next('/')
    }
  } else {
    next()
  }
})

export default router
