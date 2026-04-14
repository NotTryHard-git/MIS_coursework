<script>
import { useStore } from '@/store/index'

export default {
  name: 'ModalAddEquip',
  props: {
    show:            { type: Boolean, default: false },
    mode:            { type: String,  default: 'add' },
    equipmentToEdit: { type: Object,  default: null  },
  },
  emits: ['close', 'update:show'],
  data() {
    return {
      store: useStore(),
      selectedWorkshopNumber: null,
      selectedWarehouse:      null,
      selectedType:           null,
      equipmentName:          '',
      isUsed: null,
      characteristicsData:    {},
      selectedFiles:          { passport: null, documentation: null },
      filesToDelete:          { passport: false, documentation: false },
      submitting:   false,
      errorMessage: '',
      equip_extra_char: {
        pump:          { capacity_m3_per_hour: 0, engine_power_kw: 0, voltage_v: '', inlet_diameter_mm: 0, outlet_diameter_mm: 0 },
        electric_motor:{ power_kw: 0, rated_current_a: 0, rated_speed_rpm: 0, shaft_diameter_mm: 0, energy_efficiency_class: '' },
        machine_tool:  { table_size_mm: '', max_workpiece_weight_kg: 0, rotation_speed_rpm: 0, axis_count: 0, accuracy_class: '' }
      }
    }
  },
  computed: {
    isEditMode() { return this.mode === 'edit' },
    currentPassport() {
      if (this.filesToDelete.passport) return null
      return this.equipmentToEdit?.equipment_files?.passport_unique_name || null
    },
    currentDocumentation() {
      if (this.filesToDelete.documentation) return null
      return this.equipmentToEdit?.equipment_files?.documentation_unique_name || null
    },
    warehousesForSelectedWorkshop() {
      if (!this.selectedWorkshopNumber) return []
      const w = this.store.locationsList.find(w => w.workshop_number === this.selectedWorkshopNumber)
      return w ? w.warehouses : []
    },
    selectedTypeChars() {
      if (!this.selectedType?.name) return {}
      return this.equip_extra_char[this.selectedType.name] || {}
    }
  },
  watch: {
    show(newVal) {
      if (newVal) {
        if (this.isEditMode && this.equipmentToEdit) this.fillForm()
        else this.resetForm()
      }
    },
    selectedType(newType, oldType) {
      if (oldType !== null) this.characteristicsData = {}
    }
  },
  methods: {
    fillForm() {
      const eq = this.equipmentToEdit
      this.equipmentName = eq.name
      this.selectedWorkshopNumber = eq.location.workshop_number
      this.$nextTick(() => {
        const w = this.store.locationsList.find(w => w.workshop_number === eq.location.workshop_number)
        if (w) this.selectedWarehouse = w.warehouses.find(wh => wh.id === eq.location.place_id) || null
      })
      this.selectedType = this.store.typesList.find(t => t.type_id === eq.equipment_type.type_id) || null
      const typeName = eq.equipment_type.name
      if (eq[typeName]) {
        const chars = { ...eq[typeName] }; delete chars.id
        this.characteristicsData = chars
      } else { this.characteristicsData = {} }
      this.selectedFiles = { passport: null, documentation: null }
      this.filesToDelete = { passport: false, documentation: false }
      this.errorMessage  = ''
      this.submitting    = false
      this.isUsed = eq.is_used ?? false
    },
    resetForm() {
      this.selectedWorkshopNumber = null; this.selectedWarehouse = null
      this.selectedType = null; this.equipmentName = ''; this.characteristicsData = {}
      this.selectedFiles = { passport: null, documentation: null }
      this.filesToDelete = { passport: false, documentation: false }
      this.errorMessage  = ''; this.submitting = false
    },
    onFileSelect(e, type) {
      this.selectedFiles[type] = e.target.files[0] || null
      if (this.selectedFiles[type]) this.filesToDelete[type] = false
    },
    removeCurrentFile(type) { this.filesToDelete[type] = true },
    closeModal() { this.$emit('update:show', false); this.$emit('close'); this.resetForm() },
    buildChars() {
      const n = this.selectedType.name; const d = this.characteristicsData
      if (n === 'pump') return { capacity_m3_per_hour: Number(d.capacity_m3_per_hour)||0, engine_power_kw: Number(d.engine_power_kw)||0, voltage_v: d.voltage_v||'', inlet_diameter_mm: Number(d.inlet_diameter_mm)||0, outlet_diameter_mm: Number(d.outlet_diameter_mm)||0 }
      if (n === 'electric_motor') return { power_kw: Number(d.power_kw)||0, rated_current_a: Number(d.rated_current_a)||0, rated_speed_rpm: Number(d.rated_speed_rpm)||0, shaft_diameter_mm: Number(d.shaft_diameter_mm)||0, energy_efficiency_class: d.energy_efficiency_class||'' }
      if (n === 'machine_tool') return { table_size_mm: d.table_size_mm||'', max_workpiece_weight_kg: Number(d.max_workpiece_weight_kg)||0, rotation_speed_rpm: Number(d.rotation_speed_rpm)||0, axis_count: Number(d.axis_count)||0, accuracy_class: d.accuracy_class||'' }
      return null
    },
    validate() {
      if (!this.selectedWorkshopNumber || !this.selectedWarehouse) { this.errorMessage = 'Выберите цех и склад'; return false }
      if (!this.selectedType)         { this.errorMessage = 'Выберите категорию'; return false }
      if (!this.equipmentName.trim()) { this.errorMessage = 'Введите название'; return false }
      return true
    },
    async handleSubmit() {
      this.errorMessage = ''
      if (!this.validate()) return
      this.submitting = true
      try {
        if (this.isEditMode) await this.submitEdit()
        else                 await this.submitAdd()
        this.closeModal()
      } catch (e) {
        this.errorMessage = this.store.error || e.message || 'Произошла ошибка'
      } finally { this.submitting = false }
    },
    async submitAdd() {
      const n = this.selectedType.name; const c = this.buildChars()
      const eq = await this.store.addEquipment({ name: this.equipmentName.trim(), is_used: this.isUsed, place_id: this.selectedWarehouse.id, type_id: this.selectedType.type_id, passport_unique_name: '', documentation_unique_name: '', electric_motor: n==='electric_motor'?c:null, machine_tool: n==='machine_tool'?c:null, pump: n==='pump'?c:null })
      const uploads = []
      if (this.selectedFiles.passport)      uploads.push(this.store.uploadFile(eq.id,'passport',this.selectedFiles.passport))
      if (this.selectedFiles.documentation) uploads.push(this.store.uploadFile(eq.id,'documentation',this.selectedFiles.documentation))
      if (uploads.length) await Promise.all(uploads)
    },
    async submitEdit() {
      const n = this.selectedType.name; const c = this.buildChars(); const id = this.equipmentToEdit.id
      await this.store.updateEquipment(id, { name: this.equipmentName.trim(), is_used: this.isUsed, place_id: this.selectedWarehouse.id, type_id: this.selectedType.type_id, electric_motor: n==='electric_motor'?c:null, machine_tool: n==='machine_tool'?c:null, pump: n==='pump'?c:null })
      const deletes = []
      if (this.filesToDelete.passport)      deletes.push(this.store.deleteFile(id,'passport'))
      if (this.filesToDelete.documentation) deletes.push(this.store.deleteFile(id,'documentation'))
      if (deletes.length) await Promise.all(deletes)
      const uploads = []
      if (this.selectedFiles.passport)      uploads.push(this.store.uploadFile(id,'passport',this.selectedFiles.passport))
      if (this.selectedFiles.documentation) uploads.push(this.store.uploadFile(id,'documentation',this.selectedFiles.documentation))
      if (uploads.length) await Promise.all(uploads)
    },
    async handleDelete() {
      if (!confirm(`Удалить оборудование "${this.equipmentToEdit.name}"?`)) return
      this.submitting = true
      try { await this.store.deleteEquipment(this.equipmentToEdit.id); this.closeModal() }
      catch (e) { this.errorMessage = this.store.error || e.message || 'Ошибка удаления' }
      finally { this.submitting = false }
    },
    resetWarehouse() { this.selectedWarehouse = null },
  }
}
</script>

<template>
<div v-if="show" class="wh-modal-overlay" @click.self="closeModal">
  <div class="wh-modal">

    <div class="wh-modal-header">
      <h5 class="wh-modal-title">
        <i :class="isEditMode ? 'bi bi-pencil' : 'bi bi-plus-circle'" class="me-2"></i>
        {{ isEditMode ? 'Редактировать оборудование' : 'Новое оборудование' }}
      </h5>
    </div>

    <div class="wh-modal-body">

      <!-- Местоположение -->
      <div class="form-row-2">
        <div>
          <label class="wh-label">Цех</label>
          <select class="wh-select" v-model="selectedWorkshopNumber" @change="resetWarehouse">
            <option disabled value="">Выберите цех</option>
            <option v-for="w in store.locationsList" :value="w.workshop_number" :key="w.workshop_number">
              Цех {{ w.workshop_number }}
            </option>
          </select>
        </div>
        <div>
          <label class="wh-label">Склад</label>
          <select class="wh-select" v-model="selectedWarehouse" :disabled="!selectedWorkshopNumber">
            <option disabled value="">Выберите склад</option>
            <option v-for="wh in warehousesForSelectedWorkshop" :value="wh" :key="wh.id">
              Склад {{ wh.warehouse_number }}
            </option>
          </select>
        </div>
        <div>
          <label class="wh-label">Состояние</label>
          <select class="wh-select" v-model="isUsed" >
            <option disabled value="">Выберите состояние</option>
            <option value="false">На складе</option>
            <option value="true">В эксплуатации</option>
          </select>
        </div>
      </div>

      <!-- Категория -->
      <div class="field-group">
        <label class="wh-label">Категория</label>
        <select class="wh-select" v-model="selectedType">
          <option disabled value="">Выберите категорию</option>
          <option v-for="t in store.typesList" :value="t" :key="t.type_id">
            {{ store.formatLabel(t.name) }}
          </option>
        </select>
      </div>

      <!-- Название -->
      <div class="field-group">
        <label class="wh-label">Название</label>
        <input class="wh-input" type="text" v-model="equipmentName"
               placeholder="Введите название оборудования" />
      </div>

      <!-- Характеристики -->
      <div class="field-group" v-if="Object.keys(selectedTypeChars).length">
        <label class="wh-label">Характеристики</label>
        <div class="chars-grid">
          <div v-for="(value, key, i) in selectedTypeChars" :key="i" class="char-field">
            <label class="wh-label" style="font-size:10px;">{{ store.formatLabel(key) }}</label>
            <input class="wh-input" type="text" v-model="characteristicsData[key]"
                   :placeholder="store.formatLabel(key)" />
          </div>
        </div>
      </div>
      <div v-else class="chars-empty">
        <i class="bi bi-sliders me-1"></i>Выберите категорию для ввода характеристик
      </div>

      <!-- Документы -->
      <div class="field-group">
        <label class="wh-label">Документы <span style="font-weight:400; text-transform:none; letter-spacing:0; color: var(--c-muted);">(необязательно)</span></label>
        <div class="docs-grid">

          <div class="doc-field">
            <div class="doc-field-label">
              Паспорт
              <span v-if="isEditMode" class="wh-badge" :class="currentPassport ? 'wh-badge-success' : 'wh-badge-muted'">
                {{ currentPassport ? 'Загружен' : 'Нет' }}
              </span>
              <button v-if="isEditMode && currentPassport" type="button"
                      class="btn-wh-icon danger" style="margin-left: auto;"
                      @click="removeCurrentFile('passport')">
                <i class="bi bi-trash"></i>Удалить
              </button>
            </div>
            <input class="wh-input" type="file"
                   style="font-size:12px; padding: 5px 10px;"
                   accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
                   @change="e => onFileSelect(e,'passport')" />
            <span v-if="selectedFiles.passport" class="field-hint">{{ selectedFiles.passport.name }}</span>
          </div>

          <div class="doc-field">
            <div class="doc-field-label">
              Документация
              <span v-if="isEditMode" class="wh-badge" :class="currentDocumentation ? 'wh-badge-success' : 'wh-badge-muted'">
                {{ currentDocumentation ? 'Загружена' : 'Нет' }}
              </span>
              <button v-if="isEditMode && currentDocumentation" type="button"
                      class="btn-wh-icon danger" style="margin-left: auto;"
                      @click="removeCurrentFile('documentation')">
                <i class="bi bi-trash"></i>Удалить
              </button>
            </div>
            <input class="wh-input" type="file"
                   style="font-size:12px; padding: 5px 10px;"
                   accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
                   @change="e => onFileSelect(e,'documentation')" />
            <span v-if="selectedFiles.documentation" class="field-hint">{{ selectedFiles.documentation.name }}</span>
          </div>

        </div>
      </div>

      <div v-if="errorMessage" class="wh-alert wh-alert-danger">
        <i class="bi bi-exclamation-triangle me-1"></i>{{ errorMessage }}
      </div>

    </div>

    <div class="wh-modal-footer">
      <button v-if="isEditMode" class="btn-wh-danger" style="margin-right: auto;"
              :disabled="submitting" @click="handleDelete">
        <i class="bi bi-trash me-1"></i>Удалить
      </button>
      <button class="btn-wh-ghost" :disabled="submitting" @click="closeModal">Отмена</button>
      <button class="btn-wh-primary" :disabled="submitting" @click="handleSubmit">
        {{ submitting ? 'Сохранение...' : (isEditMode ? 'Сохранить' : 'Добавить') }}
      </button>
    </div>

  </div>
</div>
</template>

<style scoped>
.form-row-2   { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px; }
.field-group  { margin-bottom: 14px; }
.field-hint   { font-size: 11px; color: var(--c-muted); margin-top: 4px; display: block; }
.chars-grid   { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.char-field   { display: flex; flex-direction: column; }
.chars-empty  { font-size: 12px; color: var(--c-muted); padding: 10px 12px; background: var(--c-surface2); border: 1px dashed var(--c-border2); border-radius: var(--radius-sm); margin-bottom: 14px; }
.docs-grid    { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.doc-field    { display: flex; flex-direction: column; gap: 6px; }
.doc-field-label { display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 700; color: var(--c-label); text-transform: uppercase; letter-spacing: 0.05em; }
</style>
