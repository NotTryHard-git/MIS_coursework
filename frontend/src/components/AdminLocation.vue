<script>
import LocationItem from './LocationItem.vue';
import { useStore } from '@/store/index'

export default {
  components: { LocationItem },
  async mounted() {
    await this.store.fetchAllEquipment()
    await this.store.fetchAllLocations()
  },
  data() {
    return { store: useStore() }
  },
  methods: {
    async addWorkshopHandler() {
      await this.store.addWorkshop()
      await this.store.fetchAllLocations()
    }
  }
}
</script>

<template>
<div class="location-page">

  <div class="location-topbar">
    <div class="location-title">
      <i class="bi bi-diagram-3 me-2 text-accent"></i>
      Структура складов
      <span class="location-count">{{ store.locationsList.length }} цехов</span>
    </div>
    <button class="btn-wh-primary" @click="addWorkshopHandler">
      <i class="bi bi-plus me-1"></i>Добавить цех
    </button>
  </div>

  <div class="location-grid">
    <div v-if="!store.locationsList.length" class="location-empty">
      <i class="bi bi-building" style="font-size: 32px; color: var(--c-border2);"></i>
      <span>Нет добавленных цехов</span>
    </div>
    <LocationItem
      v-for="workshop in store.locationsList"
      :key="workshop.workshop_number"
      :data="workshop"
    />
  </div>

</div>
</template>

<style scoped>
.location-page { 
  padding: 24px;
  min-height: calc(100vh - 64px - 200px); 
}

.location-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.location-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--c-text);
  display: flex;
  align-items: baseline;
  gap: 10px;
}
.location-count {
  font-size: 12px;
  font-weight: 400;
  color: var(--c-muted);
  font-family: var(--font-mono);
}

.location-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-start;
}
.location-empty {
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
