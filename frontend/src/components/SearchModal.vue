<script>
import { useStore } from '@/store'
import SearchResultList from './SearchResultList.vue'
import SearchDetailPanel from './SearchDetailPanel.vue'

export default {
  name: 'SearchModal',
  components: { SearchResultList, SearchDetailPanel },
  props: {
    show: { type: Boolean, default: false },
  },
  emits: ['update:show'],
  data() {
    return {
      store: useStore(),
      query: '', results: [], selectedId: null,
      searched: false, debounceTimer: null,
    }
  },
  computed: {
    selectedItem() {
      if (!this.selectedId) return null
      return this.results.find(eq => eq.id === this.selectedId) || null
    },
  },
  watch: {
    show(val) {
      if (val) {
        document.body.style.overflow = 'hidden'
        this.$nextTick(() => this.$refs.searchInput?.focus())
      } else {
        document.body.style.overflow = ''
        this.reset()
      }
    },
  },
  methods: {
    onInput() {
      clearTimeout(this.debounceTimer)
      if (!this.query.trim()) { this.results = []; this.searched = false; this.selectedId = null; return }
      this.debounceTimer = setTimeout(() => this.search(), 350)
    },
    async search() {
      try {
        const result = await this.store.SearchEquipment({ name: this.query.trim() })
        this.results = Array.isArray(result) ? result : []
        this.searched = true
        this.selectedId = this.results.length > 0 ? this.results[0].id : null
      } catch { this.results = []; this.searched = true; this.selectedId = null }
    },
    selectItem(id) { this.selectedId = id },
    moveSelection(dir) {
      if (!this.results.length) return
      const idx = this.results.findIndex(eq => eq.id === this.selectedId)
      const next = idx + dir
      if (next >= 0 && next < this.results.length) this.selectedId = this.results[next].id
    },
    onEnter() {
      if (this.selectedItem) {
        this.$router.push({ name: 'equipment-detail', params: { id: this.selectedItem.id } })
        this.$emit('update:show', false)
      }
    },
    reset() {
      this.query = ''; this.results = []; this.searched = false
      this.selectedId = null; clearTimeout(this.debounceTimer)
    },
  },
}
</script>

<template>
<div v-if="show" class="search-overlay" @click.self="$emit('update:show', false)">
  <div class="search-dialog">

    <!-- Строка поиска -->
    <div class="search-bar">
      <i class="bi bi-search search-bar-icon"></i>
      <input
        type="text"
        class="search-bar-input"
        placeholder="Поиск оборудования по названию..."
        v-model="query"
        @input="onInput"
        @keydown.down.prevent="moveSelection(1)"
        @keydown.up.prevent="moveSelection(-1)"
        @keydown.enter.prevent="onEnter"
        @keydown.esc="$emit('update:show', false)"
        ref="searchInput"
        autocomplete="off"
      />
      <span v-if="results.length" class="search-bar-count">{{ results.length }} рез.</span>
      <button class="search-bar-close" @click="$emit('update:show', false)">
        <i class="bi bi-x-lg"></i>
      </button>
    </div>

    <!-- Тело -->
    <div class="search-body">

      <!-- Загрузка -->
      <div v-if="store.loading" class="search-state">
        <div class="spinner"></div>
        <span>Поиск...</span>
      </div>

      <!-- Пусто -->
      <div v-else-if="searched && results.length === 0" class="search-state">
        <i class="bi bi-inbox" style="font-size: 28px; color: var(--c-border2);"></i>
        <span>По запросу «{{ query }}» ничего не найдено</span>
      </div>

      <!-- Подсказка -->
      <div v-else-if="!searched" class="search-state">
        <i class="bi bi-search" style="font-size: 24px; color: var(--c-border2);"></i>
        <span>Начните вводить название оборудования</span>
        <div class="search-hint-keys">
          <kbd>↑↓</kbd> навигация &nbsp; <kbd>Enter</kbd> открыть &nbsp; <kbd>Esc</kbd> закрыть
        </div>
      </div>

      <!-- Результаты -->
      <div v-else class="search-results-layout">
        <SearchResultList
          :results="results"
          :selected-id="selectedId"
          @select="selectItem"
        />
        <SearchDetailPanel
          :equipment="selectedItem"
          @close="$emit('update:show', false)"
        />
      </div>

    </div>

  </div>
</div>
</template>

<style scoped>
.search-overlay {
  position: fixed;
  inset: 0;
  z-index: 1055;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 60px 1rem 1rem;
  backdrop-filter: blur(3px);
}

.search-dialog {
  background: var(--c-surface);
  border: 1px solid var(--c-border2);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 900px;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 80px);
}

/* Строка поиска */
.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--c-border);
}
.search-bar-icon { color: var(--c-muted); font-size: 15px; flex-shrink: 0; }
.search-bar-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--c-text);
  font-family: var(--font-main);
  font-size: 15px;
}
.search-bar-input::placeholder { color: var(--c-muted); }
.search-bar-count {
  font-size: 11px;
  color: var(--c-muted);
  font-family: var(--font-mono);
  white-space: nowrap;
}
.search-bar-close {
  background: transparent;
  border: 1px solid var(--c-border);
  border-radius: var(--radius-sm);
  color: var(--c-muted);
  font-size: 12px;
  padding: 4px 8px;
  cursor: pointer;
  transition: all var(--transition);
  flex-shrink: 0;
}
.search-bar-close:hover { color: var(--c-text); border-color: var(--c-border2); }

/* Тело */
.search-body { flex: 1; overflow: hidden; min-height: 380px; }

.search-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  height: 100%;
  min-height: 380px;
  color: var(--c-muted);
  font-size: 13px;
}
.search-hint-keys {
  font-size: 11px;
  color: var(--c-muted);
  margin-top: 6px;
}
.search-hint-keys kbd {
  background: var(--c-surface2);
  border: 1px solid var(--c-border2);
  border-radius: 3px;
  padding: 1px 5px;
  font-size: 10px;
  font-family: var(--font-mono);
}

.search-results-layout {
  display: flex;
  height: 100%;
  overflow: hidden;
}

/* Спиннер */
.spinner {
  width: 20px; height: 20px;
  border: 2px solid var(--c-border2);
  border-top-color: var(--c-accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
