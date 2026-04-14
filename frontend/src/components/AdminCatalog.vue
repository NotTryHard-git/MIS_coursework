<script>
import ModalAddEquip from './ModalAddEquip.vue';
import { useStore } from '@/store/index'
import SearchDetailPanel from './SearchDetailPanel.vue';

export default {
  components: { ModalAddEquip, SearchDetailPanel },

  data() {
    return {
      ModalShow: false,
      store: useStore(),
      SearchQueryDetail: '',
      equipType: 1,
      typeSearchResults: null,
    }
  },

  computed: {
    searchResults() {
      if (this.typeSearchResults !== null) return this.typeSearchResults
      return this.store.equipmentList.filter(
        eq => eq.equipment_type.type_id === this.equipType
      )
    },
    isAdmin() {
      return this.store.currentUser?.is_admin === true
    }
  },

  async mounted() {
    await this.store.fetchAllTypes()
    await this.store.fetchAllEquipment()
    await this.store.fetchAllLocations()
    this.equipType = this.store.typeFilter.type_id
  },

  methods: {
    showModalAdd() { this.ModalShow = true },
    async ModalClose() { this.typeSearchResults = null },
    handleTypeClick(type) {
      this.store.getTypeFilter(type)
      this.equipType = type.type_id
      this.typeSearchResults = null
      this.SearchQueryDetail = ''
    },
    async performSearch() {
      if (!this.SearchQueryDetail) { this.typeSearchResults = null; return }
      const query = this.SearchQueryDetail.split(':').map(i => i.trim())
      const key = this.store.findMatchingKey(query[0])
      const result = await this.store.SearchInType({ key, value: query[1] })
      this.typeSearchResults = result.filter(eq => eq.equipment_type.type_id === this.equipType)
    }
  }
}
</script>

<template>
<div class="catalog-layout">

  <!-- Сайдбар категорий -->
  <aside class="catalog-sidebar">
    <div class="wh-card-header">
      <i class="bi bi-tag"></i> Категории
    </div>
    <ul class="cat-list">
      <li
        v-for="type in store.typesList"
        :key="type.type_id"
        class="cat-item"
        :class="{ active: equipType === type.type_id }"
        @click="handleTypeClick(type)"
      >
        <span
          class="wh-type-icon"
          :class="{
            pump:  type.name === 'pump',
            motor: type.name === 'electric_motor',
            tool:  type.name === 'machine_tool',
            other: !['pump','electric_motor','machine_tool'].includes(type.name)
          }"
          style="width:28px; height:28px; font-size:11px;"
        >{{ store.formatLabel(type.name).charAt(0) }}</span>
        {{ store.formatLabel(type.name) }}
      </li>
    </ul>
  </aside>

  <!-- Основная область -->
  <main class="catalog-main">

    <!-- Панель поиска и заголовка -->
    <div class="catalog-topbar">
      <div class="catalog-title">
        {{ store.formatLabel(store.typeFilter.name) }}
        <span class="catalog-count">{{ searchResults.length }} ед.</span>
      </div>
      <form class="catalog-search-form" @submit.prevent="performSearch">
        <div class="search-input-wrap">
          <i class="bi bi-search search-icon"></i>
          <input
            class="wh-input search-input"
            type="search"
            placeholder="Мощность двигателя (кВт) : 200"
            v-model="SearchQueryDetail"
          />
        </div>
        <button class="btn-wh-ghost" type="submit">Поиск</button>
        <button v-if="isAdmin" class="btn-wh-primary" type="button" @click="showModalAdd">
          <i class="bi bi-plus me-1"></i>Добавить
        </button>
      </form>
    </div>

    <!-- Сетка карточек -->
    <div class="catalog-grid">
      <div
        v-if="!searchResults.length"
        class="catalog-empty"
      >
        <i class="bi bi-inbox" style="font-size: 32px; color: var(--c-border2);"></i>
        <span>Оборудование не найдено</span>
      </div>
      <SearchDetailPanel
        v-for="equipment in searchResults"
        :key="equipment.id"
        :equipment="equipment"
      />
    </div>
  </main>

</div>

<ModalAddEquip v-model:show="ModalShow" @close="ModalClose" />
</template>

<style scoped>
.catalog-layout {
  display: flex;
  gap: 0;
  min-height: calc(100vh - 64px - 150px);
}

/* Сайдбар */
.catalog-sidebar {
  width: 220px;
  flex-shrink: 0;
  border-right: 1px solid var(--c-border);
  background: var(--c-surface);
}
.cat-list {
  list-style: none;
  margin: 0;
  padding: 6px 0;
}
.cat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  font-size: 13px;
  font-weight: 500;
  color: var(--c-label);
  cursor: pointer;
  transition: all var(--transition);
  border-left: 2px solid transparent;
}
.cat-item:hover { color: var(--c-text); background: var(--c-surface2); }
.cat-item.active {
  color: var(--c-accent);
  background: var(--c-accent-bg);
  border-left-color: var(--c-accent);
}

/* Основная область */
.catalog-main { flex: 1; padding: 20px 24px; overflow: hidden; }

.catalog-topbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.catalog-title {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--c-text);
  white-space: nowrap;
  display: flex;
  align-items: baseline;
  gap: 10px;
}
.catalog-count {
  font-size: 12px;
  font-weight: 400;
  color: var(--c-muted);
  font-family: var(--font-mono);
}
.catalog-search-form {
  display: flex;
  gap: 8px;
  flex: 1;
  min-width: 0;
  align-items: center;
}
.search-input-wrap {
  position: relative;
  flex: 1;
  min-width: 0;
}
.search-icon {
  position: absolute;
  left: 10px; top: 50%;
  transform: translateY(-50%);
  color: var(--c-muted);
  font-size: 13px;
  pointer-events: none;
}
.search-input {
  padding-left: 32px;
}

/* Сетка */
.catalog-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-start;
}
.catalog-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 60px 0;
  width: 100%;
  color: var(--c-muted);
  font-size: 13px;
}
</style>
