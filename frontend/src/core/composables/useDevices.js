import { ref, computed } from 'vue'
import { apiJson } from '../api/client.js'

const entities = ref([])
const loading = ref(false)
const error = ref(null)
const selectedController = ref(null)
const selectedDomain = ref(null)
const viewMode = ref('active') // 'active' or 'all'

export function useDevices() {
  async function fetchEntities(controllerId, domain = null) {
    loading.value = true
    error.value = null
    selectedController.value = controllerId
    selectedDomain.value = domain

    try {
      const url = domain
        ? `/api/v1/apps/command_center/controllers/${controllerId}/entities?domain=${domain}`
        : `/api/v1/apps/command_center/controllers/${controllerId}/entities`
      entities.value = await apiJson(url)
    } catch (err) {
      error.value = err.message
      entities.value = []
    } finally {
      loading.value = false
    }
  }

  function setDomain(domain) {
    selectedDomain.value = domain
    if (selectedController.value) {
      fetchEntities(selectedController.value, domain)
    }
  }

  function setViewMode(mode) {
    viewMode.value = mode
    // Reset domain filter when switching views
    selectedDomain.value = null
  }

  // Get unique domains from entities
  const domains = computed(() => {
    const domainSet = new Set()
    entities.value.forEach((entity) => {
      domainSet.add(entity.domain)
    })
    return Array.from(domainSet).sort()
  })

  // Active entities - healthy ones (not unavailable/unknown, updated within 5 minutes)
  const activeEntities = computed(() => {
    const now = new Date()
    return entities.value.filter((entity) => {
      const state = entity.state.toLowerCase()
      // Exclude unavailable or unknown states
      if (state === 'unavailable' || state === 'unknown') {
        return false
      }
      // Only include entities updated within 5 minutes (health-good)
      const lastUpdated = new Date(entity.last_updated)
      const diffMinutes = (now - lastUpdated) / 1000 / 60
      return diffMinutes < 5
    })
  })

  // Get unique domains from active entities only
  const activeDomains = computed(() => {
    const domainSet = new Set()
    activeEntities.value.forEach((entity) => {
      domainSet.add(entity.domain)
    })
    return Array.from(domainSet).sort()
  })

  // Filtered entities based on view mode and selected domain
  const filteredEntities = computed(() => {
    const baseEntities = viewMode.value === 'active' ? activeEntities.value : entities.value

    if (!selectedDomain.value) {
      return baseEntities
    }
    return baseEntities.filter((entity) => entity.domain === selectedDomain.value)
  })

  // Current domains based on view mode
  const currentDomains = computed(() => {
    return viewMode.value === 'active' ? activeDomains.value : domains.value
  })

  return {
    entities,
    loading,
    error,
    selectedController,
    selectedDomain,
    viewMode,
    fetchEntities,
    setDomain,
    setViewMode,
    domains,
    activeDomains,
    activeEntities,
    filteredEntities,
    currentDomains,
  }
}
