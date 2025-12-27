<script setup>
import { ref, computed } from 'vue'
import { useControllers } from '../core/composables/useControllers.js'

const emit = defineEmits(['close', 'added'])

const { addController, discoverControllers, testConnection } = useControllers()

const step = ref(1)
const method = ref(null) // 'discover' or 'manual'

// Discovery state
const discovering = ref(false)
const discoveredList = ref([])
const selectedDiscovered = ref(null)

// Manual state
const manualUrl = ref('')
const manualName = ref('')

// Common state
const accessToken = ref('')
const testing = ref(false)
const testResult = ref(null)
const saving = ref(false)
const error = ref(null)

const canProceedToStep2 = computed(() => {
  return method.value !== null
})

const canProceedToStep3 = computed(() => {
  if (method.value === 'discover') {
    return selectedDiscovered.value !== null
  } else if (method.value === 'manual') {
    return manualUrl.value.trim() !== '' && manualName.value.trim() !== ''
  }
  return false
})

const canTest = computed(() => {
  return accessToken.value.trim() !== ''
})

const canSave = computed(() => {
  return testResult.value?.success === true
})

function selectMethod(selectedMethod) {
  method.value = selectedMethod
  step.value = 2
}

async function handleDiscover() {
  discovering.value = true
  error.value = null
  try {
    discoveredList.value = await discoverControllers()
    if (discoveredList.value.length === 0) {
      error.value = 'No Home Assistant instances found on the network'
    }
  } catch (err) {
    error.value = `Discovery failed: ${err.message}`
  } finally {
    discovering.value = false
  }
}

function selectDiscovered(discovered) {
  selectedDiscovered.value = discovered
  manualName.value = discovered.name
  manualUrl.value = discovered.url
}

function nextStep() {
  if (step.value === 2 && canProceedToStep3.value) {
    step.value = 3
  }
}

function prevStep() {
  if (step.value > 1) {
    step.value--
    error.value = null
    testResult.value = null
  }
}

async function handleTest() {
  testing.value = true
  error.value = null
  testResult.value = null

  try {
    const result = await testConnection(manualUrl.value, accessToken.value)
    testResult.value = result

    if (!result.success) {
      error.value = result.error
    }
  } catch (err) {
    error.value = `Test failed: ${err.message}`
    testResult.value = { success: false, error: err.message }
  } finally {
    testing.value = false
  }
}

async function handleSave() {
  saving.value = true
  error.value = null

  try {
    const discoveredVia = method.value === 'discover' ? 'mDNS' : 'manual'
    await addController(manualName.value, manualUrl.value, accessToken.value, discoveredVia)
    emit('added')
  } catch (err) {
    error.value = `Failed to add controller: ${err.message}`
  } finally {
    saving.value = false
  }
}

function close() {
  emit('close')
}
</script>

<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal">
      <div class="modal-header">
        <h2>Add Home Assistant Controller</h2>
        <button class="close-btn" @click="close">&times;</button>
      </div>

      <div class="modal-body">
        <!-- Step 1: Choose Method -->
        <div v-if="step === 1" class="step">
          <h3>How would you like to add your controller?</h3>
          <div class="method-grid">
            <button class="method-card" @click="selectMethod('discover')">
              <div class="method-icon">🔍</div>
              <h4>Discover</h4>
              <p>Automatically find Home Assistant instances on your network</p>
            </button>
            <button class="method-card" @click="selectMethod('manual')">
              <div class="method-icon">✏️</div>
              <h4>Manual Entry</h4>
              <p>Enter the URL and details manually</p>
            </button>
          </div>
        </div>

        <!-- Step 2: Discovery or Manual Entry -->
        <div v-if="step === 2" class="step">
          <!-- Discovery -->
          <div v-if="method === 'discover'" class="discovery-section">
            <h3>Discover Home Assistant Instances</h3>
            <p class="hint">Scan your local network for Home Assistant instances</p>

            <button
              class="btn-primary"
              :disabled="discovering"
              @click="handleDiscover"
            >
              {{ discovering ? 'Scanning...' : 'Start Discovery' }}
            </button>

            <div v-if="discoveredList.length > 0" class="discovered-list">
              <h4>Found {{ discoveredList.length }} instance(s)</h4>
              <div
                v-for="(item, index) in discoveredList"
                :key="index"
                :class="['discovered-item', { selected: selectedDiscovered === item }]"
                @click="selectDiscovered(item)"
              >
                <div>
                  <div class="discovered-name">{{ item.name }}</div>
                  <div class="discovered-url">{{ item.url }}</div>
                </div>
                <input
                  type="radio"
                  :checked="selectedDiscovered === item"
                  @click.stop="selectDiscovered(item)"
                />
              </div>
            </div>
          </div>

          <!-- Manual Entry -->
          <div v-if="method === 'manual'" class="manual-section">
            <h3>Enter Controller Details</h3>

            <div class="form-group">
              <label for="name">Name</label>
              <input
                id="name"
                v-model="manualName"
                type="text"
                placeholder="e.g., Home Assistant Main"
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label for="url">URL</label>
              <input
                id="url"
                v-model="manualUrl"
                type="url"
                placeholder="http://homeassistant.local:8123"
                class="form-input"
              />
              <p class="hint">Include the protocol (http:// or https://) and port</p>
            </div>
          </div>
        </div>

        <!-- Step 3: Access Token -->
        <div v-if="step === 3" class="step">
          <h3>Enter Access Token</h3>
          <p class="hint">
            Create a long-lived access token in Home Assistant: Profile → Security → Long-Lived Access Tokens
          </p>

          <div class="form-group">
            <label for="token">Long-Lived Access Token</label>
            <input
              id="token"
              v-model="accessToken"
              type="password"
              placeholder="Enter your Home Assistant access token"
              class="form-input"
            />
          </div>

          <button
            class="btn-secondary"
            :disabled="!canTest || testing"
            @click="handleTest"
          >
            {{ testing ? 'Testing...' : 'Test Connection' }}
          </button>

          <div v-if="testResult" class="test-result">
            <div v-if="testResult.success" class="success">
              <strong>✓ Connection successful!</strong>
              <div v-if="testResult.version">Version: {{ testResult.version }}</div>
            </div>
            <div v-else class="error">
              <strong>✗ Connection failed</strong>
              <div>{{ testResult.error }}</div>
            </div>
          </div>
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </div>

      <div class="modal-footer">
        <button v-if="step > 1" class="btn-secondary" @click="prevStep">Back</button>
        <button v-if="step === 2" class="btn-primary" :disabled="!canProceedToStep3" @click="nextStep">
          Next
        </button>
        <button v-if="step === 3" class="btn-primary" :disabled="!canSave || saving" @click="handleSave">
          {{ saving ? 'Saving...' : 'Save Controller' }}
        </button>
        <button class="btn-secondary" @click="close">Cancel</button>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use '../styles/variables' as *;
@use '../styles/mixins' as *;

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: $spacing-lg;
}

.modal {
  background: $color-bg;
  border-radius: $radius-md;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-lg;
  border-bottom: 1px solid $color-border;

  h2 {
    font-size: 1.25rem;
    font-weight: 600;
  }
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: $color-text-secondary;
  cursor: pointer;
  line-height: 1;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: $radius-sm;
  transition: all 0.2s;

  &:hover {
    background: $color-bg-secondary;
    color: $color-text;
  }
}

.modal-body {
  flex: 1;
  padding: $spacing-lg;
  overflow-y: auto;
}

.step {
  h3 {
    margin-bottom: $spacing-md;
  }

  .hint {
    color: $color-text-secondary;
    font-size: 0.875rem;
    margin-bottom: $spacing-md;
  }
}

.method-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $spacing-md;
}

.method-card {
  @include card;
  border: 2px solid $color-border;
  padding: $spacing-lg;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: $color-bg;

  &:hover {
    border-color: $color-primary;
    transform: translateY(-2px);
  }

  .method-icon {
    font-size: 3rem;
    margin-bottom: $spacing-md;
  }

  h4 {
    margin-bottom: $spacing-sm;
    font-weight: 600;
  }

  p {
    font-size: 0.875rem;
    color: $color-text-secondary;
    margin: 0;
  }
}

.form-group {
  margin-bottom: $spacing-md;

  label {
    display: block;
    margin-bottom: $spacing-xs;
    font-weight: 500;
    font-size: 0.875rem;
  }

  .hint {
    margin-top: $spacing-xs;
    margin-bottom: 0;
  }
}

.form-input {
  @include input;
  width: 100%;
}

.btn-primary {
  @include button-primary;
  margin-bottom: $spacing-md;
}

.btn-secondary {
  @include button-secondary;
}

.discovered-list {
  margin-top: $spacing-lg;

  h4 {
    margin-bottom: $spacing-md;
    font-size: 0.875rem;
    font-weight: 600;
    color: $color-text-secondary;
    text-transform: uppercase;
  }
}

.discovered-item {
  @include card;
  padding: $spacing-md;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  margin-bottom: $spacing-sm;
  border: 2px solid $color-border;
  transition: all 0.2s;

  &:hover {
    border-color: $color-primary;
  }

  &.selected {
    border-color: $color-primary;
    background: rgba($color-primary, 0.05);
  }

  .discovered-name {
    font-weight: 500;
    margin-bottom: $spacing-xs;
  }

  .discovered-url {
    font-size: 0.875rem;
    color: $color-text-secondary;
  }

  input[type='radio'] {
    cursor: pointer;
  }
}

.test-result {
  margin-top: $spacing-md;
  padding: $spacing-md;
  border-radius: $radius-sm;

  .success {
    color: $color-success;
    background: rgba($color-success, 0.1);
    padding: $spacing-md;
    border-radius: $radius-sm;

    strong {
      display: block;
      margin-bottom: $spacing-xs;
    }
  }

  .error {
    color: $color-error;
    background: rgba($color-error, 0.1);
    padding: $spacing-md;
    border-radius: $radius-sm;

    strong {
      display: block;
      margin-bottom: $spacing-xs;
    }
  }
}

.error-message {
  color: $color-error;
  background: rgba($color-error, 0.1);
  padding: $spacing-md;
  border-radius: $radius-sm;
  margin-top: $spacing-md;
  border: 1px solid $color-error;
}

.modal-footer {
  display: flex;
  gap: $spacing-sm;
  justify-content: flex-end;
  padding: $spacing-lg;
  border-top: 1px solid $color-border;

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}
</style>
