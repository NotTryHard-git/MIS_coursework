import AdminCatalogPage from '@/pages/AdminCatalogPage.vue'
import AdminLocationPage from '@/pages/AdminLocationPage.vue'
import AdminUsersPage from '@/pages/AdminUsersPage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import ViewerPage from '@/pages/ViewerPage.vue'
import { createRouter, createWebHistory } from 'vue-router'
import { useStore } from '@/store'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: LoginPage,
      meta: { guestOnly: true }   // только для незалогиненных
    },
    {
      path: '/admin',
      component: AdminCatalogPage,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/catalog',
      component: AdminCatalogPage,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/users',
      component: AdminUsersPage,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/location',
      component: AdminLocationPage,
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/view',
      component: ViewerPage,
      meta: { requiresAuth: true }
    }
  ],
})

router.beforeEach(async (to, from, next) => {
  const store = useStore()

  // Если статус авторизации ещё неизвестен — пробуем получить текущего пользователя
  if (!store.isAuthenticated && !store.authChecked) {
    try {
      await store.getCurrentUser()
    } catch {
      // не авторизован — ничего не делаем, идём дальше
    }
  }

  const isAuth  = store.isAuthenticated
  const isAdmin = store.currentUser?.is_admin === true

  // Залогиненного отправляем с / на нужную страницу
  if (to.meta.guestOnly && isAuth) {
    return next(isAdmin ? '/admin/catalog' : '/view')
  }

  // Требует авторизации
  if (to.meta.requiresAuth && !isAuth) {
    return next('/')
  }

  // Требует прав админа
  if (to.meta.requiresAdmin && !isAdmin) {
    return next('/view')
  }

  next()
})

export default router