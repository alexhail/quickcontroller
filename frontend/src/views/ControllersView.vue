<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../core/composables/useAuth.js'
import { useControllers } from '../core/composables/useControllers.js'
import AddControllerModal from '../components/AddControllerModal.vue'

const router = useRouter()
const { user, logout } = useAuth()
const { controllers, loading, error, fetchControllers, deleteController } = useControllers()

const showAddModal = ref(false)
const deletingId = ref(null)

onMounted(() => {
  fetchControllers()
})

async function handleLogout() {
  await logout()
  router.push({ name: 'login' })
}

function openAddModal() {
  showAddModal.value = true
}

function closeAddModal() {
  showAddModal.value = false
}

async function handleControllerAdded() {
  closeAddModal()
  await fetchControllers()
}

async function handleDelete(controller) {
  if (!confirm(`Are you sure you want to delete "${controller.name}"?`)) {
    return
  }

  deletingId.value = controller.id
  try {
    await deleteController(controller.id)
  } catch (err) {
    alert(`Failed to delete controller: ${err.message}`)
  } finally {
    deletingId.value = null
  }
}

function getStatusClass(status) {
  switch (status) {
    case 'online':
      return 'status-online'
    case 'offline':
      return 'status-offline'
    case 'connecting':
      return 'status-connecting'
    case 'error':
      return 'status-error'
    default:
      return ''
  }
}

function formatDateTime(dateString) {
  if (!dateString) return 'Never'
  const date = new Date(dateString)
  return date.toLocaleString()
}
</script>

<template>
  <div class="controllers-view">
    <header class="header">
      <div class="header-left">
        <h1>Quick Controller</h1>
        <nav class="nav">
          <router-link to="/" class="nav-link">Dashboard</router-link>
          <router-link to="/controllers" class="nav-link active">Controllers</router-link>
          <router-link to="/devices" class="nav-link">Devices</router-link>
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
          <h2>Master Controllers</h2>
          <p class="subtitle">Manage your Home Assistant instances</p>
        </div>
        <button class="btn-primary" @click="openAddModal">Add Controller</button>
      </div>

      <div v-if="loading" class="loading">Loading controllers...</div>

      <div v-else-if="error" class="error-message">
        Error loading controllers: {{ error }}
      </div>

      <div v-else-if="controllers.length === 0" class="empty-state">
        <div class="empty-icon">🏠</div>
        <h3>No controllers yet</h3>
        <p>Add your first Home Assistant instance to get started</p>
        <button class="btn-primary" @click="openAddModal">Add Controller</button>
      </div>

      <div v-else class="controllers-grid">
        <div v-for="controller in controllers" :key="controller.id" class="controller-card">
          <div class="card-header">
            <div>
              <h3 class="controller-name">{{ controller.name }}</h3>
              <p class="controller-url">{{ controller.url }}</p>
            </div>
            <span :class="['status-badge', getStatusClass(controller.connection_status)]">
              {{ controller.connection_status }}
            </span>
          </div>

          <div class="card-body">
            <div class="info-row">
              <span class="label">Version:</span>
              <span class="value">{{ controller.ha_version || 'Unknown' }}</span>
            </div>
            <div class="info-row">
              <span class="label">Last Seen:</span>
              <span class="value">{{ formatDateTime(controller.last_seen) }}</span>
            </div>
            <div v-if="controller.last_error" class="info-row error">
              <span class="label">Error:</span>
              <span class="value">{{ controller.last_error }}</span>
            </div>
            <div v-if="controller.discovered_via" class="info-row">
              <span class="label">Discovered Via:</span>
              <span class="value">{{ controller.discovered_via }}</span>
            </div>
          </div>

          <div class="card-footer">
            <router-link
              v-if="controller.connection_status === 'online'"
              :to="`/devices/${controller.id}`"
              class="btn-view-devices"
            >
              View Devices
            </router-link>
            <button
              class="btn-danger"
              :disabled="deletingId === controller.id"
              @click="handleDelete(controller)"
            >
              {{ deletingId === controller.id ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </main>

    <AddControllerModal
      v-if="showAddModal"
      @close="closeAddModal"
      @added="handleControllerAdded"
    />
  </div>
</template>

<style lang="scss" scoped>
@use '../styles/variables' as *;
@use '../styles/mixins' as *;

.controllers-view {
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
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
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

.btn-primary {
  @include button-primary;
}

.btn-danger {
  @include button-secondary;
  color: $color-error;
  border-color: $color-error;

  &:hover:not(:disabled) {
    background: rgba($color-error, 0.1);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
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
}

.controllers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: $spacing-lg;
}

.controller-card {
  @include card;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: $spacing-md;
  padding-bottom: $spacing-md;
  border-bottom: 1px solid $color-border;
}

.controller-name {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: $spacing-xs;
}

.controller-url {
  font-size: 0.875rem;
  color: $color-text-secondary;
  word-break: break-all;
}

.status-badge {
  padding: $spacing-xs $spacing-sm;
  border-radius: $radius-sm;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  white-space: nowrap;
}

.status-online {
  background: rgba($color-success, 0.1);
  color: $color-success;
}

.status-offline {
  background: rgba($color-text-secondary, 0.1);
  color: $color-text-secondary;
}

.status-connecting {
  background: rgba($color-primary, 0.1);
  color: $color-primary;
}

.status-error {
  background: rgba($color-error, 0.1);
  color: $color-error;
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  gap: $spacing-sm;

  .label {
    color: $color-text-secondary;
    font-weight: 500;
  }

  .value {
    text-align: right;
    word-break: break-word;
  }

  &.error {
    .value {
      color: $color-error;
    }
  }
}

.card-footer {
  margin-top: $spacing-md;
  padding-top: $spacing-md;
  border-top: 1px solid $color-border;
  display: flex;
  gap: $spacing-sm;
  justify-content: flex-end;
}

.btn-view-devices {
  @include button-primary;
  text-decoration: none;
  font-size: 0.875rem;
  padding: $spacing-xs $spacing-sm;
}
</style>
