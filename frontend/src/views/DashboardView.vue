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
      <h1>Quick Controller</h1>
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
}
</style>
