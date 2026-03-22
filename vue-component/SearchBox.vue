<script setup lang="ts">
interface Props {
  modelValue?: string
  placeholder?: string
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '搜索...',
  loading: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'search': [value: string]
}>()

const handleInput = (e: Event) => {
  const value = (e.target as HTMLInputElement).value
  emit('update:modelValue', value)
}

const handleSearch = () => {
  emit('search', props.modelValue)
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter') {
    handleSearch()
  }
}

const handleClear = () => {
  emit('update:modelValue', '')
  emit('search', '')
}
</script>

<template>
  <div class="search-box">
    <div class="search-input-wrapper">
      <svg class="search-icon" viewBox="0 0 24 24" width="16" height="16">
        <path fill="currentColor" d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
      </svg>
      <input
        type="text"
        class="search-input"
        :value="modelValue"
        :placeholder="placeholder"
        @input="handleInput"
        @keydown="handleKeydown"
      />
      <button
        v-if="modelValue"
        class="clear-btn"
        type="button"
        @click="handleClear"
      >
        <svg viewBox="0 0 24 24" width="14" height="14">
          <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
        </svg>
      </button>
    </div>
    <button
      class="search-btn"
      :disabled="loading"
      @click="handleSearch"
    >
      <span v-if="loading" class="loading-spinner" />
      <span v-else>搜索</span>
    </button>
  </div>
</template>

<style scoped>
.search-box {
  display: flex;
  gap: 8px;
  align-items: center;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: #9ca3af;
  pointer-events: none;
}

.search-input {
  width: 100%;
  height: 36px;
  padding: 0 36px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-input::placeholder {
  color: #9ca3af;
}

.clear-btn {
  position: absolute;
  right: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  padding: 0;
  border: none;
  background: #e5e7eb;
  border-radius: 50%;
  color: #6b7280;
  cursor: pointer;
  transition: background 0.2s;
}

.clear-btn:hover {
  background: #d1d5db;
}

.search-btn {
  height: 36px;
  padding: 0 16px;
  border: none;
  border-radius: 6px;
  background: #3b82f6;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.search-btn:hover:not(:disabled) {
  background: #2563eb;
}

.search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid #fff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
