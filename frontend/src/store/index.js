import { defineStore } from 'pinia'

export const useStore = defineStore('all', {
  state: () => ({
    /** @type {{ login: string, password: string }} */
    userAuth: { login: '', password: '' },
    // Состояние для пользователя
    /** @type {{ id: number, last_name: string, first_name: string, middle_name: string, login: string, is_admin: boolean }| null} */
    currentUser: {id: 1, last_name: 'string', first_name: 'string', middle_name: 'string', login: 'string', is_admin: true},

    /** @type {{ id: number, last_name: string, first_name: string, middle_name: string, login: string, is_admin: boolean }[]} */
    users: [],
    isAuthenticated: false,
    authChecked: false,
    // Состояние для оборудования
    /** @type {{ id: number, name: string, is_used: boll, location: LocationResponse, equipment_files: EquipmentFilesResponse, equipment_type: EquipmentTypeResponse, electric_motor: ElectricMotorResponse | null, machine_tool: MachineToolResponse | null, pump: PumpResponse | null }[]} */
    equipmentList: [],

    /** @type {{ id: number, capacity_m3_per_hour: number, engine_power_kw: number, voltage_v: string, inlet_diameter_mm: number, outlet_diameter_mm: number }} */
    pump: {id: 0, capacity_m3_per_hour: 0, engine_power_kw: 0, voltage_v: '', inlet_diameter_mm: 0, outlet_diameter_mm: 0},
    
    /** @type {{ id: number, power_kw: number, rated_current_a: number, rated_speed_rpm: number, shaft_diameter_mm: number, energy_efficiency_class: string }} */
    electric_motor: {id: 0, power_kw: 0, rated_current_a: 0, rated_speed_rpm: 0, shaft_diameter_mm: 0, energy_efficiency_class: ''},

    /** @type {{ id: number, table_size_mm: string, max_workpiece_weight_kg: number, rotation_speed_rpm: number, axis_count: number, accuracy_class: string }} */
    machine_tool:{id: 0, table_size_mm: '', max_workpiece_weight_kg: 0, rotation_speed_rpm: 0, axis_count: 0, accuracy_class: ''},
    
    equip_extra_char: [{name: 'pump', chars: {id: 0, capacity_m3_per_hour: 0, engine_power_kw: 0, voltage_v: '', inlet_diameter_mm: 0, outlet_diameter_mm: 0}},
      {name: 'electric_motor', chars: {id: 0, power_kw: 0, rated_current_a: 0, rated_speed_rpm: 0, shaft_diameter_mm: 0, energy_efficiency_class: ''}},
      {name: 'machine_tool', chars: {id: 0, table_size_mm: '', max_workpiece_weight_kg: 0, rotation_speed_rpm: 0, axis_count: 0, accuracy_class: ''}}
    ],

    // Состояние для локаций
    /** @type {{ place_id: number, workshop_number: number, warehouse_number: [] }[]} */
    locationsList: [] ,
    labels: {
      capacity_m3_per_hour: 'Производительность (м³/ч)',
      engine_power_kw: 'Мощность двигателя кВт',
      voltage_v: 'Напряжение (В)',
      inlet_diameter_mm: 'Входной диаметр (мм)',
      outlet_diameter_mm: 'Выходной диаметр (мм)',
      power_kw: 'Мощность эл. (кВт)',
      rated_current_a: 'Номинальный ток (А)',
      rated_speed_rpm: 'Скорость номин. (об/мин)',
      shaft_diameter_mm: 'Диаметр вала (мм)',
      energy_efficiency_class: 'Класс энергоэффект.',
      table_size_mm: 'Размер стола (мм)',
      max_workpiece_weight_kg: 'Макс. вес заготовки (кг)',
      rotation_speed_rpm: 'Частота вращения (об/мин)',
      axis_count: 'Кол-во осей',
      accuracy_class: 'Класс точн.',
      pump: 'Насосное оборуд.',
      electric_motor: 'Электромотор',
      machine_tool: 'Металлообраб. станок'
    },
    // Состояние для типов оборудования
    /** @type {{ type_id: number, name: string }[]} */
    typesList: [] ,
    
    // Общие состояния
    loading: false,
     /** @type {string | null} */
    error: null,

    // Состояние для файлов
    /** @type {string | null} */
    fileDownloadUrl: null ,
    
    // Состояние для поиска по названию оборудования
    searchResults: {},
    // поиск внутри типа по характеристикам
    typeSearchResults: {},
    //фильтр по типам
    typeFilter: {type_id: 1, name: 'electric_motor'},

    
  }),
  getters: {
    // Геттеры для пользователей
    getUserById: (state) => (userId) => {
      return state.users.find(user => user.id === userId)
    },
    
    getUserFullName: (state) => (userId) => {
      const user = state.users.find(u => u.id === userId)
      if (!user) return ''
      return `${user.last_name} ${user.first_name} ${user.middle_name || ''}`.trim()
    },
    
    // Геттеры для оборудования
    getEquipmentById: (state) => (equipmentId) => {
      return state.equipmentList.find(eq => eq.id === equipmentId)
    },
    
    getEquipmentByType: (state) => () => {
      return state.equipmentList.filter(eq => eq.equipment_type.type_id === state.typeFilter.type_id)
    },
    //посчёт количесвта оборудования на складе
    getEquipmentByLocation: (state) => (placeId) => {
      return state.equipmentList.filter(eq => eq.location.place_id === placeId).length
    },
    
    // Геттеры для локаций
    getLocationById: (state) => (placeId) => {
      return state.locationsList.find(loc => loc.place_id === placeId)
    },
    
    getLocationsByWorkshop: (state) => (workshopNumber) => {
      return state.locationsList.filter(loc => loc.workshop_number === workshopNumber)
    },
    
    // Геттеры для типов
    getTypeById: (state) => (typeId) => {
      return state.typesList.find(type => type.type_id === typeId)
    },
    getTypeFilter: (state) => (type) => {
      state.typeFilter=type
      console.log(state.typeFilter)
      return state.typeFilter
    },
    
    // Статус загрузки
    isLoading: (state) => state.loading,
    hasError: (state) => !!state.error
  },
  actions: {
    formatLabel(key) {
            return this.labels[key] || key
    },
    findMatchingKey(searchText) {
        
      // 1. Прямое совпадение со значением
      for (const [key, value] of Object.entries(this.labels)) {
          if (value.toLowerCase() === searchText.toLowerCase()) {
              return key;
          }
      }

      // 2. Частичное совпадение (поиск текста внутри значения)
      for (const [key, value] of Object.entries(this.labels)) {
          if (value.toLowerCase().includes(searchText.toLowerCase()) || 
              searchText.toLowerCase().includes(value.toLowerCase())) {
              return key;
          }
      }

      // 3. Поиск по ключу (если пользователь ввел сам ключ)
      if (this.labels[searchText]) {
          return searchText;
      }

      // 4. Если ничего не найдено, возвращаем исходный текст
      return searchText;
    },
    // POST /login/
    async login() {
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch('http://localhost:8000/login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(this.userAuth)
        })
        
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Ошибка авторизации')
        }
        
        const data = await response.json()
        this.isAuthenticated = true
        this.userAuth={ login: '', password: '' }
        // После успешного входа получаем данные пользователя
        await this.getCurrentUser()
        
        return data
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    
    // POST /logout/
    async logout() {
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch('http://localhost:8000/logout/', {
          method: 'POST',
          credentials: 'include',
        })
        
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Ошибка выхода')
        }
        
        const data = await response.json()
        this.isAuthenticated = false
        this.currentUser = null
        
        return data
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    
    // GET /me/
    async getCurrentUser() {
      this.loading = true
      this.error = null

      try {
        const response = await fetch('http://localhost:8000/me/', {
          credentials: 'include',
        })
      
        if (!response.ok) {
          throw new Error('Не удалось получить данные пользователя')
        }
      
        const userData = await response.json()
        this.currentUser = userData
        this.isAuthenticated = true
        return userData
      } catch (err) {
        this.error = err.message
        this.isAuthenticated = false
        throw err
      } finally {
        this.authChecked = true   // добавить
        this.loading = false
      }
    },
    
    // GET /auth хз хачем
    async checkAuth() {
      try {
        await this.getCurrentUser()
        return true
      } catch {
        this.isAuthenticated = false
        return false
      }
    },
    
    // ========== Пользователи ==========
    
    // GET /users
    async fetchAllUsers() {
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch('http://localhost:8000/users',{
        credentials: 'include',  // ДОБАВИТЬ
    })
        
        if (!response.ok) {
          throw new Error('Не удалось загрузить список пользователей')
        }
        
        const users = await response.json()
        this.users = users
        
        return users
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    
    // POST /user/add
    async addUser(userData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch('http://localhost:8000/user/add', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',  
          body: JSON.stringify(userData)
        })
        
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Ошибка создания пользователя')
        }
        
        const newUser = await response.json()
        this.users.push(newUser)
        
        return newUser
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    
    // ========== Оборудование ==========
    
    // GET /equipment
    async fetchAllEquipment() {
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch('http://localhost:8000/equipment',{
        credentials: 'include', 
        })
        
        if (!response.ok) {
          throw new Error('Не удалось загрузить список оборудования')
        }
        
        const equipment = await response.json()
        this.equipmentList = equipment
        console.log(equipment)
        return equipment
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    // POST /equipment/add
    async addEquipment(equipmentData) {
      this.loading = true
      this.error = null
    
      try {
        const response = await fetch('http://localhost:8000/equipment/add', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(equipmentData)
        })
      
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Ошибка добавления оборудования')
        }
      
        const newEquipment = await response.json()
        this.equipmentList.push(newEquipment)
        return newEquipment
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },

    async SearchInType(queryData) {
      this.loading = true
      this.error = null
      console.log(JSON.stringify(queryData))
      try {
        const response = await fetch('http://localhost:8000/search/type', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',  
    
          body: JSON.stringify(queryData)
        })
        
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Ошибка поиска оборудования')
        }
        
        const result = await response.json()
              
        return result
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    async SearchEquipment(queryData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch('http://localhost:8000/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',  
    
          body: JSON.stringify(queryData)
        })
        
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Ошибка поиска оборудования')
        }
        
        const result = await response.json()
              
        return result
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    
    async updateEquipment(equipmentId, equipmentData) {
      this.loading = true
      this.error = null
      console.log(equipmentId,equipmentData )
      try {
        const response = await fetch(`http://localhost:8000/equipment/${equipmentId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(equipmentData)
        })
      
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Ошибка обновления оборудования')
        }
      
        const updated = await response.json()
      
        // Обновляем объект в списке реактивно
        const index = this.equipmentList.findIndex(eq => eq.id === equipmentId)
        if (index !== -1) {
          this.equipmentList[index] = updated
        }
      
        return updated
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    
    // ========== Локации ==========
    
    // GET /locations
    async fetchAllLocations() {
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch('http://localhost:8000/locations',{
        credentials: 'include',  // ДОБАВИТЬ
    })
        
        if (!response.ok) {
          throw new Error('Не удалось загрузить список локаций')
        }
        
        const locations = await response.json()
        
        let exist_workshop_number=locations[0].workshop_number
        let temp_locations=[{workshop_number: exist_workshop_number, warehouses: []}]
        for (let i = 0; i < locations.length; i++) {
          if (locations[i].workshop_number===exist_workshop_number) {
            temp_locations[exist_workshop_number-1].warehouses.push({id:locations[i].place_id,warehouse_number: locations[i].warehouse_number})
          }
          else{
            exist_workshop_number=locations[i].workshop_number
            temp_locations.push({workshop_number: exist_workshop_number, warehouses: []})
            temp_locations[exist_workshop_number-1].warehouses.push({id:locations[i].place_id,warehouse_number: locations[i].warehouse_number})

          }
        }
        
        this.locationsList.splice(0, this.locationsList.length, ...temp_locations)
        console.log(this.locationsList)
        return locations
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    
    // POST /location/add_workshop
    async addWorkshop() {
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch('http://localhost:8000/location/add_workshop', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',  
          body: JSON.stringify({ "workshop_number": 1,"warehouse_number": 1})
        })
        
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Ошибка добавления цеха')
        }
        
        const newLocation = await response.json()
        this.locationsList.push(newLocation)
        
        return newLocation
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    
    // POST /location/add_warehouse
    async addWarehouse(locationData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch('http://localhost:8000/location/add_warehouse', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include', 
          body: JSON.stringify(locationData)
        })
        
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Ошибка добавления склада')
        }
        
        const newLocation = await response.json()
        this.locationsList.push(newLocation)
        
        return newLocation
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    
    // ========== Типы оборудования ==========
    
    // GET /types
    async fetchAllTypes() {
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch('http://localhost:8000/types',{
        credentials: 'include', 
    })
        
        if (!response.ok) {
          throw new Error('Не удалось загрузить список типов оборудования')
        }
        
        const types = await response.json()
        this.typesList = types
        console.log(types)
        return types
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
      
    },
    
        // ========== Файлы ==========

    async downloadFile(equipmentId, fileType) {
      this.loading = true
      this.error = null

      try {
        const response = await fetch(
          `http://localhost:8000/equipment/${equipmentId}/download/${fileType}`,
          { credentials: 'include' }
        )
      
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Не удалось скачать файл')
        }
      
        // Берём имя файла из заголовка Content-Disposition
        const disposition = response.headers.get('Content-Disposition')
        let filename = `${fileType}_${equipmentId}`  // fallback без расширения
      
        if (disposition) {
          // Заголовок приходит в виде: attachment; filename="passport_5.pdf"
          const match = disposition.match(/filename[^;=\n]*=["']?([^"'\n]+)["']?/)
          if (match && match[1]) {
            filename = match[1].trim()
          }
        }
      
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
      
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      
        setTimeout(() => window.URL.revokeObjectURL(url), 100)
      
        return { success: true }
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },

    async uploadFile(equipmentId, fileType, file) {
      // fileType: 'passport' | 'documentation'
      this.loading = true
      this.error = null
    
      try {
        const formData = new FormData()
        formData.append('file', file)
      
        const response = await fetch(
          `http://localhost:8000/equipment/${equipmentId}/upload/${fileType}`,
          {
            method: 'POST',
            credentials: 'include',
            body: formData
            // Content-Type НЕ указываем — браузер сам выставит boundary для multipart
          }
        )
      
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Ошибка загрузки файла')
        }
      
        const data = await response.json()
      
        // Обновляем имя файла в equipmentList локально, без перезапроса
        const eq = this.equipmentList.find(e => e.id === equipmentId)
        if (eq && eq.equipment_files) {
          eq.equipment_files[`${fileType}_unique_name`] = data.unique_name
        }
      
        return data
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },

    async deleteFile(equipmentId, fileType) {
      this.loading = true
      this.error = null
    
      try {
        const response = await fetch(
          `http://localhost:8000/equipment/${equipmentId}/delete/${fileType}`,
          { method: 'DELETE', credentials: 'include' }
        )
      
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Ошибка удаления файла')
        }
      
        // Очищаем имя файла локально
        const eq = this.equipmentList.find(e => e.id === equipmentId)
        if (eq && eq.equipment_files) {
          eq.equipment_files[`${fileType}_unique_name`] = ''
        }
      
        return await response.json()
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    async deleteEquipment(equipmentId) {
      this.loading = true
      this.error = null

      try {
        const response = await fetch(`http://localhost:8000/equipment/${equipmentId}`, {
          method: 'DELETE',
          credentials: 'include',
        })
      
        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || 'Ошибка удаления оборудования')
        }
      
        this.equipmentList = this.equipmentList.filter(eq => eq.id !== equipmentId)
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },
    
    // ========== Вспомогательные методы ==========
    
    // Сброс ошибки
    clearError() {
      this.error = null
    },
    
    // Очистка всех данных
    clearAllData() {
      this.currentUser = null
      this.users = []
      this.equipmentList = []
      this.locationsList = []
      this.typesList = []
      this.searchResults = []
      this.typeSearchResults = []
      this.isAuthenticated = false
      this.error = null
    }
  
  },
})