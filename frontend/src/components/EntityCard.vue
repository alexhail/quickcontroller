<script setup>
import { computed } from 'vue'

const props = defineProps({
  entity: {
    type: Object,
    required: true,
  },
})

// Domain icons mapping
const domainIcons = {
  light: '💡',
  switch: '🔌',
  sensor: '📊',
  binary_sensor: '⚡',
  climate: '🌡️',
  cover: '🚪',
  media_player: '🎵',
  camera: '📷',
  fan: '🌀',
  lock: '🔒',
  vacuum: '🤖',
  automation: '⚙️',
  script: '📝',
  scene: '🎬',
  person: '👤',
  device_tracker: '📍',
  weather: '🌤️',
  sun: '☀️',
}

const domainIcon = computed(() => {
  return domainIcons[props.entity.domain] || '❓'
})

// State color mapping
const stateColors = {
  on: 'state-on',
  off: 'state-off',
  unavailable: 'state-unavailable',
  unknown: 'state-unknown',
}

const stateClass = computed(() => {
  const state = props.entity.state.toLowerCase()
  return stateColors[state] || 'state-default'
})

// Health indicator based on last_updated
const healthStatus = computed(() => {
  const state = props.entity.state.toLowerCase()

  // Red if unavailable or unknown
  if (state === 'unavailable' || state === 'unknown') {
    return 'health-unavailable'
  }

  const lastUpdated = new Date(props.entity.last_updated)
  const now = new Date()
  const diffMinutes = (now - lastUpdated) / 1000 / 60

  if (diffMinutes < 5) {
    return 'health-good'
  } else if (diffMinutes < 30) {
    return 'health-stale'
  } else {
    return 'health-old'
  }
})

// Format relative time
function formatRelativeTime(dateString) {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMinutes = Math.floor(diffMs / 1000 / 60)
  const diffHours = Math.floor(diffMinutes / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMinutes < 1) {
    return 'just now'
  } else if (diffMinutes < 60) {
    return `${diffMinutes} min ago`
  } else if (diffHours < 24) {
    return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  } else {
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  }
}

const displayName = computed(() => {
  return props.entity.friendly_name || props.entity.entity_id
})
</script>

<template>
  <div class="entity-card">
    <div class="entity-header">
      <div class="entity-icon">{{ domainIcon }}</div>
      <div class="entity-info">
        <div class="entity-name">{{ displayName }}</div>
        <div class="entity-id">{{ entity.entity_id }}</div>
      </div>
      <div :class="['health-indicator', healthStatus]" :title="healthStatus"></div>
    </div>

    <div class="entity-body">
      <div class="entity-state">
        <span :class="['state-badge', stateClass]">{{ entity.state }}</span>
      </div>
      <div class="entity-time">
        <span class="time-label">Updated:</span>
        <span class="time-value">{{ formatRelativeTime(entity.last_updated) }}</span>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '../styles/variables' as *;
@use '../styles/mixins' as *;

.entity-card {
  @include card;
  padding: $spacing-md;
  transition: all 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}

.entity-header {
  display: flex;
  align-items: flex-start;
  gap: $spacing-sm;
  margin-bottom: $spacing-sm;
}

.entity-icon {
  font-size: 2rem;
  line-height: 1;
}

.entity-info {
  flex: 1;
  min-width: 0;
}

.entity-name {
  font-weight: 600;
  font-size: 0.875rem;
  margin-bottom: calc($spacing-xs / 2);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.entity-id {
  font-size: 0.75rem;
  color: $color-text-secondary;
  font-family: monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.health-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;

  &.health-good {
    background: $color-success;
  }

  &.health-stale {
    background: #f59e0b;
  }

  &.health-old,
  &.health-unavailable {
    background: $color-error;
  }
}

.entity-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: $spacing-sm;
  padding-top: $spacing-sm;
  border-top: 1px solid $color-border;
}

.entity-state {
  .state-badge {
    display: inline-block;
    padding: calc($spacing-xs / 2) $spacing-sm;
    border-radius: $radius-sm;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: capitalize;
  }

  .state-on {
    background: rgba($color-success, 0.1);
    color: $color-success;
  }

  .state-off {
    background: rgba($color-text-secondary, 0.1);
    color: $color-text-secondary;
  }

  .state-unavailable,
  .state-unknown {
    background: rgba($color-error, 0.1);
    color: $color-error;
  }

  .state-default {
    background: rgba($color-primary, 0.1);
    color: $color-primary;
  }
}

.entity-time {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  font-size: 0.75rem;

  .time-label {
    color: $color-text-secondary;
    margin-bottom: 2px;
  }

  .time-value {
    color: $color-text;
  }
}
</style>
