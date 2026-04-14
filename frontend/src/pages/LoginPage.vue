<script>
import { useStore } from '@/store'

export default {
  data() {
    return {
      store: useStore(),
      login:    '',
      password: '',
      error:    '',
    }
  },
  methods: {
    async handleLogin() {
      this.error = ''
      if (!this.login.trim() || !this.password) {
        this.error = 'Введите логин и пароль'
        return
      }
      this.store.userAuth = { login: this.login, password: this.password }
      try {
        await this.store.login()
        const isAdmin = this.store.currentUser?.is_admin
        this.$router.push(isAdmin ? '/admin/catalog' : '/view')
      } catch {
        this.error = this.store.error || 'Неверный логин или пароль'
      }
    }
  }
}
</script>

<template>
  <div class="wh-login-bg">
    <div class="login-wrap">

      <!-- Шапка над карточкой -->
      <div class="login-brand">
        <div class="login-logo">⬡</div>
        <div class="login-company">НАЗВАНИЕ ПРЕДПРИЯТИЯ</div>
        <div class="login-subtitle">Система управления складским каталогом</div>
      </div>

      <!-- Карточка входа -->
      <div class="wh-login-card">
        <div class="login-card-header">
          <span class="login-card-label">Авторизация</span>
        </div>

        <div style="margin-top: 20px;">
          <div class="field-group">
            <label class="wh-label">Логин</label>
            <input
              type="text"
              class="wh-input"
              placeholder="Введите логин"
              v-model="login"
              @keyup.enter="handleLogin"
            />
          </div>

          <div class="field-group">
            <label class="wh-label">Пароль</label>
            <input
              type="password"
              class="wh-input"
              placeholder="••••••••"
              v-model="password"
              @keyup.enter="handleLogin"
            />
          </div>

          <div v-if="error" class="wh-alert wh-alert-danger" style="margin-bottom: 14px;">
            <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
          </div>

          <button
            class="btn-wh-primary"
            style="width: 100%; padding: 10px;"
            :disabled="store.loading"
            @click="handleLogin"
          >
            <span v-if="store.loading">
              <i class="bi bi-arrow-repeat me-1" style="animation: spin 1s linear infinite; display:inline-block;"></i>
              Вход...
            </span>
            <span v-else>Войти</span>
          </button>
        </div>
      </div>

      <div class="login-footer-note">
        © 2026 · Все права защищены
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 440px;
}

.login-brand {
  text-align: center;
  margin-bottom: 28px;
}
.login-logo {
  font-size: 40px;
  color: var(--c-accent);
  line-height: 1;
  margin-bottom: 10px;
}
.login-company {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.15em;
  color: var(--c-text);
  margin-bottom: 4px;
}
.login-subtitle {
  font-size: 12px;
  color: var(--c-muted);
  letter-spacing: 0.05em;
}

.login-card-header {
  border-bottom: 1px solid var(--c-border);
  padding-bottom: 14px;
}
.login-card-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--c-accent);
}

.field-group { margin-bottom: 14px; }

.login-footer-note {
  margin-top: 20px;
  font-size: 11px;
  color: var(--c-muted);
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
