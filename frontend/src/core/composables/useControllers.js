import { ref } from 'vue'
import { apiJson } from '../api/client.js'

const controllers = ref([])
const loading = ref(false)
const error = ref(null)

export function useControllers() {
  async function fetchControllers() {
    loading.value = true
    error.value = null
    try {
      controllers.value = await apiJson('/api/v1/controllers')
    } catch (err) {
      error.value = err.message
      controllers.value = []
    } finally {
      loading.value = false
    }
  }

  async function addController(name, url, accessToken, discoveredVia = null) {
    error.value = null
    const data = await apiJson('/api/v1/controllers', {
      method: 'POST',
      body: JSON.stringify({
        name,
        url,
        access_token: accessToken,
        discovered_via: discoveredVia,
      }),
    })
    controllers.value.unshift(data)
    return data
  }

  async function updateController(id, updates) {
    error.value = null
    const data = await apiJson(`/api/v1/controllers/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    })

    const index = controllers.value.findIndex((c) => c.id === id)
    if (index !== -1) {
      controllers.value[index] = data
    }
    return data
  }

  async function deleteController(id) {
    error.value = null
    await apiJson(`/api/v1/controllers/${id}`, {
      method: 'DELETE',
    })
    controllers.value = controllers.value.filter((c) => c.id !== id)
  }

  async function discoverControllers() {
    error.value = null
    return await apiJson('/api/v1/controllers/discover', {
      method: 'POST',
    })
  }

  async function testConnection(url, accessToken) {
    error.value = null
    return await apiJson('/api/v1/controllers/test-connection', {
      method: 'POST',
      body: JSON.stringify({
        url,
        access_token: accessToken,
      }),
    })
  }

  return {
    controllers,
    loading,
    error,
    fetchControllers,
    addController,
    updateController,
    deleteController,
    discoverControllers,
    testConnection,
  }
}
