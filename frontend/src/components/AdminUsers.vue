<script>
import ModalAddUser from './ModalAddUser.vue'
import UserItem from './UserItem.vue'
import { useStore } from '@/store/index'

export default {
  components: { UserItem, ModalAddUser },
  async mounted() {
    await this.store.fetchAllUsers()
  },
  data() {
    return {
      ModalShow: false,
      store: useStore()
    }
  },
  methods: {
    showModalAdd() { this.ModalShow = true }
  }
}
</script>

<template>
<ModalAddUser v-model:show="ModalShow" />

<div class="users-page">

  <div class="users-topbar">
    <div class="users-title">
      <i class="bi bi-people me-2 text-accent"></i>
      Пользователи
      <span class="users-count">{{ store.users.length }}</span>
    </div>
    <button class="btn-wh-primary" @click="showModalAdd">
      <i class="bi bi-plus me-1"></i>Добавить пользователя
    </button>
  </div>

  <div class="users-grid">
    <div v-if="!store.users.length" class="users-empty">
      <i class="bi bi-person-slash" style="font-size: 32px; color: var(--c-border2);"></i>
      <span>Нет пользователей</span>
    </div>
    <UserItem
      v-for="user in store.users"
      :key="user.id"
      :data="user"
    />
  </div>

</div>
</template>

<style scoped>
.users-page { 
  padding: 24px;
  min-height: calc(100vh - 64px - 200px); 
}

.users-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.users-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--c-text);
  display: flex;
  align-items: baseline;
  gap: 10px;
}
.users-count {
  font-size: 12px;
  font-weight: 400;
  color: var(--c-muted);
  font-family: var(--font-mono);
}

.users-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-start;
}
.users-empty {
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
