<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const navItems = [
  {
    name: 'Dashboard',
    path: '/app/command_center',
    icon: 'dashboard'
  },
  {
    name: 'Controllers',
    path: '/app/command_center/controllers',
    icon: 'hub'
  },
  {
    name: 'Users',
    path: '/app/command_center/users',
    icon: 'group'
  },
  {
    name: 'System',
    path: '/app/command_center/system',
    icon: 'monitor_heart'
  },
  {
    name: 'Audit Logs',
    path: '/app/command_center/audit',
    icon: 'history'
  }
]

const currentPath = computed(() => route.path)

function navigate(path) {
  router.push(path)
}

function isActive(path) {
  return currentPath.value === path
}
</script>

<template>
  <nav class="app-navigation">
    <button
      v-for="item in navItems"
      :key="item.path"
      :class="['nav-item', { active: isActive(item.path) }]"
      @click="navigate(item.path)"
    >
      <span class="material-symbols-outlined">{{ item.icon }}</span>
      <span class="nav-label">{{ item.name }}</span>
    </button>
  </nav>
</template>

<style lang="scss" scoped>
@use '../../../styles/variables' as *;

.app-navigation {
  display: flex;
  // No gap - items touch directly, padding creates highlight area
  padding: 0;
  background: $color-bg-secondary;
  border-bottom: 1px solid $color-border;
  overflow-x: auto;

  .nav-item {
    display: flex;
    align-items: center;
    gap: $spacing-xs;
    // Compact padding - the padded area is the highlight zone
    // 48px matches sidebar header height for alignment
    padding: $spacing-sm $spacing-md;
    height: 48px;
    background: transparent;
    border: none;
    border-radius: 0;
    color: $color-text-secondary;
    font-size: 0.8125rem;
    font-weight: 500;
    white-space: nowrap;
    cursor: pointer;
    transition: background $transition-fast, color $transition-fast;

    .material-symbols-outlined {
      font-size: 1.125rem;
    }

    &:hover {
      background: $color-bg-tertiary;
      color: $color-text;
    }

    &.active {
      background: rgba($color-primary, 0.15);
      color: $color-primary;

      .material-symbols-outlined {
        color: $color-primary;
      }
    }
  }
}

// Hide scrollbar but keep functionality
.app-navigation {
  scrollbar-width: none;
  -ms-overflow-style: none;

  &::-webkit-scrollbar {
    display: none;
  }
}
</style>
