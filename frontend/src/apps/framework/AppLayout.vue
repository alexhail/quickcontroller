<script setup>
import { onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../../core/composables/useAuth.js'
import { useApps } from './useApps.js'
import AppSidebar from './AppSidebar.vue'

const router = useRouter()
const route = useRoute()
const { user, logout } = useAuth()
const { fetchPermissions, setCurrentApp } = useApps()

onMounted(async () => {
  await fetchPermissions()
})

// Update currentApp based on route
watch(() => route.meta.appId, (appId) => {
  if (appId) {
    setCurrentApp(appId)
  }
}, { immediate: true })

async function handleLogout() {
  await logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="app-layout">
    <AppSidebar>
      <template #user>
        <div class="user-info">
          <div class="user-avatar">
            <span class="material-symbols-outlined">account_circle</span>
          </div>
          <div class="user-details">
            <div class="user-email">{{ user?.email }}</div>
            <button class="logout-btn" @click="handleLogout" title="Logout">
              <span class="material-symbols-outlined">logout</span>
            </button>
          </div>
        </div>
      </template>
    </AppSidebar>

    <main class="app-content">
      <router-view />
    </main>
  </div>
</template>

<style lang="scss" scoped>
@use '../../styles/variables' as *;

.app-layout {
  display: flex;
  min-height: 100vh;
  background: $color-bg;
}

.app-content {
  margin-left: 48px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.user-info {
  display: flex;
  align-items: center;
  height: 48px;
  padding: 0;
  cursor: pointer;
  transition: background $transition-fast;

  .user-avatar {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    .material-symbols-outlined {
      font-size: 1.5rem;
      color: $color-text-secondary;
    }
  }

  .user-details {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
    flex: 1;
    min-width: 0;
    padding-right: $spacing-sm;
    opacity: 0;
    transition: opacity $transition-fast;

    .user-email {
      font-size: 0.75rem;
      color: $color-text-secondary;
      font-weight: 500;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      flex: 1;
    }

    .logout-btn {
      flex-shrink: 0;
      width: 28px;
      height: 28px;
      padding: 0;
      background: transparent;
      border: none;
      border-radius: $radius-sm;
      color: $color-text-muted;
      cursor: pointer;
      transition: all $transition-fast;
      display: flex;
      align-items: center;
      justify-content: center;

      .material-symbols-outlined {
        font-size: 1.125rem;
      }

      &:hover {
        background: rgba($color-error, 0.15);
        color: $color-error;
      }
    }
  }

  &:hover {
    background: $color-bg-tertiary;
  }
}

// Show user details when sidebar is expanded
:deep(.app-sidebar.expanded) .user-details {
  opacity: 1;
}
</style>
