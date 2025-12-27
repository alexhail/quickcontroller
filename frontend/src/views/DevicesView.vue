<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../core/composables/useAuth.js'
import { useControllers } from '../core/composables/useControllers.js'
import { useDevices } from '../core/composables/useDevices.js'
import EntityCard from '../components/EntityCard.vue'

const router = useRouter()
const route = useRoute()
const { user, logout } = useAuth()
const { controllers, loading: controllersLoading, fetchControllers } = useControllers()
const {
  entities,
  loading,
  error,
  selectedDomain,
  viewMode,
  fetchEntities,
  setDomain,
  setViewMode,
  activeEntities,
  filteredEntities,
  currentDomains,
} = useDevices()

const currentControllerId = ref(null)

onMounted(async () => {
  await fetchControllers()

  // If we have a controller ID from route params, use it
  if (route.params.controllerId) {
    currentControllerId.value = route.params.controllerId
    fetchEntities(route.params.controllerId)
  } else if (controllers.value.length > 0) {
    // Otherwise, select the first online controller or just the first one
    const onlineController = controllers.value.find((c) => c.connection_status === 'online')
    const firstController = onlineController || controllers.value[0]
    currentControllerId.value = firstController.id
    fetchEntities(firstController.id)
  }
})

async function handleLogout() {
  await logout()
  router.push({ name: 'login' })
}

function handleControllerChange(event) {
  const controllerId = event.target.value
  currentControllerId.value = controllerId
  fetchEntities(controllerId)
}

function handleDomainFilter(domain) {
  setDomain(domain)
}

function handleViewModeChange(mode) {
  setViewMode(mode)
}

const currentController = computed(() => {
  return controllers.value.find((c) => c.id === currentControllerId.value)
})

const onlineControllers = computed(() => {
  return controllers.value.filter((c) => c.connection_status === 'online')
})

const hasOnlineControllers = computed(() => {
  return onlineControllers.value.length > 0
})

// Count entities by domain for current view
function getEntityCountByDomain(domain) {
  const baseEntities = viewMode.value === 'active' ? activeEntities.value : entities.value
  return baseEntities.filter((e) => e.domain === domain).length
}

// Get total count for current view
const totalCount = computed(() => {
  return viewMode.value === 'active' ? activeEntities.value.length : entities.value.length
})
</script>

<template>
  <div class="devices-view">
    <header class="header">
      <div class="header-left">
        <h1>Quick Controller</h1>
        <nav class="nav">
          <router-link to="/" class="nav-link">Dashboard</router-link>
          <router-link to="/controllers" class="nav-link">Controllers</router-link>
          <router-link to="/devices" class="nav-link active">Devices</router-link>
        </nav>
      </div>
      <div class="user-menu">
        <span class="email">{{ user?.email }}</span>
        <button class="logout-btn" @click="handleLogout">Logout</button>
      </div>
    </header>

    <main class="main">
      <div class="page-header">
        <div>
          <h2>Devices</h2>
          <p class="subtitle">Monitor your Home Assistant entities</p>
        </div>
      </div>

      <div v-if="controllersLoading" class="loading">Loading controllers...</div>

      <div v-else-if="!hasOnlineControllers" class="empty-state">
        <div class="empty-icon">🏠</div>
        <h3>No online controllers</h3>
        <p>You need at least one online Home Assistant controller to view devices</p>
        <router-link to="/controllers" class="btn-primary">Go to Controllers</router-link>
      </div>

      <div v-else>
        <!-- Controller Selector -->
        <div v-if="controllers.length > 1" class="controller-selector">
          <label for="controller-select">Controller:</label>
          <select
            id="controller-select"
            :value="currentControllerId"
            @change="handleControllerChange"
            class="controller-select"
          >
            <option
              v-for="controller in onlineControllers"
              :key="controller.id"
              :value="controller.id"
            >
              {{ controller.name }} ({{ controller.url }})
            </option>
          </select>
        </div>

        <!-- View Mode Toggle -->
        <div class="view-mode-toggle">
          <button
            :class="['view-mode-btn', { active: viewMode === 'active' }]"
            @click="handleViewModeChange('active')"
          >
            <span class="view-mode-icon">🟢</span>
            <span class="view-mode-label">Active</span>
            <span class="view-mode-count">{{ activeEntities.length }}</span>
          </button>
          <button
            :class="['view-mode-btn', { active: viewMode === 'all' }]"
            @click="handleViewModeChange('all')"
          >
            <span class="view-mode-icon">📋</span>
            <span class="view-mode-label">All Entities</span>
            <span class="view-mode-count">{{ entities.length }}</span>
          </button>
        </div>

        <!-- Domain Filters -->
        <div v-if="currentDomains.length > 0 && !loading" class="domain-filters">
          <button
            :class="['domain-tab', { active: !selectedDomain }]"
            @click="handleDomainFilter(null)"
          >
            All ({{ totalCount }})
          </button>
          <button
            v-for="domain in currentDomains"
            :key="domain"
            :class="['domain-tab', { active: selectedDomain === domain }]"
            @click="handleDomainFilter(domain)"
          >
            {{ domain }} ({{ getEntityCountByDomain(domain) }})
          </button>
        </div>

        <!-- Loading / Error States -->
        <div v-if="loading" class="loading">Loading devices...</div>

        <div v-else-if="error" class="error-message">Error loading devices: {{ error }}</div>

        <div v-else-if="filteredEntities.length === 0" class="empty-state">
          <div class="empty-icon">{{ viewMode === 'active' ? '✅' : '📭' }}</div>
          <h3>{{ viewMode === 'active' ? 'No active devices' : 'No devices found' }}</h3>
          <p>{{ viewMode === 'active' ? 'All entities are currently unavailable' : 'No entities available from this controller' }}</p>
          <button v-if="viewMode === 'active'" class="btn-secondary" @click="handleViewModeChange('all')">
            View All Entities
          </button>
        </div>

        <!-- Entities Grid -->
        <div v-else class="entities-grid">
          <EntityCard v-for="entity in filteredEntities" :key="entity.entity_id" :entity="entity" />
        </div>
      </div>
    </main>
  </div>
</template>

<style lang="scss" scoped>
@use '../styles/variables' as *;
@use '../styles/mixins' as *;

.devices-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-md $spacing-lg;
  background: $color-bg-secondary;
  border-bottom: 1px solid $color-border;

  h1 {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: $spacing-xs;
  }
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.nav {
  display: flex;
  gap: $spacing-md;
}

.nav-link {
  color: $color-text-secondary;
  text-decoration: none;
  font-size: 0.875rem;
  padding: $spacing-xs $spacing-sm;
  border-radius: $radius-sm;
  transition: all 0.2s;

  &:hover {
    color: $color-text;
    background: $color-bg;
  }

  &.active {
    color: $color-primary;
    font-weight: 500;
  }
}

.user-menu {
  display: flex;
  align-items: center;
  gap: $spacing-md;

  .email {
    color: $color-text-secondary;
    font-size: 0.875rem;
  }

  .logout-btn {
    @include button-secondary;
    font-size: 0.875rem;
    padding: $spacing-xs $spacing-sm;
  }
}

.main {
  flex: 1;
  padding: $spacing-xl;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

.page-header {
  margin-bottom: $spacing-xl;

  h2 {
    font-size: 1.75rem;
    margin-bottom: $spacing-xs;
  }

  .subtitle {
    color: $color-text-secondary;
    font-size: 0.875rem;
  }
}

.controller-selector {
  @include card;
  padding: $spacing-md;
  margin-bottom: $spacing-lg;
  display: flex;
  align-items: center;
  gap: $spacing-md;

  label {
    font-weight: 500;
    color: $color-text-secondary;
  }

  .controller-select {
    flex: 1;
    padding: $spacing-sm $spacing-md;
    border: 1px solid $color-border;
    border-radius: $radius-sm;
    background: $color-bg;
    color: $color-text;
    font-size: 0.875rem;
    cursor: pointer;

    &:focus {
      outline: none;
      border-color: $color-primary;
    }
  }
}

.view-mode-toggle {
  display: flex;
  gap: $spacing-md;
  margin-bottom: $spacing-lg;
}

.view-mode-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
  padding: $spacing-md $spacing-lg;
  border: 2px solid $color-border;
  border-radius: $radius-md;
  background: $color-bg-secondary;
  color: $color-text-secondary;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: $color-bg-tertiary;
    color: $color-text;
  }

  &.active {
    border-color: $color-primary;
    background: rgba($color-primary, 0.1);
    color: $color-text;

    .view-mode-count {
      background: $color-primary;
      color: white;
    }
  }

  .view-mode-icon {
    font-size: 1.25rem;
  }

  .view-mode-label {
    font-weight: 500;
  }

  .view-mode-count {
    padding: $spacing-xs $spacing-sm;
    background: $color-bg-tertiary;
    border-radius: $radius-full;
    font-size: 0.875rem;
    font-weight: 600;
    min-width: 2rem;
    text-align: center;
  }
}

.domain-filters {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-sm;
  margin-bottom: $spacing-lg;
  padding: $spacing-md;
  background: $color-bg-secondary;
  border-radius: $radius-md;
}

.domain-tab {
  padding: $spacing-xs $spacing-md;
  border: 1px solid $color-border;
  border-radius: $radius-sm;
  background: $color-bg;
  color: $color-text-secondary;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  text-transform: capitalize;

  &:hover {
    background: $color-bg-tertiary;
    color: $color-text;
  }

  &.active {
    background: $color-primary;
    color: white;
    border-color: $color-primary;
  }
}

.loading {
  text-align: center;
  padding: $spacing-xl;
  color: $color-text-secondary;
}

.error-message {
  @include card;
  color: $color-error;
  padding: $spacing-md;
  background: rgba($color-error, 0.1);
  border: 1px solid $color-error;
}

.empty-state {
  @include card;
  text-align: center;
  padding: $spacing-xl * 2;
  max-width: 400px;
  margin: 0 auto;

  .empty-icon {
    font-size: 4rem;
    margin-bottom: $spacing-lg;
  }

  h3 {
    margin-bottom: $spacing-sm;
  }

  p {
    color: $color-text-secondary;
    margin-bottom: $spacing-lg;
  }

  .btn-primary {
    @include button-primary;
    text-decoration: none;
    display: inline-block;
  }

  .btn-secondary {
    @include button-secondary;
  }
}

.entities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: $spacing-md;
}
</style>
