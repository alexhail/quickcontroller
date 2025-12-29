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

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="command-center-dashboard">
    <AppNavigation />
    <div class="dashboard-content">
      <header class="page-header">
        <h1>Command Center</h1>
        <p class="subtitle">System overview and management</p>
      </header>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="dashboard-grid">
      <!-- System Health -->
      <section class="card">
        <h2>System Health</h2>
        <div v-if="health" class="health-status">
          <div class="status-item">
            <span class="label">Database:</span>
            <span :class="['status', health.database === 'healthy' ? 'healthy' : 'error']">
              {{ health.database }}
            </span>
          </div>
          <div class="status-item">
            <span class="label">Redis:</span>
            <span :class="['status', health.redis === 'healthy' ? 'healthy' : 'error']">
              {{ health.redis }}
            </span>
          </div>
          <div class="status-item">
            <span class="label">Apps:</span>
            <span class="status">{{ health.apps?.length || 0 }} registered</span>
          </div>
        </div>
      </section>

      <!-- System Stats -->
      <section class="card">
        <h2>Statistics</h2>
        <div v-if="stats" class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ stats.users?.total || 0 }}</div>
            <div class="stat-label">Total Users</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.controllers?.total || 0 }}</div>
            <div class="stat-label">Total Controllers</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.controllers?.online || 0 }}</div>
            <div class="stat-label">Online</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.controllers?.offline || 0 }}</div>
            <div class="stat-label">Offline</div>
          </div>
        </div>
      </section>

      <!-- Registered Apps -->
      <section class="card full-width" v-if="health?.apps">
        <h2>Registered Apps</h2>
        <div class="apps-list">
          <div v-for="app in health.apps" :key="app.app_id" class="app-item">
            <span class="material-symbols-outlined">{{ app.icon || 'apps' }}</span>
            <div class="app-details">
              <div class="app-name">{{ app.display_name }}</div>
              <div class="app-id">{{ app.app_id }}</div>
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

.command-center-dashboard {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.dashboard-content {
  flex: 1;
  padding: $spacing-md;
  overflow-y: auto;
}

.page-header {
  margin-bottom: $spacing-md;

  h1 {
    font-size: 1.25rem;
    font-weight: 600;
    color: $color-text;
    margin: 0;
  }

  .subtitle {
    color: $color-text-muted;
    font-size: 0.75rem;
    margin: $spacing-xs 0 0 0;
  }
}

.loading,
.error {
  padding: $spacing-md;
  text-align: center;
  font-size: 0.875rem;
  color: $color-text-muted;
}

.error {
  color: $color-error;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: $spacing-md;
}

.card {
  background: $color-bg-secondary;
  border: 1px solid $color-border;
  border-radius: $radius-md;
  padding: $spacing-sm $spacing-md;

  &.full-width {
    grid-column: 1 / -1;
  }

  h2 {
    font-size: 0.875rem;
    font-weight: 600;
    color: $color-text-secondary;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 0 $spacing-sm 0;
  }
}

.health-status {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;

  .status-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $spacing-xs $spacing-sm;
    background: $color-bg;
    border-radius: $radius-sm;

    .label {
      color: $color-text-secondary;
      font-size: 0.8125rem;
      font-weight: 500;
    }

    .status {
      font-family: monospace;
      font-size: 0.75rem;

      &.healthy {
        color: $color-success;
      }

      &.error {
        color: $color-error;
      }
    }
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $spacing-sm;

  .stat-item {
    text-align: center;
    padding: $spacing-sm;
    background: $color-bg;
    border-radius: $radius-sm;

    .stat-value {
      font-size: 1.5rem;
      font-weight: 700;
      color: $color-primary;
      line-height: 1;
    }

    .stat-label {
      font-size: 0.6875rem;
      color: $color-text-muted;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-top: $spacing-xs;
    }
  }
}

.apps-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;

  .app-item {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
    padding: $spacing-xs $spacing-sm;
    background: $color-bg;
    border-radius: $radius-sm;

    .material-symbols-outlined {
      font-size: 1.25rem;
      color: $color-primary;
    }

    .app-details {
      flex: 1;

      .app-name {
        font-weight: 500;
        font-size: 0.875rem;
        color: $color-text;
      }

      .app-id {
        font-size: 0.6875rem;
        color: $color-text-muted;
        font-family: monospace;
      }
    }
  }
}
</style>
