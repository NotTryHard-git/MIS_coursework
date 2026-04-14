<script>
import { useStore } from '@/store'
import ModalAddEquip from '@/components/ModalAddEquip.vue'

export default {
  name: 'SearchDetailPanel',
  components: { ModalAddEquip },

  props: {
    equipment: { type: Object, default: null },
  },

  data() {
    return {
      store: useStore(),
      selectedFiles:  { passport: null, documentation: null },
      uploadingType:  null,
      message:        '',
      messageIsError: false,
      showEditModal:  false,
    }
  },

  computed: {
    isAdmin()          { return this.store.currentUser?.is_admin === true },
    hasPassport()      { return !!this.equipment?.equipment_files?.passport_unique_name },
    hasDocumentation() { return !!this.equipment?.equipment_files?.documentation_unique_name },
    typeName()         { return this.equipment?.equipment_type?.name || null },
    typeLabel() {
      if (!this.typeName) return '—'
      return this.store.labels[this.typeName] || this.typeName
    },
    typeInitial()  { return this.typeLabel.charAt(0).toUpperCase() },
    typeIconClass() {
      const m = { pump: 'pump', electric_motor: 'motor', machine_tool: 'tool' }
      return m[this.typeName] || 'other'
    },
    badgeClass() {
      const m = { pump: 'wh-badge-pump', electric_motor: 'wh-badge-motor', machine_tool: 'wh-badge-tool' }
      return m[this.typeName] || 'wh-badge-muted'
    },
    locationLabel() {
      const loc = this.equipment?.location
      if (!loc) return '—'
      const w  = loc.workshop_number  != null ? `Цех ${loc.workshop_number}`  : ''
      const wh = loc.warehouse_number != null ? `Склад ${loc.warehouse_number}` : ''
      return [w, wh].filter(Boolean).join(' · ') || '—'
    },
    extraChars() {
      if (!this.equipment || !this.typeName) return null
      const raw = this.equipment[this.typeName]
      if (!raw) return null
      const f = { ...raw }
      delete f.id
      return f
    },
  },

  methods: {
    onFileSelect(e, type) { this.selectedFiles[type] = e.target.files[0] || null },

    async download(fileType) {
      try { await this.store.downloadFile(this.equipment.id, fileType) }
      catch { this.showMsg(this.store.error || 'Ошибка скачивания', true) }
    },

    async upload(fileType) {
      if (!this.selectedFiles[fileType]) return
      this.uploadingType = fileType
      try {
        await this.store.uploadFile(this.equipment.id, fileType, this.selectedFiles[fileType])
        this.selectedFiles[fileType] = null
        this.showMsg('Файл загружен', false)
      } catch {
        this.showMsg(this.store.error || 'Ошибка загрузки', true)
      } finally { this.uploadingType = null }
    },

    async deleteFile(fileType) {
      if (!confirm('Удалить файл?')) return
      try {
        await this.store.deleteFile(this.equipment.id, fileType)
        this.showMsg('Файл удалён', false)
      } catch { this.showMsg(this.store.error || 'Ошибка удаления', true) }
    },

    showMsg(text, isError) {
      this.message = text
      this.messageIsError = isError
      setTimeout(() => this.message = '', 3000)
    },
  },
}
</script>

<template>
<div class="wh-card detail-panel">

  <!-- Пустое состояние -->
  <div v-if="!equipment" class="detail-empty">
    <i class="bi bi-arrow-left-circle" style="font-size: 28px; color: var(--c-border2);"></i>
    <span>Выберите оборудование</span>
  </div>

  <div v-else class="detail-body">

    <!-- Шапка -->
    <div class="detail-header">
      <div class="wh-type-icon" :class="typeIconClass">{{ typeInitial }}</div>
      <div class="detail-header-info">
        <div class="detail-name">{{ equipment.name }}</div>
        <div class="detail-meta">
          <span class="wh-badge" :class="badgeClass">{{ typeLabel }}</span>
          <span class="detail-location">
            <i class="bi bi-geo-alt me-1"></i>{{ locationLabel }}
          </span>
        </div>
      </div>
    </div>

    <hr class="divider" />

    <!-- Основные данные -->
    <div class="wh-section-label">Основные данные</div>
    <table class="wh-table">
      <tbody>
        <tr><td>Тип</td><td>{{ typeLabel }}</td></tr>
        <tr><td>Местонахождение</td><td>{{ locationLabel }}</td></tr>
        <tr>
        <td>Статус</td>
        <td>
          <span class="wh-badge" :class="equipment.is_used ? 'wh-badge-pump' : 'wh-badge-success'">
            {{ equipment.is_used ? 'В эксплуатации' : 'На складе' }}
              </span>
            </td>
          </tr>
      </tbody>
    </table>

    <!-- Характеристики -->
    <template v-if="extraChars">
      <div class="wh-section-label" style="margin-top: 8px;">Характеристики</div>
      <table class="wh-table">
        <tbody>
          <tr v-for="(value, key) in extraChars" :key="key">
            <td>{{ store.formatLabel(key) }}</td>
            <td>{{ value || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </template>

    <!-- Документы -->
    <div class="wh-section-label" style="margin-top: 8px;">Документы</div>

    <!-- Паспорт -->
    <div class="doc-row" :class="{ 'border-bottom-row': isAdmin }">
      <div class="doc-row-top">
        <span class="doc-label">Паспорт</span>
        <div class="doc-actions">
          <span v-if="!hasPassport" class="doc-missing">Не загружен</span>
          <template v-else>
            <button class="btn-wh-icon" :disabled="store.loading" @click="download('passport')">
              <i class="bi bi-download"></i>Скачать
            </button>
            <button v-if="isAdmin" class="btn-wh-icon danger" :disabled="store.loading" @click="deleteFile('passport')">
              <i class="bi bi-trash"></i>Удалить
            </button>
          </template>
        </div>
      </div>
      <div v-if="isAdmin" class="doc-upload-row">
        <input
          type="file"
          class="wh-input"
          style="font-size: 12px; padding: 5px 10px;"
          accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
          @change="e => onFileSelect(e, 'passport')"
        />
        <button
          class="btn-wh-primary"
          style="flex-shrink:0; padding: 5px 12px; font-size: 12px;"
          :disabled="!selectedFiles.passport || store.loading"
          @click="upload('passport')"
        >{{ uploadingType === 'passport' ? '...' : '⬆' }}</button>
      </div>
    </div>

    <!-- Документация -->
    <div class="doc-row">
      <div class="doc-row-top">
        <span class="doc-label">Документация</span>
        <div class="doc-actions">
          <span v-if="!hasDocumentation" class="doc-missing">Не загружена</span>
          <template v-else>
            <button class="btn-wh-icon" :disabled="store.loading" @click="download('documentation')">
              <i class="bi bi-download"></i>Скачать
            </button>
            <button v-if="isAdmin" class="btn-wh-icon danger" :disabled="store.loading" @click="deleteFile('documentation')">
              <i class="bi bi-trash"></i>Удалить
            </button>
          </template>
        </div>
      </div>
      <div v-if="isAdmin" class="doc-upload-row">
        <input
          type="file"
          class="wh-input"
          style="font-size: 12px; padding: 5px 10px;"
          accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
          @change="e => onFileSelect(e, 'documentation')"
        />
        <button
          class="btn-wh-primary"
          style="flex-shrink:0; padding: 5px 12px; font-size: 12px;"
          :disabled="!selectedFiles.documentation || store.loading"
          @click="upload('documentation')"
        >{{ uploadingType === 'documentation' ? '...' : '⬆' }}</button>
      </div>
    </div>

    <!-- Сообщение -->
    <div v-if="message" class="wh-alert" :class="messageIsError ? 'wh-alert-danger' : 'wh-alert-success'" style="margin-top: 10px;">
      {{ message }}
    </div>

    <!-- Кнопка редактирования -->
    <div v-if="isAdmin" style="margin-top: 12px;">
      <button class="btn-wh-ghost" style="width: 100%;" @click="showEditModal = true">
        <i class="bi bi-pencil me-1"></i>Редактировать
      </button>
    </div>

  </div>

  <ModalAddEquip
    v-model:show="showEditModal"
    mode="edit"
    :equipment-to-edit="equipment"
  />
</div>
</template>

<style scoped>
.detail-panel {
  width: 360px;
  flex-shrink: 0;
}
.detail-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 60px 20px;
  color: var(--c-muted);
  font-size: 13px;
}
.detail-body { padding: 14px; }

.detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}
.detail-header-info { flex: 1; min-width: 0; }
.detail-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--c-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.detail-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}
.detail-location {
  font-size: 11px;
  color: var(--c-muted);
}

/* Документы */
.doc-row {
  padding: 10px 0;
  border-bottom: 1px solid var(--c-border);
}
.doc-row:last-of-type { border-bottom: none; }
.doc-row-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.doc-label  { font-size: 13px; color: var(--c-text); }
.doc-missing{ font-size: 11px; color: var(--c-muted); }
.doc-actions { display: flex; gap: 4px; align-items: center; }
.doc-upload-row {
  display: flex;
  gap: 6px;
  margin-top: 8px;
  align-items: center;
}
</style>
