<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from '../core/composables/useAuth.js'

const router = useRouter()
const { user, logout } = useAuth()

async function handleLogout() {
  await logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="dashboard">
    <header class="header">
      <div class="header-left">
        <h1>Quick Controller</h1>
        <nav class="nav">
          <router-link to="/" class="nav-link active">Dashboard</router-link>
          <router-link to="/controllers" class="nav-link">Controllers</router-link>
          <router-link to="/devices" class="nav-link">Devices</router-link>
        </nav>
      </div>
      <div class="user-menu">
        <span class="email">{{ user?.email }}</span>
        <button class="logout-btn" @click="handleLogout">Logout</button>
      </div>
    </header>

    <main class="main">
      <div class="welcome-card">
        <h2>Welcome to Quick Controller</h2>
        <p>Your IoT meta-analysis platform is ready.</p>
        <p class="user-info">Logged in as: <strong>{{ user?.email }}</strong></p>

        <div class="quick-actions">
          <h3>Quick Actions</h3>
          <router-link to="/controllers" class="action-link">
            <span class="action-icon">🏠</span>
            <div>
              <div class="action-title">Manage Controllers</div>
              <div class="action-desc">Add and configure Home Assistant instances</div>
            </div>
          </router-link>
          <router-link to="/devices" class="action-link">
            <span class="action-icon">📱</span>
            <div>
              <div class="action-title">View Devices</div>
              <div class="action-desc">Browse all entities from your controllers</div>
            </div>
          </router-link>
        </div>
      </div>
    </main>
  </div>
</template>

<style lang="scss" scoped>
@use '../styles/variables' as *;
@use '../styles/mixins' as *;

.dashboard {
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
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

.welcome-card {
  @include card;
  max-width: 500px;
  text-align: center;

  h2 {
    margin-bottom: $spacing-sm;
  }

  p {
    color: $color-text-secondary;
  }

  .user-info {
    margin-top: $spacing-lg;
    padding-top: $spacing-lg;
    border-top: 1px solid $color-border;

    strong {
      color: $color-text;
    }
  }

  .quick-actions {
    margin-top: $spacing-lg;
    padding-top: $spacing-lg;
    border-top: 1px solid $color-border;

    h3 {
      font-size: 0.875rem;
      font-weight: 600;
      text-transform: uppercase;
      color: $color-text-secondary;
      margin-bottom: $spacing-md;
    }
  }

  .action-link {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    padding: $spacing-md;
    border-radius: $radius-sm;
    text-decoration: none;
    color: $color-text;
    background: $color-bg-secondary;
    transition: all 0.2s;

    &:hover {
      background: $color-bg-tertiary;
      transform: translateX(4px);
    }

    .action-icon {
      font-size: 2rem;
    }

    .action-title {
      font-weight: 500;
      margin-bottom: $spacing-xs;
    }

    .action-desc {
      font-size: 0.875rem;
      color: $color-text-secondary;
    }
  }
}
</style>
