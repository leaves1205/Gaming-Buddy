<template>
  <div class="app-container">
    <!-- Search filters -->
    <div class="flex flex-wrap items-end gap-3 mb-4">
      <div class="flex items-center gap-2">
        <label class="text-sm text-gray-600 w-[70px]">Menu name</label>
        <input v-model="query.menuName" placeholder="Enter a menu name" class="h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 w-52" @keyup.enter="handleQuery"/>
      </div>
      <div class="flex gap-2">
        <button @click="handleQuery" :disabled="loading" class="h-9 px-4 rounded-lg text-sm font-medium text-white transition-colors flex items-center gap-1" :class="loading ? 'bg-[var(--color-primary)]/50 cursor-not-allowed' : 'bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)]'">
          <svg v-if="!loading" class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <svg v-else class="w-3.5 h-3.5 animate-spin" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" class="opacity-25"/><path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>
          {{ loading ? 'Searching...' : 'Search' }}
        </button>
        <button @click="resetQuery" :disabled="loading" class="h-9 px-4 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors flex items-center gap-1" :class="{ 'opacity-50 cursor-not-allowed': loading }">
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>Reset
        </button>
      </div>
    </div>

    <!-- Action buttons -->
    <div class="flex gap-2 mb-2">
      <button @click="handleInsert" class="h-9 px-4 rounded-lg text-sm font-medium text-[var(--color-primary)] border border-[var(--color-primary)] bg-white hover:bg-[var(--color-primary-bg)] transition-colors flex items-center gap-1">
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>Add
      </button>
    </div>

    <!-- Tree table -->
    <div class="overflow-x-auto border border-gray-200 rounded-lg relative">
      <div v-if="loading" class="absolute inset-0 bg-white/60 z-10 flex items-center justify-center rounded-lg">
        <div class="flex flex-col items-center gap-2">
          <svg class="w-8 h-8 animate-spin text-[var(--color-primary)]" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-linecap="round" class="opacity-25"/><path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>
          <span class="text-sm text-gray-500">Loading...</span>
        </div>
      </div>
      <table class="w-full text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-3 py-3 text-center font-medium text-gray-600">Menu name</th>
            <th class="w-[100px] px-3 py-3 text-center font-medium text-gray-600">Icon</th>
            <th class="w-[100px] px-3 py-3 text-center font-medium text-gray-600">Order</th>
            <th class="px-3 py-3 text-center font-medium text-gray-600">Component path</th>
            <th class="w-[200px] px-3 py-3 text-center font-medium text-gray-600">Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="row in menuList" :key="row.menuId">
            <MenuTreeRow :row="row" :depth="0" @update="handleUpdate" @delete="handleDelete"/>
          </template>
          <tr v-if="menuList.length === 0">
            <td colspan="5" class="px-3 py-12 text-center text-gray-400">No results</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Dialog -->
    <Modal :title="title" v-model="open" width="600px">
      <form @submit.prevent="submitForm" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <!-- Parent menu -->
          <div class="flex items-start gap-2">
            <label class="w-[72px] pt-2 text-sm text-gray-600 text-right flex-shrink-0">Parent menu</label>
            <div class="flex-1 relative" ref="treeSelectRef">
              <div @click="treeSelectOpen = !treeSelectOpen" class="h-9 px-3 rounded-lg border border-gray-300 text-sm flex items-center justify-between cursor-pointer bg-white hover:border-gray-400 transition-colors">
                <span :class="selectedParentName ? 'text-gray-700' : 'text-gray-400'">{{ selectedParentName || 'Select a parent menu' }}</span>
                <svg class="w-3.5 h-3.5 text-gray-400 transition-transform duration-200" :class="{ 'rotate-180': treeSelectOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
              </div>
              <div v-if="treeSelectOpen" class="absolute top-full left-0 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-[200px] overflow-y-auto py-1">
                <div @click="selectParent({ menuId: 0, menuName: 'Top level' })" class="px-3 py-1.5 text-sm hover:bg-gray-50 cursor-pointer" :class="{ 'text-[var(--color-primary)] bg-[var(--color-primary-bg)]': form.parentId === 0 }">Top level</div>
                <TreeSelectNode v-for="node in menuOptions" :key="node.menuId" :node="node" :selected-id="form.parentId" @select="selectParent"/>
              </div>
            </div>
          </div>

          <!-- Menu type -->
          <div class="flex items-start gap-2">
            <label class="w-[72px] pt-2 text-sm text-gray-600 text-right flex-shrink-0">Menu type</label>
            <div class="flex gap-6 pt-2">
              <label class="flex items-center gap-1.5 text-sm cursor-pointer"><input type="radio" v-model="form.menuType" value="M"/>Directory</label>
              <label class="flex items-center gap-1.5 text-sm cursor-pointer"><input type="radio" v-model="form.menuType" value="C"/>Menu</label>
            </div>
          </div>

          <!-- Menu icon -->
          <div class="flex items-start gap-2">
            <label class="w-[72px] pt-2 text-sm text-gray-600 text-right flex-shrink-0">Menu icon</label>
            <div class="flex-1 relative" ref="popoverRef">
              <div @click="iconPopoverOpen = !iconPopoverOpen" class="h-9 px-3 rounded-lg border border-gray-300 text-sm flex items-center gap-2 cursor-pointer bg-white hover:border-gray-400 transition-colors">
                <svg-icon v-if="form.icon" :icon-class="form.icon" class="w-4 h-4"/>
                <svg v-else class="w-4 h-4 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <span :class="form.icon ? 'text-gray-700' : 'text-gray-400'">{{ form.icon || 'Select an icon' }}</span>
              </div>
              <div v-if="iconPopoverOpen" class="absolute top-full left-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 p-2" style="width:400px">
                <icon-select ref="iconSelectRef" @selected="selectedIcon"/>
              </div>
            </div>
          </div>

          <!-- Display order -->
          <div class="flex items-start gap-2">
            <label class="w-[72px] pt-2 text-sm text-gray-600 text-right flex-shrink-0">Display order</label>
            <div class="flex-1">
              <input v-model.number="form.menuSort" type="number" min="0" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
            </div>
          </div>

          <!-- Menu name -->
          <div class="flex items-start gap-2">
            <label class="w-[72px] pt-2 text-sm text-gray-600 text-right flex-shrink-0">Menu name</label>
            <div class="flex-1">
              <input v-model="form.menuName" placeholder="Enter a menu name" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
            </div>
          </div>

          <!-- Route path (menu items only) -->
          <div v-if="form.menuType === 'C'" class="flex items-start gap-2">
            <label class="w-[72px] pt-2 text-sm text-gray-600 text-right flex-shrink-0">Route path</label>
            <div class="flex-1">
              <input v-model="form.path" placeholder="Enter a route path" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
            </div>
          </div>

          <!-- Component path (menu items only) -->
          <div v-if="form.menuType === 'C'" class="flex items-start gap-2">
            <label class="w-[72px] pt-2 text-sm text-gray-600 text-right flex-shrink-0">Component path</label>
            <div class="flex-1">
              <input v-model="form.component" placeholder="Enter a component path" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
            </div>
          </div>
        </div>
      </form>
      <template #footer>
        <button @click="submitForm" class="h-9 px-5 rounded-lg text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] transition-colors">Save</button>
        <button @click="open = false" class="h-9 px-5 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors">Cancel</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import {onMounted, ref, reactive, computed, nextTick} from "vue";
import {deleteMenuByMenuId, insertMenu, selectMenuByMenuId, selectMenuList, updateMenu} from "@/api/system/menu.js";
import SvgIcon from "@/components/SvgIcon/index.vue";
import {ElMessage, ElMessageBox} from "@/utils/toast.js";
import IconSelect from "@/components/IconSelect/index.vue";
import MenuTreeRow from "./MenuTreeRow.vue";
import TreeSelectNode from "./TreeSelectNode.vue";

const iconSelectRef = ref()
const iconPopoverOpen = ref(false)
const treeSelectOpen = ref(false)

const treeSelectRef = ref(null)
const popoverRef = ref(null)

// Click outside to close
onMounted(() => {
  document.addEventListener('click', (e) => {
    if (treeSelectRef.value && !treeSelectRef.value.contains(e.target)) treeSelectOpen.value = false
    if (popoverRef.value && !popoverRef.value.contains(e.target)) iconPopoverOpen.value = false
  })
})

const selectedIcon = (name) => {
  form.icon = name
  iconPopoverOpen.value = false
}

const selectedParentName = computed(() => {
  if (form.parentId === 0 || form.parentId === '0') return 'Top level'
  return findNodeName(menuOptions.value, form.parentId)
})

const findNodeName = (nodes, id) => {
  for (const n of nodes) {
    if (n.menuId === id) return n.menuName
    if (n.children) {
      const found = findNodeName(n.children, id)
      if (found) return found
    }
  }
  return ''
}

const selectParent = (node) => {
  form.parentId = node.menuId
  treeSelectOpen.value = false
}

const title = ref('')
const open = ref(false)

const form = reactive({
  menuId: null, parentId: 0, menuName: '', icon: '', menuType: 'M', menuSort: 0, path: '', component: ''
})

const handleInsert = () => {
  Object.assign(form, { menuId: null, parentId: 0, menuName: '', icon: '', menuType: 'M', menuSort: 0, path: '', component: '' })
  if (menuOptions.value.length === 0) getTreeSelect()
  open.value = true
  title.value = 'Add a menu'
}

const handleUpdate = (row) => {
  const menuId = row.menuId
  if (menuOptions.value.length === 0) getTreeSelect()
  selectMenuByMenuId(menuId).then(res => {
    Object.assign(form, res.data)
    open.value = true
    title.value = 'Edit a menu'
  })
}

const handleDelete = (row) => {
  const menuId = row.menuId
  ElMessageBox.confirm('Delete this menu?', 'System Notice', {
    confirmButtonText: 'Confirm', cancelButtonText: 'Cancel', type: 'warning'
  }).then(() => {
    deleteMenuByMenuId(menuId).then(() => {
      ElMessage.success('Deleted successfully')
      getList()
    })
  }).catch(() => {})
}

const menuOptions = ref([])
const menuList = ref([])
const query = ref({ menuName: '' })
const loading = ref(false)

const getTreeSelect = () => {
  selectMenuList().then(res => {
    menuOptions.value = buildTree(res.data, 0)
  })
}

const submitForm = () => {
  if (form.menuId != null) {
    updateMenu({...form}).then(() => {
      ElMessage.success('Changes saved')
      open.value = false; getList()
    })
  } else {
    insertMenu({...form}).then(() => {
      ElMessage.success('Added successfully')
      open.value = false; getList()
    })
  }
}

const handleQuery = () => { getList() }
const resetQuery = () => { query.value.menuName = ''; handleQuery() }

const getList = () => {
  loading.value = true
  selectMenuList(query.value).then(res => {
    menuList.value = query.value.menuName ? res.data : buildTree(res.data, 0)
  }).finally(() => { loading.value = false })
}

const buildTree = (data, parentId) => {
  const result = []
  for (const item of data) {
    if (item.parentId === parentId) {
      const children = buildTree(data, item.menuId)
      if (children.length > 0) item.children = children
      result.push(item)
    }
  }
  return result
}

onMounted(() => getList())
</script>
