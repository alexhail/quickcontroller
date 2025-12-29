<script setup>
import { ref, onMounted } from 'vue'
import { apiJson } from '../../../core/api/client.js'
import AppNavigation from '../components/AppNavigation.vue'

const users = ref([])
const loading = ref(true)
const error = ref(null)
const selectedUserId = ref(null)
const userPermissions = ref({})
const loadingPermissions = ref(false)

async function fetchUsers() {
  loading.value = true
  error.value = null
  try {
    users.value = await apiJson('/api/v1/apps/command_center/users')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

async function fetchUserPermissions(userId) {
  loadingPermissions.value = true
  try {
    const permissions = await apiJson(`/api/v1/apps/command_center/users/${userId}/app-permissions`)
    userPermissions.value = permissions.reduce((acc, perm) => {
      acc[perm.app_id] = perm.has_access
      return acc
    }, {})
  } catch (err) {
    console.error('Failed to load permissions:', err)
  } finally {
    loadingPermissions.value = false
  }
}

async function toggleAppAccess(userId, appId, currentAccess) {
  try {
    await apiJson(`/api/v1/apps/command_center/users/${userId}/app-permissions/${appId}`, {
      method: 'PUT',
      body: JSON.stringify({ has_access: !currentAccess })
    })
    // Refresh permissions
    if (selectedUserId.value === userId) {
      await fetchUserPermissions(userId)
    }
  } catch (err) {
    alert(`Failed to update permission: ${err.message}`)
  }
}

function selectUser(userId) {
  selectedUserId.value = userId
  fetchUserPermissions(userId)
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(fetchUsers)
</script>

<template>
  <div class="users-view">
    <AppNavigation />
    <header class="page-header">
      <div class="header-content">
        <div class="header-title">
          <span class="material-symbols-outlined">group</span>
          <div>
            <h1>Users</h1>
            <p class="subtitle">Manage user accounts and app permissions</p>
          </div>
        </div>
      </div>
    </header>

    <div class="users-content">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
      </div>

      <div v-else-if="error" class="error">
        <span class="material-symbols-outlined">error</span>
        <p>{{ error }}</p>
      </div>

      <div v-else-if="users.length === 0" class="empty">
        <span class="material-symbols-outlined">group_off</span>
        <p>No users found</p>
      </div>

      <div v-else class="users-grid">
        <!-- Users List -->
        <section class="panel users-panel">
          <div class="panel-header">
            <h2>All Users</h2>
            <span class="count">{{ users.length }}</span>
          </div>
          <div class="users-list">
            <div
              v-for="user in users"
              :key="user.id"
              :class="['user-item', { active: selectedUserId === user.id }]"
              @click="selectUser(user.id)"
            >
              <div class="user-avatar">
                <span class="material-symbols-outlined">account_circle</span>
              </div>
              <div class="user-info">
                <div class="user-email">{{ user.email }}</div>
                <div class="user-meta">
                  Joined {{ formatDate(user.created_at) }}
                </div>
              </div>
              <span class="material-symbols-outlined arrow">chevron_right</span>
            </div>
          </div>
        </section>

        <!-- User Permissions -->
        <section class="panel permissions-panel">
          <div class="panel-header">
            <h2>App Permissions</h2>
          </div>

          <div v-if="!selectedUserId" class="panel-empty">
            <span class="material-symbols-outlined">person_search</span>
            <p>Select a user to manage permissions</p>
          </div>

          <div v-else-if="loadingPermissions" class="panel-loading">
            <div class="spinner"></div>
          </div>

          <div v-else class="permissions-content">
            <div class="permissions-list">
              <div class="permission-item">
                <div class="permission-info">
                  <span class="material-symbols-outlined">settings</span>
                  <div>
                    <div class="permission-name">Command Center</div>
                    <div class="permission-desc">Core system management</div>
                  </div>
                </div>
                <label class="toggle">
                  <input
                    type="checkbox"
                    :checked="userPermissions['command_center'] !== false"
                    @change="toggleAppAccess(selectedUserId, 'command_center', userPermissions['command_center'] !== false)"
                  />
                  <span class="toggle-slider"></span>
                </label>
              </div>

              <!-- Placeholder for future apps -->
              <div class="info-message">
                <span class="material-symbols-outlined">info</span>
                <p>More apps will appear here as they are registered with the system.</p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '../../../styles/variables' as *;

.users-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  padding: $spacing-lg;
  background: $color-bg-secondary;
  border-bottom: 1px solid $color-border;

  .header-content {
    max-width: 1400px;
    margin: 0 auto;
  }

  .header-title {
    display: flex;
    align-items: center;
    gap: $spacing-md;

    .material-symbols-outlined {
      font-size: 2.5rem;
      color: $color-primary;
    }

    h1 {
      font-size: 1.75rem;
      font-weight: 600;
      margin: 0;
      color: $color-text;
    }

    .subtitle {
      font-size: 0.875rem;
      color: $color-text-secondary;
      margin: $spacing-xs 0 0 0;
    }
  }
}

.users-content {
  flex: 1;
  padding: $spacing-xl;
  overflow: hidden;
  display: flex;
  justify-content: center;
}

.loading,
.error,
.empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: $color-text-secondary;

  .material-symbols-outlined {
    font-size: 3rem;
    margin-bottom: $spacing-md;
    opacity: 0.5;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid $color-bg-tertiary;
    border-top-color: $color-primary;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
}

.error {
  color: $color-error;

  .material-symbols-outlined {
    color: $color-error;
  }
}

.users-grid {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: $spacing-xl;
  max-width: 1400px;
  width: 100%;
  height: 100%;
}

.panel {
  background: $color-bg-secondary;
  border: 1px solid $color-border;
  border-radius: $radius-lg;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: $spacing-lg;
    border-bottom: 1px solid $color-border;
    background: rgba($color-bg-tertiary, 0.3);

    h2 {
      font-size: 1.125rem;
      font-weight: 600;
      margin: 0;
    }

    .count {
      padding: $spacing-xs $spacing-sm;
      background: $color-primary;
      color: white;
      border-radius: $radius-full;
      font-size: 0.75rem;
      font-weight: 700;
      min-width: 1.75rem;
      text-align: center;
    }
  }

  .panel-loading,
  .panel-empty {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: $spacing-2xl;
    color: $color-text-secondary;

    .material-symbols-outlined {
      font-size: 3rem;
      margin-bottom: $spacing-md;
      opacity: 0.5;
    }

    .spinner {
      width: 40px;
      height: 40px;
      border: 3px solid $color-bg-tertiary;
      border-top-color: $color-primary;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
  }
}

.users-list {
  flex: 1;
  overflow-y: auto;
  padding: $spacing-sm;
}

.user-item {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  padding: $spacing-md;
  margin-bottom: $spacing-sm;
  background: $color-bg;
  border: 1px solid $color-border;
  border-radius: $radius-md;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: $color-border-light;
    background: $color-bg-tertiary;
  }

  &.active {
    border-color: $color-primary;
    background: rgba($color-primary, 0.05);
  }

  .user-avatar {
    .material-symbols-outlined {
      font-size: 2.5rem;
      color: $color-text-secondary;
    }
  }

  .user-info {
    flex: 1;
    min-width: 0;

    .user-email {
      font-size: 0.9375rem;
      font-weight: 600;
      color: $color-text;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .user-meta {
      font-size: 0.75rem;
      color: $color-text-muted;
      margin-top: $spacing-xs;
    }
  }

  .arrow {
    color: $color-text-muted;
    font-size: 1.25rem;
  }
}

.permissions-content {
  flex: 1;
  overflow-y: auto;
}

.permissions-list {
  padding: $spacing-md;
}

.permission-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-md;
  margin-bottom: $spacing-sm;
  background: $color-bg;
  border: 1px solid $color-border;
  border-radius: $radius-md;

  .permission-info {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    flex: 1;

    .material-symbols-outlined {
      font-size: 2rem;
      color: $color-primary;
    }

    .permission-name {
      font-size: 0.9375rem;
      font-weight: 600;
      color: $color-text;
    }

    .permission-desc {
      font-size: 0.75rem;
      color: $color-text-muted;
      margin-top: $spacing-xs;
    }
  }
}

.toggle {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;

  input {
    opacity: 0;
    width: 0;
    height: 0;

    &:checked + .toggle-slider {
      background-color: $color-primary;
    }

    &:checked + .toggle-slider:before {
      transform: translateX(22px);
    }
  }

  .toggle-slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: $color-bg-tertiary;
    border: 1px solid $color-border;
    border-radius: 26px;
    transition: 0.3s;

    &:before {
      position: absolute;
      content: '';
      height: 18px;
      width: 18px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      border-radius: 50%;
      transition: 0.3s;
    }
  }
}

.info-message {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-md;
  margin-top: $spacing-lg;
  background: rgba($color-primary, 0.05);
  border: 1px solid rgba($color-primary, 0.2);
  border-radius: $radius-md;
  color: $color-text-secondary;
  font-size: 0.875rem;

  .material-symbols-outlined {
    color: $color-primary;
    font-size: 1.25rem;
  }

  p {
    margin: 0;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
