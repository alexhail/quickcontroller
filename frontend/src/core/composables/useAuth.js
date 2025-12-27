import { ref, computed } from 'vue'
import { api, apiJson, setAccessToken, clearAccessToken } from '../api/client.js'

const user = ref(null)
const loading = ref(true)
const initialized = ref(false)

export function useAuth() {
  const isAuthenticated = computed(() => !!user.value)

  async function register(email, password) {
    const data = await apiJson('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    return data
  }

  async function login(email, password) {
    const response = await api('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }))
      throw new Error(error.detail || 'Login failed')
    }

    const data = await response.json()
    setAccessToken(data.access_token)

    await fetchUser()
    return data
  }

  async function logout() {
    try {
      await api('/api/v1/auth/logout', { method: 'POST' })
    } finally {
      clearAccessToken()
      user.value = null
    }
  }

  async function fetchUser() {
    try {
      const data = await apiJson('/api/v1/auth/me')
      user.value = data
      return data
    } catch {
      user.value = null
      return null
    }
  }

  async function initialize() {
    if (initialized.value) return

    loading.value = true
    try {
      const response = await api('/api/v1/auth/refresh', { method: 'POST' })
      if (response.ok) {
        const data = await response.json()
        setAccessToken(data.access_token)
        await fetchUser()
      }
    } catch {
      // Not authenticated
    } finally {
      loading.value = false
      initialized.value = true
    }
  }

  return {
    user,
    loading,
    isAuthenticated,
    register,
    login,
    logout,
    fetchUser,
    initialize,
  }
}
