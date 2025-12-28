<script setup>
import { useAuth } from '../core/composables/useAuth.js'

const { loading } = useAuth()
</script>

<template>
  <div v-if="loading" class="loading">
    <div class="spinner"></div>
  </div>
  <slot v-else />
</template>

<style lang="scss" scoped>
@use '../styles/variables' as *;

.loading {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $color-bg;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid $color-bg-tertiary;
  border-top-color: $color-primary;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
