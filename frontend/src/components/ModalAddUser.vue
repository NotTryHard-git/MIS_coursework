<script>
import { useStore } from '@/store/index'

export default {
  props: {
    show: { type: Boolean, default: false }
  },
  emits: ['close', 'update:show'],
  data() {
    return {
      inputedLogin:    '',
      inputedFIO:      '',
      inputedPassword: '',
      isAdmin:         false,
      error:           '',
      store:           useStore()
    }
  },
  watch: {
    show(newVal) {
      if (newVal) this.resetForm()
    }
  },
  methods: {
    closeModal() {
      this.$emit('update:show', false)
    },
    resetForm() {
      this.inputedLogin    = ''
      this.inputedFIO      = ''
      this.inputedPassword = ''
      this.isAdmin         = false
      this.error           = ''
    },
    async handleSubmit() {
      this.error = ''
      const fio = this.inputedFIO.trim().split(/\s+/)
      if (fio.length < 3) {
        this.error = 'Введите ФИО полностью (Фамилия Имя Отчество)'
        return
      }
      if (!this.inputedLogin.trim()) { this.error = 'Введите логин'; return }
      if (!this.inputedPassword)     { this.error = 'Введите пароль'; return }

      const formData = {
        last_name:   fio[0],
        first_name:  fio[1],
        middle_name: fio[2],
        login:       this.inputedLogin,
        is_admin:    this.isAdmin,
        password:    this.inputedPassword
      }
      try {
        await this.store.addUser(formData)
        this.closeModal()
      } catch {
        this.error = this.store.error || 'Ошибка добавления пользователя'
      }
    }
  }
}
</script>

<template>
<div v-if="show" class="wh-modal-overlay" @click.self="closeModal">
  <div class="wh-modal">

    <div class="wh-modal-header">
      <h5 class="wh-modal-title">
        <i class="bi bi-person-plus me-2"></i>Новый пользователь
      </h5>
    </div>

    <div class="wh-modal-body">

      <div class="field-group">
        <label class="wh-label">ФИО</label>
        <input
          class="wh-input"
          type="text"
          placeholder="Иванов Иван Иванович"
          v-model="inputedFIO"
        />
        <span class="field-hint">Фамилия Имя Отчество через пробел</span>
      </div>

      <div class="field-group">
        <label class="wh-label">Логин</label>
        <input
          class="wh-input"
          type="text"
          placeholder="ivan_ivanov"
          v-model="inputedLogin"
        />
      </div>

      <div class="field-group">
        <label class="wh-label">Пароль</label>
        <input
          class="wh-input"
          type="password"
          placeholder="Минимум 6 символов"
          v-model="inputedPassword"
        />
      </div>

      <div class="field-group admin-toggle">
        <label class="toggle-label">
          <div class="toggle-track" :class="{ active: isAdmin }" @click="isAdmin = !isAdmin">
            <div class="toggle-thumb"></div>
          </div>
          <span class="toggle-text">
            Права администратора
            <span class="field-hint" style="display:block;">Доступ к управлению каталогом и пользователями</span>
          </span>
        </label>
      </div>

      <div v-if="error" class="wh-alert wh-alert-danger">
        <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
      </div>

    </div>

    <div class="wh-modal-footer">
      <button class="btn-wh-ghost" @click="closeModal">Отмена</button>
      <button class="btn-wh-primary" @click="handleSubmit"
              :disabled="store.loading">
        {{ store.loading ? 'Сохранение...' : 'Добавить' }}
      </button>
    </div>

  </div>
</div>
</template>

<style scoped>
.field-group { margin-bottom: 14px; }
.field-hint  { font-size: 11px; color: var(--c-muted); margin-top: 3px; display: block; }

/* Тогл */
.admin-toggle { margin-top: 4px; }
.toggle-label {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  cursor: pointer;
  user-select: none;
}
.toggle-track {
  width: 36px; height: 20px;
  border-radius: 10px;
  background: var(--c-border2);
  position: relative;
  flex-shrink: 0;
  margin-top: 2px;
  transition: background var(--transition);
}
.toggle-track.active { background: var(--c-accent); }
.toggle-thumb {
  position: absolute;
  top: 2px; left: 2px;
  width: 16px; height: 16px;
  border-radius: 50%;
  background: white;
  transition: transform var(--transition);
}
.toggle-track.active .toggle-thumb { transform: translateX(16px); }
.toggle-text { font-size: 13px; color: var(--c-text); }
</style>
