<script>
import SearchModal from '@/components/SearchModal.vue'
import { useStore } from '@/store'

export default {
  components: { SearchModal },
  data() {
    return {
      store: useStore(),
      searchOpen: false,
    }
  },
  computed: {
    fullName() {
      const u = this.store.currentUser
      if (!u) return ''
      return `${u.last_name} ${u.first_name}`
    },
    login() {
      return this.store.currentUser?.login || ''
    }
  },
  methods: {
    async handleLogout() {
      await this.store.logout()
      this.$router.push('/')
    }
  }
}
</script>

<template>
<header class="wh-header">
  <div class="wh-header-inner">

    <!-- Лого -->
    <div class="wh-header-logo">
      <span class="wh-logo-icon">⬡</span>
      <span class="wh-logo-text">СКЛАД<span class="text-accent">КАТ</span></span>
    </div>

    <!-- Кнопка поиска -->
    <div class="wh-header-search">
      <button class="wh-search-trigger" @click="searchOpen = true">
        <i class="bi bi-search"></i>
        <span>Поиск оборудования</span>
        <kbd>⌘K</kbd>
      </button>
    </div>

    <!-- Пользователь -->
    <div class="wh-header-user">
      <div class="wh-user-info">
        <span class="wh-user-name">{{ fullName }}</span>
        <span class="wh-user-login">{{ login }}</span>
      </div>
      <button
        class="btn-wh-danger"
        style="font-size: 12px; padding: 5px 12px;"
        :disabled="store.loading"
        @click="handleLogout"
      >
        <i class="bi bi-box-arrow-right me-1"></i>Выход
      </button>
    </div>

  </div>

  <SearchModal v-model:show="searchOpen" />
</header>
</template>

<style scoped>
.wh-header {
  background: var(--c-surface);
  border-bottom: 1px solid var(--c-border);
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 100;
}
.wh-header-inner {
  max-width: 100%;
  height: 100%;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 24px;
}

/* Лого */
.wh-header-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.wh-logo-icon {
  font-size: 22px;
  color: var(--c-accent);
  line-height: 1;
}
.wh-logo-text {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--c-text);
}

/* Поиск */
.wh-header-search { flex: 1; }
.wh-search-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--c-surface2);
  border: 1px solid var(--c-border2);
  border-radius: var(--radius);
  color: var(--c-muted);
  font-family: var(--font-main);
  font-size: 13px;
  padding: 7px 14px;
  cursor: pointer;
  max-width: 400px;
  width: 100%;
  transition: all var(--transition);
}
.wh-search-trigger:hover { border-color: var(--c-accent); color: var(--c-text); }
.wh-search-trigger kbd {
  margin-left: auto;
  background: var(--c-border2);
  border-radius: 3px;
  padding: 1px 5px;
  font-size: 10px;
  color: var(--c-muted);
  font-family: var(--font-mono);
}

/* Пользователь */
.wh-header-user {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
}
.wh-user-info {
  display: flex;
  flex-direction: column;
  text-align: right;
}
.wh-user-name  { font-size: 13px; font-weight: 700; color: var(--c-text); }
.wh-user-login { font-size: 11px; color: var(--c-muted); font-family: var(--font-mono); }
</style>
