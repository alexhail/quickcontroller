<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../core/composables/useAuth.js'

const router = useRouter()
const { register, login } = useAuth()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const submitting = ref(false)

async function handleSubmit() {
  error.value = ''

  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  if (password.value.length < 8) {
    error.value = 'Password must be at least 8 characters'
    return
  }

  submitting.value = true

  try {
    await register(email.value, password.value)
    await login(email.value, password.value)
    router.push({ name: 'dashboard' })
  } catch (e) {
    error.value = e.message
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>Create Account</h1>
      <p class="subtitle">Get started with Quick Controller</p>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="you@example.com"
            required
            autocomplete="email"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="At least 8 characters"
            required
            autocomplete="new-password"
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="Confirm your password"
            required
            autocomplete="new-password"
          />
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" :disabled="submitting">
          {{ submitting ? 'Creating account...' : 'Create account' }}
        </button>
      </form>

      <p class="footer">
        Already have an account?
        <router-link to="/login">Sign in</router-link>
      </p>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '../styles/variables' as *;
@use '../styles/mixins' as *;

.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $spacing-md;
}

.auth-card {
  @include card;
  width: 100%;
  max-width: 400px;

  h1 {
    font-size: 1.5rem;
    margin-bottom: $spacing-xs;
  }

  .subtitle {
    color: $color-text-secondary;
    margin-bottom: $spacing-lg;
  }
}

.form-group {
  margin-bottom: $spacing-md;

  label {
    display: block;
    margin-bottom: $spacing-xs;
    font-size: 0.875rem;
    color: $color-text-secondary;
  }

  input {
    @include input-base;
  }
}

.error {
  color: $color-error;
  font-size: 0.875rem;
  margin-bottom: $spacing-md;
}

button[type='submit'] {
  @include button-primary;
  width: 100%;
  padding: $spacing-md;
}

.footer {
  margin-top: $spacing-lg;
  text-align: center;
  color: $color-text-secondary;
  font-size: 0.875rem;
}
</style>
