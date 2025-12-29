<script setup>
import { ref, onMounted } from 'vue'
import { apiJson } from '../../../core/api/client.js'
import AppNavigation from '../components/AppNavigation.vue'

const health = ref(null)
const stats = ref(null)
const loading = ref(true)
const error = ref(null)

async function loadData() {
  try {
    loading.value = true
    error.value = null
    const [healthData, statsData] = await Promise.all([
      apiJson('/api/v1/apps/command_center/system/health'),
      apiJson('/api/v1/apps/command_center/system/stats')
    ])
    health.value = healthData
    stats.value = statsData
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function getHealthStatus(status) {
  if (status === 'healthy') return 'healthy'
  if (status.startsWith('error:')) return 'error'
  return 'unknown'
}

onMounted(loadData)
</script>

<template>
  <div class="system-view">
    <AppNavigation />
    <header class="page-header">
      <div class="header-content">
        <div class="header-title">
          <span class="material-symbols-outlined">monitor_heart</span>
          <div>
            <h1>System Health</h1>
            <p class="subtitle">Monitor system status and statistics</p>
          </div>
        </div>
        <button class="refresh-btn" @click="loadData" :disabled="loading">
          <span class="material-symbols-outlined">refresh</span>
          Refresh
        </button>
      </div>
    </header>

    <div class="system-content">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
      </div>

      <div v-else-if="error" class="error">
        <span class="material-symbols-outlined">error</span>
        <p>{{ error }}</p>
      </div>

      <div v-else class="dashboard-grid">
        <!-- System Health -->
        <section class="card health-card">
          <div class="card-header">
            <h2>
              <span class="material-symbols-outlined">health_and_safety</span>
              Service Health
            </h2>
          </div>
          <div v-if="health" class="health-status">
            <div class="status-item">
              <div class="status-label">
                <span class="material-symbols-outlined">database</span>
                <span>Database</span>
              </div>
              <span :class="['status-badge', getHealthStatus(health.database)]">
                {{ health.database }}
              </span>
            </div>
            <div class="status-item">
              <div class="status-label">
                <span class="material-symbols-outlined">memory</span>
                <span>Redis Cache</span>
              </div>
              <span :class="['status-badge', getHealthStatus(health.redis)]">
                {{ health.redis }}
              </span>
            </div>
            <div class="status-item">
              <div class="status-label">
                <span class="material-symbols-outlined">apps</span>
                <span>Registered Apps</span>
              </div>
              <span class="status-badge info">
                {{ health.apps?.length || 0 }} apps
              </span>
            </div>
          </div>
        </section>

        <!-- System Stats -->
        <section class="card stats-card">
          <div class="card-header">
            <h2>
              <span class="material-symbols-outlined">bar_chart</span>
              Statistics
            </h2>
          </div>
          <div v-if="stats" class="stats-grid">
            <div class="stat-item">
              <span class="material-symbols-outlined">group</span>
              <div class="stat-value">{{ stats.users?.total || 0 }}</div>
              <div class="stat-label">Total Users</div>
            </div>
            <div class="stat-item">
              <span class="material-symbols-outlined">hub</span>
              <div class="stat-value">{{ stats.controllers?.total || 0 }}</div>
              <div class="stat-label">Total Controllers</div>
            </div>
            <div class="stat-item success">
              <span class="material-symbols-outlined">check_circle</span>
              <div class="stat-value">{{ stats.controllers?.online || 0 }}</div>
              <div class="stat-label">Online</div>
            </div>
            <div class="stat-item error">
              <span class="material-symbols-outlined">cancel</span>
              <div class="stat-value">{{ stats.controllers?.offline || 0 }}</div>
              <div class="stat-label">Offline</div>
            </div>
          </div>
        </section>

        <!-- Registered Apps -->
        <section class="card apps-card" v-if="health?.apps">
          <div class="card-header">
            <h2>
              <span class="material-symbols-outlined">widgets</span>
              Registered Apps
            </h2>
          </div>
          <div class="apps-list">
            <div v-for="app in health.apps" :key="app.app_id" class="app-item">
              <span class="material-symbols-outlined">extension</span>
              <div class="app-details">
                <div class="app-name">{{ app.display_name }}</div>
                <div class="app-id">{{ app.app_id }}</div>
              </div>
              <span class="status-indicator healthy"></span>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '../../../styles/variables' as *;

.system-view {
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

.system-content {
  flex: 1;
  padding: $spacing-xl;
  overflow-y: auto;
  display: flex;
  justify-content: center;
}

.loading,
.error {
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

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: $spacing-lg;
  max-width: 1400px;
  width: 100%;
  align-content: start;
}

.card {
  background: $color-bg-secondary;
  border: 1px solid $color-border;
  border-radius: $radius-lg;
  overflow: hidden;

  &.apps-card {
    grid-column: 1 / -1;
  }

  .card-header {
    padding: $spacing-lg;
    border-bottom: 1px solid $color-border;
    background: rgba($color-bg-tertiary, 0.3);

    h2 {
      display: flex;
      align-items: center;
      gap: $spacing-sm;
      font-size: 1.125rem;
      font-weight: 600;
      color: $color-text;
      margin: 0;

      .material-symbols-outlined {
        font-size: 1.5rem;
        color: $color-primary;
      }
    }
  }
}

.health-status {
  padding: $spacing-md;
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;

  .status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $spacing-md;
    background: $color-bg;
    border: 1px solid $color-border;
    border-radius: $radius-md;

    .status-label {
      display: flex;
      align-items: center;
      gap: $spacing-sm;
      color: $color-text;
      font-weight: 500;

      .material-symbols-outlined {
        font-size: 1.5rem;
        color: $color-text-secondary;
      }
    }

    .status-badge {
      padding: $spacing-xs $spacing-md;
      border-radius: $radius-full;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;

      &.healthy {
        background: rgba($color-success, 0.1);
        color: $color-success;
        border: 1px solid rgba($color-success, 0.3);
      }

      &.error {
        background: rgba($color-error, 0.1);
        color: $color-error;
        border: 1px solid rgba($color-error, 0.3);
      }

      &.unknown {
        background: rgba($color-text-muted, 0.1);
        color: $color-text-muted;
        border: 1px solid rgba($color-text-muted, 0.3);
      }

      &.info {
        background: rgba($color-primary, 0.1);
        color: $color-primary;
        border: 1px solid rgba($color-primary, 0.3);
      }
    }
  }
}

.stats-grid {
  padding: $spacing-md;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $spacing-md;

  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: $spacing-lg;
    background: $color-bg;
    border: 1px solid $color-border;
    border-radius: $radius-md;

    .material-symbols-outlined {
      font-size: 2.5rem;
      color: $color-primary;
      margin-bottom: $spacing-sm;
    }

    .stat-value {
      font-size: 2.5rem;
      font-weight: 700;
      color: $color-text;
      margin-bottom: $spacing-xs;
    }

    .stat-label {
      font-size: 0.875rem;
      color: $color-text-secondary;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      font-weight: 600;
    }

    &.success {
      .material-symbols-outlined {
        color: $color-success;
      }
      .stat-value {
        color: $color-success;
      }
    }

    &.error {
      .material-symbols-outlined {
        color: $color-error;
      }
      .stat-value {
        color: $color-error;
      }
    }
  }
}

.apps-list {
  padding: $spacing-md;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: $spacing-sm;

  .app-item {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    padding: $spacing-md;
    background: $color-bg;
    border: 1px solid $color-border;
    border-radius: $radius-md;
    transition: all 0.2s ease;

    &:hover {
      border-color: $color-border-light;
      background: $color-bg-tertiary;
    }

    .material-symbols-outlined {
      font-size: 2rem;
      color: $color-primary;
    }

    .app-details {
      flex: 1;

      .app-name {
        font-weight: 600;
        color: $color-text;
        margin-bottom: $spacing-xs;
      }

      .app-id {
        font-size: 0.75rem;
        color: $color-text-muted;
        font-family: monospace;
      }
    }

    .status-indicator {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      flex-shrink: 0;

      &.healthy {
        background: $color-success;
        box-shadow: 0 0 8px rgba($color-success, 0.5);
      }
    }
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
