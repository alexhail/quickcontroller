import { createApp } from 'vue'
import App from './App.vue'
import router, { mountAppRoutes } from './router'
import './styles/main.scss'

const app = createApp(App)

// Mount dynamic app routes before using router
mountAppRoutes().then(() => {
  app.use(router)
  app.mount('#app')
})
