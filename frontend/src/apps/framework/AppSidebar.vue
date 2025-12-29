<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useApps } from './useApps.js'

const router = useRouter()
const { accessibleApps, currentAppId } = useApps()

const expanded = ref(false)

function toggleSidebar() {
  expanded.value = !expanded.value
}

function navigateToApp(app) {
  if (app.routes && app.routes.length > 0) {
    router.push(app.routes[0].path)
  }
}

function isActiveApp(appId) {
  return currentAppId.value === appId
}
</script>

<template>
  <aside :class="['app-sidebar', { expanded }]">
    <div class="sidebar-content">
      <!-- Header with Toggle -->
      <div class="sidebar-header">
        <!-- Collapsed: Toggle icon acts as logo -->
        <button
          v-if="!expanded"
          class="toggle-btn collapsed-toggle"
          @click="toggleSidebar"
          title="Expand sidebar"
        >
          <span class="material-symbols-outlined">menu</span>
        </button>

        <!-- Expanded: Logo + text + toggle on right -->
        <template v-else>
          <div class="logo-section">
            <img src="/src/assets/logo.png" alt="Quick Controller" class="logo" />
            <span class="logo-text">Quick Controller</span>
          </div>
          <button
            class="toggle-btn expanded-toggle"
            @click="toggleSidebar"
            title="Collapse sidebar"
          >
            <span class="material-symbols-outlined">chevron_left</span>
          </button>
        </template>
      </div>

      <!-- Apps List -->
      <nav class="apps-nav">
        <button
          v-for="app in accessibleApps"
          :key="app.appId"
          :class="['app-item', { active: isActiveApp(app.appId) }]"
          :title="app.displayName"
          @click="navigateToApp(app)"
        >
          <span class="material-symbols-outlined">{{ app.icon }}</span>
          <span v-if="expanded" class="app-name">{{ app.displayName }}</span>
        </button>
      </nav>

      <!-- User Section (Slot) -->
      <div class="user-section">
        <slot name="user"></slot>
      </div>
    </div>
  </aside>
</template>

<style lang="scss" scoped>
@use '../../styles/variables' as *;

.app-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 48px;
  background: $color-bg-secondary;
  border-right: 1px solid $color-border;
  transition: width $transition-normal;
  z-index: 1000;
  overflow: hidden;

  &.expanded {
    width: 220px;
  }

  .sidebar-content {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 0;
  }

  .sidebar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0;
    height: 48px;
    flex-shrink: 0;
  }

  .toggle-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    padding: 0;
    background: transparent;
    border: none;
    border-radius: $radius-md;
    color: $color-text-secondary;
    cursor: pointer;
    transition: all $transition-fast;
    flex-shrink: 0;

    .material-symbols-outlined {
      font-size: 1.5rem;
    }

    &:hover {
      background: $color-bg-tertiary;
      color: $color-text;
    }
  }

  .collapsed-toggle {
    // Centered in 48px width
    width: 48px;
    height: 48px;
    margin: 0;
    border-radius: 0;
  }

  .logo-section {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
    flex: 1;
    min-width: 0;
    padding-left: $spacing-sm;

    .logo {
      width: 28px;
      height: 28px;
      flex-shrink: 0;
    }

    .logo-text {
      font-size: 0.8125rem;
      font-weight: 700;
      color: $color-text;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  .expanded-toggle {
    margin-right: $spacing-xs;
  }

  .apps-nav {
    display: flex;
    flex-direction: column;
    // No gap - icons stack directly
    padding: 0;

    .app-item {
      display: flex;
      align-items: center;
      // Icon centered in 48x48 square when collapsed
      // Padding creates the highlight area
      width: 100%;
      height: 48px;
      padding: 0;
      background: transparent;
      border: none;
      border-radius: 0;
      color: $color-text-secondary;
      cursor: pointer;
      transition: background $transition-fast, color $transition-fast;
      text-align: left;

      .material-symbols-outlined {
        // 48px total width, 24px icon = 12px padding each side
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
      }

      .app-name {
        font-size: 0.875rem;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        padding-right: $spacing-md;
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

  .user-section {
    margin-top: auto;
    flex-shrink: 0;
    padding: 0;
    border-top: 1px solid $color-border;
  }
}

</style>
