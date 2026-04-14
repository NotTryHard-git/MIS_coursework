<script>
import { useStore } from '@/store/index'

export default {
  props: { data: {} },
  data() {
    return { store: useStore() }
  },
  methods: {
    async addWarehouseHandler() {
      await this.store.addWarehouse({
        workshop_number: this.data.workshop_number,
        warehouse_number: 1
      })
      await this.store.fetchAllLocations()
    }
  }
}
</script>

<template>
<div class="wh-card location-card">

  <div class="wh-card-header">
    <i class="bi bi-building"></i>
    Цех {{ data.workshop_number }}
  </div>

  <ul class="loc-list">
    <li
      v-for="warehouse in data.warehouses"
      :key="warehouse.id"
      class="loc-item"
    >
      <div class="loc-item-left">
        <span class="loc-dot"></span>
        <span class="loc-name">Склад №{{ warehouse.warehouse_number }}</span>
      </div>
      <span class="loc-count">
        {{ store.getEquipmentByLocation(warehouse.id) }}
        <span class="loc-count-label">шт.</span>
      </span>
    </li>

  </ul>

  <div class="loc-footer">
    <button class="btn-wh-ghost" style="width: 100%; font-size: 12px;" @click="addWarehouseHandler">
      <i class="bi bi-plus me-1"></i>Добавить склад
    </button>
  </div>

</div>
</template>

<style scoped>
.location-card { width: 240px; }

.loc-warehouse-count {
  margin-left: auto;
  font-size: 10px;
  font-weight: 400;
  color: var(--c-muted);
  font-family: var(--font-mono);
  text-transform: none;
  letter-spacing: 0;
}

.loc-list {
  list-style: none;
  margin: 0;
  padding: 4px 0;
}

.loc-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px;
  border-bottom: 1px solid var(--c-border);
  transition: background var(--transition);
}
.loc-item:hover { background: var(--c-surface2); }
.loc-item:last-child { border-bottom: none; }

.loc-item-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.loc-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--c-accent);
  flex-shrink: 0;
}
.loc-name { font-size: 13px; color: var(--c-text); }

.loc-count {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--c-accent);
  font-weight: 500;
}
.loc-count-label {
  font-size: 10px;
  color: var(--c-muted);
  margin-left: 2px;
}

.loc-empty {
  padding: 14px;
  text-align: center;
  font-size: 12px;
  color: var(--c-muted);
}

.loc-footer {
  padding: 8px 10px;
  border-top: 1px solid var(--c-border);
}
</style>
