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
    router.push('/')
  } catch (e) {
    error.value = e.message
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-container">
      <div class="logo-section">
        <img src="/src/assets/logo.png" alt="Quick Controller" class="logo" />
        <h1 class="brand-title">Quick Controller</h1>
        <p class="brand-subtitle">IoT Visualization and Operations Platform</p>
      </div>

      <div class="register-card">
        <h2 class="register-title">Create Account</h2>
        <p class="register-subtitle">Get started with Quick Controller</p>

        <form @submit.prevent="handleSubmit" class="register-form">
          <div class="form-group">
            <label for="email">
              <span class="material-symbols-outlined">mail</span>
              Email Address
            </label>
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
            <label for="password">
              <span class="material-symbols-outlined">lock</span>
              Password
            </label>
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
            <label for="confirmPassword">
              <span class="material-symbols-outlined">lock</span>
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              v-model="confirmPassword"
              type="password"
              placeholder="Confirm your password"
              required
              autocomplete="new-password"
            />
          </div>

          <div v-if="error" class="error-message">
            <span class="material-symbols-outlined">error</span>
            {{ error }}
          </div>

          <button type="submit" class="submit-btn" :disabled="submitting">
            <span v-if="!submitting">Create Account</span>
            <span v-else>Creating account...</span>
            <span class="material-symbols-outlined">arrow_forward</span>
          </button>
        </form>

        <div class="footer">
          <p>
            Already have an account?
            <router-link to="/login" class="login-link">Sign in</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '../styles/variables' as *;

.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $spacing-xl;
  background: $color-bg;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 20% 30%, rgba($color-primary, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 80% 70%, rgba($color-primary-dark, 0.06) 0%, transparent 50%);
    pointer-events: none;
  }
}

.register-container {
  display: flex;
  align-items: center;
  gap: $spacing-2xl;
  position: relative;
  z-index: 1;
}

.logo-section {
  text-align: center;
  flex-shrink: 0;
  min-width: 280px;

  .logo {
    width: 180px;
    height: 180px;
    margin-bottom: $spacing-md;
    filter: drop-shadow(0 4px 16px rgba($color-primary, 0.3));
  }

  .brand-title {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: $spacing-xs;
    background: linear-gradient(
      90deg,
      $color-text 0%,
      $color-primary-light 25%,
      $color-text 50%,
      $color-primary-light 75%,
      $color-text 100%
    );
    background-size: 200% 100%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient-shift 8s ease-in-out infinite;
  }

  .brand-subtitle {
    font-size: 0.8125rem;
    color: $color-text-secondary;
    font-weight: 500;
    letter-spacing: 0.5px;
    white-space: nowrap;
  }
}

@keyframes gradient-shift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.register-card {
  width: 280px;

  .register-title {
    font-size: 1.125rem;
    font-weight: 600;
    margin-bottom: $spacing-xs;
    color: $color-text;
  }

  .register-subtitle {
    font-size: 0.75rem;
    color: $color-text-secondary;
    margin-bottom: $spacing-lg;
  }
}

.register-form {
  .form-group {
    margin-bottom: $spacing-md;

    label {
      display: flex;
      align-items: center;
      gap: $spacing-xs;
      margin-bottom: $spacing-xs;
      font-size: 0.8125rem;
      font-weight: 500;
      color: $color-text-secondary;

      .material-symbols-outlined {
        font-size: 1rem;
      }
    }

    input {
      width: 100%;
      padding: $spacing-sm $spacing-md;
      background: rgba($color-bg, 0.8);
      border: 1px solid rgba($color-border, 0.5);
      border-radius: $radius-md;
      color: $color-text;
      font-size: 0.875rem;
      transition: all 0.2s ease;

      &::placeholder {
        color: $color-text-muted;
      }

      // Prevent autofill from changing background color
      &:-webkit-autofill,
      &:-webkit-autofill:hover,
      &:-webkit-autofill:focus,
      &:-webkit-autofill:active {
        -webkit-box-shadow: 0 0 0 1000px $color-bg inset !important;
        -webkit-text-fill-color: $color-text !important;
        caret-color: $color-text;
        transition: background-color 5000s ease-in-out 0s;
      }

      &:focus {
        outline: none;
        border-color: $color-primary;
        background: $color-bg;
        box-shadow: 0 0 0 3px rgba($color-primary, 0.1);
      }

      &:hover:not(:focus) {
        border-color: rgba($color-border-light, 0.8);
      }
    }
  }
}

.error-message {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-sm $spacing-md;
  background: rgba($color-error, 0.1);
  border: 1px solid rgba($color-error, 0.3);
  border-radius: $radius-md;
  color: $color-error;
  font-size: 0.8125rem;
  margin-bottom: $spacing-md;

  .material-symbols-outlined {
    font-size: 1.125rem;
  }
}

.submit-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
  padding: $spacing-sm $spacing-lg;
  background: linear-gradient(135deg, $color-primary 0%, $color-primary-dark 100%);
  border: none;
  border-radius: $radius-md;
  color: white;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba($color-primary, 0.3);

  .material-symbols-outlined {
    font-size: 1.125rem;
  }

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba($color-primary, 0.4);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
}

.footer {
  margin-top: $spacing-lg;
  text-align: center;

  p {
    font-size: 0.875rem;
    color: $color-text-secondary;
  }

  .login-link {
    color: $color-primary;
    font-weight: 600;
    text-decoration: none;
    transition: color 0.2s ease;

    &:hover {
      color: $color-primary-light;
      text-decoration: underline;
    }
  }
}
</style>
