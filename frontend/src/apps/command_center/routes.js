export default [
  {
    path: '',
    name: 'dashboard',
    component: () => import('./views/DashboardView.vue')
  },
  {
    path: 'controllers',
    name: 'controllers',
    component: () => import('./views/ControllersView.vue')
  },
  {
    path: 'users',
    name: 'users',
    component: () => import('./views/UsersView.vue')
  },
  {
    path: 'system',
    name: 'system',
    component: () => import('./views/SystemView.vue')
  },
  {
    path: 'audit',
    name: 'audit',
    component: () => import('./views/AuditView.vue')
  }
]
