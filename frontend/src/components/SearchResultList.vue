<script>
import { useStore } from '@/store'

export default {
  name: 'SearchResultList',
  props: {
    results:    { type: Array,  default: () => [] },
    selectedId: { type: Number, default: null },
  },
  emits: ['select'],
  data() { return { store: useStore() } },
  computed: {
    groupedResults() {
      const groups = {}
      for (const eq of this.results) {
        const t = eq.equipment_type?.name || 'other'
        if (!groups[t]) groups[t] = []
        groups[t].push(eq)
      }
      return groups
    },
  },
  methods: {
    typeLabel(t)   { return this.store.labels[t] || t },
    typeInitial(t) { return this.typeLabel(t).charAt(0).toUpperCase() },
    iconClass(t) {
      const m = { pump: 'pump', electric_motor: 'motor', machine_tool: 'tool' }
      return m[t] || 'other'
    },
    locationLabel(eq) {
      if (!eq.location) return '—'
      const w  = eq.location.workshop_number  != null ? `Цех ${eq.location.workshop_number}`  : ''
      const wh = eq.location.warehouse_number != null ? `Склад ${eq.location.warehouse_number}` : ''
      return [w, wh].filter(Boolean).join(' · ') || '—'
    },
  },
}
</script>

<template>
<div class="result-list">
  <div v-for="(group, typeName) in groupedResults" :key="typeName">

    <!-- Заголовок группы -->
    <div class="result-group-label">{{ typeLabel(typeName) }}</div>

    <!-- Элементы группы -->
    <div
      v-for="eq in group"
      :key="eq.id"
      class="result-item"
      :class="{ active: selectedId === eq.id }"
      @click="$emit('select', eq.id)"
    >
      <div class="wh-type-icon" :class="iconClass(typeName)" style="width:30px;height:30px;font-size:11px;">
        {{ typeInitial(typeName) }}
      </div>
      <div class="result-item-info">
        <div class="result-item-name" :class="{ 'text-accent': selectedId === eq.id }">
          {{ eq.name }}
        </div>
        <div class="result-item-loc">{{ locationLabel(eq) }}</div>
      </div>
      <i class="bi bi-chevron-right result-item-arrow"
         :class="{ 'text-accent': selectedId === eq.id }"></i>
    </div>

  </div>
</div>
</template>

<style scoped>
.result-list {
  width: 260px;
  min-width: 260px;
  flex-shrink: 0;
  border-right: 1px solid var(--c-border);
  overflow-y: auto;
  max-height: 500px;
}

.result-group-label {
  padding: 7px 12px 4px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--c-muted);
  background: var(--c-surface2);
  border-bottom: 1px solid var(--c-border);
  position: sticky;
  top: 0;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-bottom: 1px solid var(--c-border);
  cursor: pointer;
  transition: background var(--transition);
}
.result-item:hover  { background: var(--c-surface2); }
.result-item.active { background: var(--c-accent-bg); }

.result-item-info {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}
.result-item-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--c-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.result-item-loc {
  font-size: 11px;
  color: var(--c-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.result-item-arrow {
  font-size: 10px;
  color: var(--c-muted);
  flex-shrink: 0;
}
</style>
