<script setup>
import { ref, onMounted, computed } from 'vue'
import { apiJson } from '../../../core/api/client.js'
import AppNavigation from '../components/AppNavigation.vue'

const logs = ref([])
const loading = ref(true)
const error = ref(null)
const currentPage = ref(1)
const pageSize = ref(50)
const totalLogs = ref(0)

async function fetchLogs() {
  loading.value = true
  error.value = null
  try {
    const offset = (currentPage.value - 1) * pageSize.value
    const data = await apiJson(
      `/api/v1/apps/command_center/audit?limit=${pageSize.value}&offset=${offset}`
    )
    logs.value = data
    // Since we don't have a total count endpoint, estimate based on results
    if (data.length < pageSize.value) {
      totalLogs.value = offset + data.length
    } else {
      totalLogs.value = offset + data.length + 1 // At least one more page
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

function getActionIcon(action) {
  const iconMap = {
    'create': 'add_circle',
    'update': 'edit',
    'delete': 'delete',
    'login': 'login',
    'logout': 'logout',
    'grant_permission': 'key',
    'revoke_permission': 'key_off',
  }
  return iconMap[action] || 'description'
}

function getActionColor(action) {
  const colorMap = {
    'create': 'success',
    'update': 'primary',
    'delete': 'error',
    'login': 'success',
    'logout': 'secondary',
    'grant_permission': 'primary',
    'revoke_permission': 'warning',
  }
  return colorMap[action] || 'default'
}

function nextPage() {
  if (hasNextPage.value) {
    currentPage.value++
    fetchLogs()
  }
}

function previousPage() {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchLogs()
  }
}

const hasNextPage = computed(() => {
  return logs.value.length === pageSize.value
})

const hasPreviousPage = computed(() => {
  return currentPage.value > 1
})

onMounted(fetchLogs)
</script>

<template>
  <div class="audit-view">
    <AppNavigation />
    <header class="page-header">
      <div class="header-content">
        <div class="header-title">
          <span class="material-symbols-outlined">history</span>
          <div>
            <h1>Audit Logs</h1>
            <p class="subtitle">Track system events and user activities</p>
          </div>
        </div>
        <button class="refresh-btn" @click="fetchLogs" :disabled="loading">
          <span class="material-symbols-outlined">refresh</span>
          Refresh
        </button>
      </div>
    </header>

    <div class="audit-content">
      <div v-if="loading && logs.length === 0" class="loading">
        <div class="spinner"></div>
      </div>

      <div v-else-if="error" class="error">
        <span class="material-symbols-outlined">error</span>
        <p>{{ error }}</p>
      </div>

      <div v-else-if="logs.length === 0" class="empty">
        <span class="material-symbols-outlined">receipt_long</span>
        <p>No audit logs found</p>
      </div>

      <div v-else class="logs-container">
        <div class="logs-table-wrapper">
          <table class="logs-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>User</th>
                <th>Action</th>
                <th>Resource</th>
                <th>IP Address</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in logs" :key="log.id" class="log-row">
                <td class="time-cell">
                  {{ formatDate(log.created_at) }}
                </td>
                <td class="user-cell">
                  <div class="user-info">
                    <span class="material-symbols-outlined">account_circle</span>
                    <span>{{ log.user_email || 'System' }}</span>
                  </div>
                </td>
                <td class="action-cell">
                  <div :class="['action-badge', getActionColor(log.action)]">
                    <span class="material-symbols-outlined">{{ getActionIcon(log.action) }}</span>
                    <span>{{ log.action }}</span>
                  </div>
                </td>
                <td class="resource-cell">
                  <div class="resource-info">
                    <div class="resource-type">{{ log.resource_type || 'N/A' }}</div>
                    <div v-if="log.resource_id" class="resource-id">{{ log.resource_id }}</div>
                  </div>
                </td>
                <td class="ip-cell">
                  <code>{{ log.ip_address || 'N/A' }}</code>
                </td>
                <td class="details-cell">
                  <div v-if="log.details" class="details-content">
                    <code>{{ JSON.stringify(log.details) }}</code>
                  </div>
                  <span v-else class="no-details">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="pagination">
          <button
            class="pagination-btn"
            @click="previousPage"
            :disabled="!hasPreviousPage || loading"
          >
            <span class="material-symbols-outlined">chevron_left</span>
            Previous
          </button>
          <span class="page-info">Page {{ currentPage }}</span>
          <button
            class="pagination-btn"
            @click="nextPage"
            :disabled="!hasNextPage || loading"
          >
            Next
            <span class="material-symbols-outlined">chevron_right</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '../../../styles/variables' as *;

.audit-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  padding: $spacing-lg;
  background: $color-bg-secondary;
  border-bottom: 1px solid $color-border;

  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1600px;
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

  .refresh-btn {
    display: flex;
    align-items: center;
    gap: $spacing-xs;
    padding: $spacing-sm $spacing-lg;
    background: $color-primary;
    border: none;
    border-radius: $radius-md;
    color: white;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;

    .material-symbols-outlined {
      font-size: 1.25rem;
    }

    &:hover:not(:disabled) {
      background: $color-primary-dark;
      transform: translateY(-1px);
    }

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }
}

.audit-content {
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

.logs-container {
  width: 100%;
  max-width: 1600px;
  display: flex;
  flex-direction: column;
  gap: $spacing-lg;
  overflow: hidden;
}

.logs-table-wrapper {
  flex: 1;
  overflow: auto;
  background: $color-bg-secondary;
  border: 1px solid $color-border;
  border-radius: $radius-lg;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;

  thead {
    position: sticky;
    top: 0;
    background: $color-bg-tertiary;
    z-index: 1;

    tr {
      border-bottom: 2px solid $color-border;
    }

    th {
      padding: $spacing-md;
      text-align: left;
      font-size: 0.75rem;
      font-weight: 700;
      color: $color-text-secondary;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      white-space: nowrap;
    }
  }

  tbody {
    .log-row {
      border-bottom: 1px solid $color-border;
      transition: background 0.2s ease;

      &:hover {
        background: rgba($color-bg-tertiary, 0.5);
      }

      td {
        padding: $spacing-md;
        vertical-align: top;
      }
    }
  }
}

.time-cell {
  font-size: 0.875rem;
  color: $color-text-secondary;
  white-space: nowrap;
  font-family: monospace;
}

.user-cell {
  .user-info {
    display: flex;
    align-items: center;
    gap: $spacing-xs;
    font-size: 0.875rem;
    color: $color-text;

    .material-symbols-outlined {
      font-size: 1.25rem;
      color: $color-text-secondary;
    }
  }
}

.action-cell {
  .action-badge {
    display: inline-flex;
    align-items: center;
    gap: $spacing-xs;
    padding: $spacing-xs $spacing-sm;
    border-radius: $radius-full;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    white-space: nowrap;

    .material-symbols-outlined {
      font-size: 1rem;
    }

    &.success {
      background: rgba($color-success, 0.1);
      color: $color-success;
      border: 1px solid rgba($color-success, 0.3);
    }

    &.error {
      background: rgba($color-error, 0.1);
      color: $color-error;
      border: 1px solid rgba($color-error, 0.3);
    }

    &.warning {
      background: rgba(#ff9800, 0.1);
      color: #ff9800;
      border: 1px solid rgba(#ff9800, 0.3);
    }

    &.primary {
      background: rgba($color-primary, 0.1);
      color: $color-primary;
      border: 1px solid rgba($color-primary, 0.3);
    }

    &.secondary {
      background: rgba($color-text-muted, 0.1);
      color: $color-text-muted;
      border: 1px solid rgba($color-text-muted, 0.3);
    }

    &.default {
      background: $color-bg-tertiary;
      color: $color-text-secondary;
      border: 1px solid $color-border;
    }
  }
}

.resource-cell {
  .resource-info {
    font-size: 0.875rem;

    .resource-type {
      font-weight: 600;
      color: $color-text;
    }

    .resource-id {
      font-size: 0.75rem;
      color: $color-text-muted;
      font-family: monospace;
      margin-top: $spacing-xs;
    }
  }
}

.ip-cell {
  code {
    font-size: 0.75rem;
    color: $color-text-secondary;
    background: $color-bg-tertiary;
    padding: $spacing-xs $spacing-sm;
    border-radius: $radius-sm;
    font-family: monospace;
  }
}

.details-cell {
  max-width: 300px;

  .details-content {
    code {
      font-size: 0.75rem;
      color: $color-text-secondary;
      background: $color-bg-tertiary;
      padding: $spacing-xs $spacing-sm;
      border-radius: $radius-sm;
      font-family: monospace;
      word-break: break-all;
      display: block;
    }
  }

  .no-details {
    color: $color-text-muted;
    font-size: 0.875rem;
  }
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-lg;
  padding: $spacing-md;
  background: $color-bg-secondary;
  border: 1px solid $color-border;
  border-radius: $radius-lg;

  .pagination-btn {
    display: flex;
    align-items: center;
    gap: $spacing-xs;
    padding: $spacing-sm $spacing-md;
    background: $color-bg;
    border: 1px solid $color-border;
    border-radius: $radius-md;
    color: $color-text;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;

    .material-symbols-outlined {
      font-size: 1.125rem;
    }

    &:hover:not(:disabled) {
      background: $color-bg-tertiary;
      border-color: $color-border-light;
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  .page-info {
    font-size: 0.875rem;
    font-weight: 600;
    color: $color-text-secondary;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
