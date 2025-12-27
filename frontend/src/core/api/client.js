const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

let accessToken = null

export function setAccessToken(token) {
  accessToken = token
}

export function getAccessToken() {
  return accessToken
}

export function clearAccessToken() {
  accessToken = null
}

export async function api(endpoint, options = {}) {
  const url = `${API_URL}${endpoint}`

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include',
  })

  if (response.status === 401 && endpoint !== '/api/v1/auth/refresh') {
    const refreshed = await tryRefreshToken()
    if (refreshed) {
      headers['Authorization'] = `Bearer ${accessToken}`
      return fetch(url, { ...options, headers, credentials: 'include' })
    }
  }

  return response
}

async function tryRefreshToken() {
  try {
    const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      credentials: 'include',
    })

    if (response.ok) {
      const data = await response.json()
      setAccessToken(data.access_token)
      return true
    }
  } catch {
    // Refresh failed
  }

  clearAccessToken()
  return false
}

export async function apiJson(endpoint, options = {}) {
  const response = await api(endpoint, options)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || 'Request failed')
  }

  return response.json()
}
