<script setup>
import { onMounted, ref, computed } from 'vue'
import { useControllers } from '../../../core/composables/useControllers.js'
import { useDevices } from '../../../core/composables/useDevices.js'
import AddControllerModal from '../../../components/AddControllerModal.vue'
import EntityCard from '../../../components/EntityCard.vue'
import AppNavigation from '../components/AppNavigation.vue'

const { controllers, loading: controllersLoading, fetchControllers, deleteController } = useControllers()
const {
  entities,
  loading: devicesLoading,
  fetchEntities,
  activeEntities,
  activeDomains,
} = useDevices()

const showAddModal = ref(false)
const deletingId = ref(null)
const selectedControllerId = ref(null)
const selectedDomain = ref(null)

onMounted(async () => {
  await fetchControllers()

  // Auto-select first online controller
  const onlineController = controllers.value.find((c) => c.connection_status === 'online')
  if (onlineController) {
    selectedControllerId.value = onlineController.id
    fetchEntities(onlineController.id)
  }
})

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

function selectController(controllerId) {
  selectedControllerId.value = controllerId
  selectedDomain.value = null
  fetchEntities(controllerId)
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

const onlineControllers = computed(() => {
  return controllers.value.filter((c) => c.connection_status === 'online')
})

const offlineControllers = computed(() => {
  return controllers.value.filter((c) => c.connection_status !== 'online')
})

const selectedController = computed(() => {
  return controllers.value.find((c) => c.id === selectedControllerId.value)
})

const filteredEntities = computed(() => {
  if (!selectedDomain.value) {
    return activeEntities.value
  }
  return activeEntities.value.filter((e) => e.domain === selectedDomain.value)
})

function getEntityCountByDomain(domain) {
  return activeEntities.value.filter((e) => e.domain === domain).length
}
</script>

<template>
  <div class="controllers-view">
    <AppNavigation />
    <header class="page-header">
      <div class="header-content">
        <div class="header-title">
          <span class="material-symbols-outlined">hub</span>
          <div>
            <h1>Controllers</h1>
            <p class="subtitle">Manage your Home Assistant instances</p>
          </div>
        </div>
        <button class="add-btn" @click="openAddModal">
          <span class="material-symbols-outlined">add</span>
          Add Controller
        </button>
      </div>
    </header>

    <div class="control-grid">
      <!-- Controllers Panel -->
      <section class="panel controllers-panel">
        <div class="panel-header">
          <div class="panel-title">
            <h2>Master Controllers</h2>
            <span class="count">{{ controllers.length }}</span>
          </div>
        </div>

        <div v-if="controllersLoading" class="panel-loading">
          <div class="spinner"></div>
        </div>

        <div v-else-if="controllers.length === 0" class="panel-empty">
          <span class="material-symbols-outlined">cloud_off</span>
          <p>No controllers configured</p>
          <button class="add-btn-large" @click="openAddModal">
            <span class="material-symbols-outlined">add</span>
            Add Controller
          </button>
        </div>

        <div v-else class="controllers-list">
          <div
            v-for="controller in onlineControllers"
            :key="controller.id"
            :class="['controller-item', { active: selectedControllerId === controller.id }]"
            @click="selectController(controller.id)"
          >
            <div class="controller-info">
              <div class="controller-header">
                <h3>{{ controller.name }}</h3>
                <span :class="['status-dot', getStatusClass(controller.connection_status)]"></span>
              </div>
              <p class="controller-url">{{ controller.url }}</p>
              <div class="controller-meta">
                <span v-if="controller.ha_version" class="meta-item">
                  <span class="material-symbols-outlined">info</span>
                  {{ controller.ha_version }}
                </span>
              </div>
            </div>
            <button
              class="delete-btn"
              :disabled="deletingId === controller.id"
              @click.stop="handleDelete(controller)"
            >
              <span class="material-symbols-outlined">delete</span>
            </button>
          </div>

          <div v-if="offlineControllers.length > 0" class="offline-section">
            <h4 class="section-title">Offline</h4>
            <div
              v-for="controller in offlineControllers"
              :key="controller.id"
              class="controller-item offline"
            >
              <div class="controller-info">
                <div class="controller-header">
                  <h3>{{ controller.name }}</h3>
                  <span :class="['status-dot', getStatusClass(controller.connection_status)]"></span>
                </div>
                <p class="controller-url">{{ controller.url }}</p>
              </div>
              <button
                class="delete-btn"
                :disabled="deletingId === controller.id"
                @click.stop="handleDelete(controller)"
              >
                <span class="material-symbols-outlined">delete</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Entities Panel -->
      <section class="panel entities-panel">
        <div class="panel-header">
          <div class="panel-title">
            <h2>Active Entities</h2>
            <span class="count">{{ activeEntities.length }}</span>
          </div>
          <div v-if="selectedController" class="controller-badge">
            {{ selectedController.name }}
          </div>
        </div>

        <!-- Domain Filters -->
        <div v-if="activeDomains.length > 0 && !devicesLoading" class="domain-filters">
          <button
            :class="['domain-chip', { active: !selectedDomain }]"
            @click="selectedDomain = null"
          >
            All ({{ activeEntities.length }})
          </button>
          <button
            v-for="domain in activeDomains"
            :key="domain"
            :class="['domain-chip', { active: selectedDomain === domain }]"
            @click="selectedDomain = domain"
          >
            {{ domain }} ({{ getEntityCountByDomain(domain) }})
          </button>
        </div>

        <div v-if="!selectedControllerId" class="panel-empty">
          <span class="material-symbols-outlined">select_all</span>
          <p>Select a controller to view entities</p>
        </div>

        <div v-else-if="devicesLoading" class="panel-loading">
          <div class="spinner"></div>
        </div>

        <div v-else-if="filteredEntities.length === 0" class="panel-empty">
          <span class="material-symbols-outlined">device_unknown</span>
          <p>No active entities found</p>
        </div>

        <div v-else class="entities-grid">
          <EntityCard v-for="entity in filteredEntities" :key="entity.entity_id" :entity="entity" />
        </div>
      </section>
    </div>

    <AddControllerModal
      v-if="showAddModal"
      @close="closeAddModal"
      @added="handleControllerAdded"
    />
  </div>
</template>

<style lang="scss" scoped>
@use '../../../styles/variables' as *;

.controllers-view {
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
    max-width: 1800px;
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

.add-btn {
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

  &:hover {
    background: $color-primary-dark;
    transform: translateY(-1px);
  }
}

.control-grid {
  flex: 1;
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: $spacing-xl;
  max-width: 1800px;
  margin: 0 auto;
  padding: $spacing-xl;
  width: 100%;
  overflow: hidden;
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

    .panel-title {
      display: flex;
      align-items: center;
      gap: $spacing-sm;

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

    .controller-badge {
      padding: $spacing-xs $spacing-md;
      background: rgba($color-primary, 0.1);
      border: 1px solid rgba($color-primary, 0.3);
      border-radius: $radius-md;
      color: $color-primary;
      font-size: 0.75rem;
      font-weight: 600;
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

    p {
      font-size: 0.875rem;
      margin-bottom: $spacing-md;
    }

    .spinner {
      width: 40px;
      height: 40px;
      border: 3px solid $color-bg-tertiary;
      border-top-color: $color-primary;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    .add-btn-large {
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

      &:hover {
        background: $color-primary-dark;
        transform: translateY(-1px);
      }
    }
  }
}

.controllers-panel {
  .controllers-list {
    flex: 1;
    overflow-y: auto;
    padding: $spacing-sm;
  }

  .controller-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
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

    &.offline {
      opacity: 0.6;
      cursor: default;

      &:hover {
        border-color: $color-border;
        background: $color-bg;
      }
    }

    .controller-info {
      flex: 1;
      min-width: 0;

      .controller-header {
        display: flex;
        align-items: center;
        gap: $spacing-sm;
        margin-bottom: $spacing-xs;

        h3 {
          font-size: 0.9375rem;
          font-weight: 600;
          margin: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }

      .controller-url {
        font-size: 0.75rem;
        color: $color-text-muted;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        margin-bottom: $spacing-xs;
      }

      .controller-meta {
        display: flex;
        gap: $spacing-sm;

        .meta-item {
          display: flex;
          align-items: center;
          gap: 2px;
          font-size: 0.75rem;
          color: $color-text-secondary;

          .material-symbols-outlined {
            font-size: 0.875rem;
          }
        }
      }
    }

    .delete-btn {
      padding: $spacing-xs;
      background: transparent;
      border: 1px solid transparent;
      border-radius: $radius-sm;
      color: $color-text-muted;
      cursor: pointer;
      transition: all 0.2s ease;

      .material-symbols-outlined {
        font-size: 1.125rem;
      }

      &:hover:not(:disabled) {
        background: rgba($color-error, 0.1);
        border-color: $color-error;
        color: $color-error;
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }

  .offline-section {
    margin-top: $spacing-lg;
    padding-top: $spacing-lg;
    border-top: 1px solid $color-border;

    .section-title {
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      color: $color-text-muted;
      margin-bottom: $spacing-sm;
      padding: 0 $spacing-md;
      letter-spacing: 0.5px;
    }
  }
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;

  &.status-online {
    background: $color-success;
    box-shadow: 0 0 8px rgba($color-success, 0.5);
  }

  &.status-offline {
    background: $color-text-muted;
  }

  &.status-connecting {
    background: $color-primary;
    animation: pulse 1.5s ease-in-out infinite;
  }

  &.status-error {
    background: $color-error;
  }
}

.entities-panel {
  .domain-filters {
    display: flex;
    flex-wrap: wrap;
    gap: $spacing-xs;
    padding: $spacing-md;
    background: rgba($color-bg, 0.5);
    border-bottom: 1px solid $color-border;
  }

  .domain-chip {
    padding: $spacing-xs $spacing-sm;
    background: $color-bg-tertiary;
    border: 1px solid $color-border;
    border-radius: $radius-full;
    color: $color-text-secondary;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: capitalize;
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      background: $color-bg-elevated;
      color: $color-text;
    }

    &.active {
      background: $color-primary;
      border-color: $color-primary;
      color: white;
    }
  }

  .entities-grid {
    flex: 1;
    overflow-y: auto;
    padding: $spacing-md;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: $spacing-md;
    align-content: start;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
