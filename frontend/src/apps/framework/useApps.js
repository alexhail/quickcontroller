import { ref, computed } from 'vue'
import { apiJson } from '../../core/api/client.js'
import { getAllApps, getApp } from './index.js'

const userAppPermissions = ref(null)
const loading = ref(false)
const currentAppId = ref(null)

export function useApps() {
  async function fetchPermissions() {
    loading.value = true
    try {
      userAppPermissions.value = await apiJson('/api/v1/apps/permissions')
    } catch (err) {
      console.error('Failed to fetch app permissions:', err)
      userAppPermissions.value = []
    } finally {
      loading.value = false
    }
  }

  const accessibleApps = computed(() => {
    const allApps = getAllApps()
    if (!userAppPermissions.value) return allApps // Return all before permissions loaded

    return allApps.filter(app => {
      const perm = userAppPermissions.value.find(p => p.app_id === app.appId)
      return perm?.has_access ?? true // Default to accessible
    })
  })

  const currentApp = computed(() => {
    return currentAppId.value ? getApp(currentAppId.value) : null
  })

  function setCurrentApp(appId) {
    currentAppId.value = appId
  }

  const defaultApp = computed(() => {
    return accessibleApps.value.find(app => app.defaultApp) || accessibleApps.value[0]
  })

  return {
    loading,
    accessibleApps,
    currentApp,
    currentAppId,
    setCurrentApp,
    defaultApp,
    fetchPermissions
  }
}
