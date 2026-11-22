<template>
  <div class="p-6 lg:p-8 max-w-[1060px] mx-auto">
    <div class="flex flex-col lg:flex-row items-start gap-6">
      <!-- Left column with the profile card -->
      <aside class="w-full lg:w-[300px] flex-shrink-0 lg:sticky lg:top-8 overflow-hidden rounded-xl border border-[var(--color-border)] bg-white shadow-[0_1px_3px_rgba(0,23,45,0.05)] profile-in">
        <!-- Brand gradient banner -->
        <div class="relative h-24 bg-gradient-to-br from-[#5cabff] via-[#409EFF] to-[#2f7be0]">
          <span class="absolute -top-10 -right-4 w-36 h-36 rounded-full bg-white/15"></span>
          <span class="absolute -bottom-12 right-12 w-24 h-24 rounded-full bg-white/10"></span>
        </div>

        <!-- Avatar and basic details -->
        <div class="px-6 pb-6 -mt-12 flex flex-col items-center">
          <div class="relative group cursor-pointer" @click="triggerUpload">
            <img :src="userStore.avatar" class="w-24 h-24 rounded-full object-cover border-[3px] border-white shadow-md bg-white" alt=""/>
            <div class="absolute inset-0 rounded-full flex flex-col items-center justify-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-black/40">
              <svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
              <span class="text-[11px] text-white">Change avatar</span>
            </div>
          </div>
          <input ref="avatarInput" type="file" accept="image/jpeg,image/png" class="hidden" @change="handleAvatarChange"/>

          <h2 class="mt-3 text-[17px] font-semibold text-[var(--color-text-dark)]">{{ state.user.userName || '—' }}</h2>
          <span class="mt-1.5 px-2.5 py-0.5 rounded-full text-[12px] font-medium"
                :class="isAdmin ? 'bg-[var(--color-primary-bg)] text-[var(--color-primary)]' : 'bg-[var(--color-bg-light)] text-[var(--color-text-medium)]'">
            {{ state.user.roleName || 'Regular User' }}
          </span>

          <div class="w-full mt-5 pt-4 border-t border-[var(--color-border-light)]">
            <div class="flex items-center justify-between text-[13px]">
              <span class="flex items-center gap-1.5 text-[var(--color-text-light)]">
                <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                Joined
              </span>
              <span class="font-medium text-[var(--color-text-dark)]">{{ state.user.createTime || '—' }}</span>
            </div>
          </div>
        </div>
      </aside>

      <!-- Right column with details and security -->
      <div class="flex-1 w-full min-w-0 space-y-6">
        <!-- Profile details -->
        <section class="rounded-xl border border-[var(--color-border)] bg-white shadow-[0_1px_3px_rgba(0,23,45,0.05)] profile-in" style="animation-delay: 60ms">
          <header class="flex items-center justify-between px-6 py-4 border-b border-[var(--color-border-light)]">
            <div class="flex items-center gap-2.5">
              <span class="w-1 h-3.5 rounded-full bg-[var(--color-primary)]"></span>
              <h3 class="text-[15px] font-semibold text-[var(--color-text-dark)]">Profile details</h3>
            </div>
            <button @click="editUserInfo" class="h-8 px-3.5 rounded-lg text-[13px] font-medium text-[var(--color-primary)] bg-[var(--color-primary-bg)] hover:bg-[#d9ecff] transition-colors">Edit profile</button>
          </header>
          <dl class="grid grid-cols-2 gap-x-8 gap-y-5 px-6 py-6">
            <div>
              <dt class="text-[13px] text-[var(--color-text-light)]">Username</dt>
              <dd class="mt-1 text-sm font-medium text-[var(--color-text-dark)]">{{ state.user.userName || '—' }}</dd>
            </div>
            <div>
              <dt class="text-[13px] text-[var(--color-text-light)]">Gender</dt>
              <dd class="mt-1 text-sm font-medium flex items-center gap-1.5 text-[var(--color-text-dark)]">
                <span class="w-1.5 h-1.5 rounded-full" :class="state.user.sex === 1 ? 'bg-[#f472b6]' : 'bg-[#409EFF]'"></span>
                {{ sexText }}
              </dd>
            </div>
            <div>
              <dt class="text-[13px] text-[var(--color-text-light)]">Role</dt>
              <dd class="mt-1">
                <span class="inline-block px-2 py-0.5 rounded-md text-[12px] font-medium"
                      :class="isAdmin ? 'bg-[var(--color-primary-bg)] text-[var(--color-primary)]' : 'bg-[var(--color-bg-light)] text-[var(--color-text-medium)]'">
                  {{ state.user.roleName || '—' }}
                </span>
              </dd>
            </div>
            <div>
              <dt class="text-[13px] text-[var(--color-text-light)]">Joined</dt>
              <dd class="mt-1 text-sm font-medium text-[var(--color-text-dark)]">{{ state.user.createTime || '—' }}</dd>
            </div>
          </dl>
        </section>

        <!-- Security -->
        <section class="rounded-xl border border-[var(--color-border)] bg-white shadow-[0_1px_3px_rgba(0,23,45,0.05)] profile-in" style="animation-delay: 120ms">
          <header class="flex items-center justify-between px-6 py-4 border-b border-[var(--color-border-light)]">
            <div class="flex items-center gap-2.5">
              <span class="w-1 h-3.5 rounded-full bg-[var(--color-primary)]"></span>
              <h3 class="text-[15px] font-semibold text-[var(--color-text-dark)]">Security</h3>
            </div>
            <button @click="editPassword" class="h-8 px-3.5 rounded-lg text-[13px] font-medium text-[var(--color-primary)] bg-[var(--color-primary-bg)] hover:bg-[#d9ecff] transition-colors">Change Password</button>
          </header>
          <div class="flex items-center gap-4 px-6 py-5">
            <span class="w-10 h-10 rounded-lg bg-[var(--color-primary-bg)] flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-[var(--color-primary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            </span>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-[var(--color-text-dark)]">Sign-in password</p>
              <p class="mt-0.5 text-[13px] text-[var(--color-text-light)]">Change your password regularly to help protect your account</p>
            </div>
          </div>
        </section>
      </div>
    </div>

    <!-- Edit profile dialog -->
    <Modal title="Edit profile" v-model="userInfoOpen" width="500px">
      <form @submit.prevent="submitUserInfo" class="space-y-4">
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">Username</label>
          <div class="flex-1">
            <input v-model="form.userName" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">Gender</label>
          <div class="flex gap-6 pt-2">
            <label class="flex items-center gap-1.5 text-sm cursor-pointer"><input type="radio" v-model="form.sex" :value="0"/>Male</label>
            <label class="flex items-center gap-1.5 text-sm cursor-pointer"><input type="radio" v-model="form.sex" :value="1"/>Female</label>
          </div>
        </div>
      </form>
      <template #footer>
        <button @click="submitUserInfo" class="h-9 px-5 rounded-lg text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] transition-colors">Save</button>
        <button @click="userInfoOpen = false" class="h-9 px-5 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors">Cancel</button>
      </template>
    </Modal>

    <!-- Change password dialog -->
    <Modal title="Change Password" v-model="pwdOpen" width="500px">
      <form @submit.prevent="submitPwd" class="space-y-4">
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">Current password</label>
          <div class="flex-1">
            <input v-model="pwdForm.oldPassword" type="password" placeholder="Enter your current password" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">New password</label>
          <div class="flex-1">
            <input v-model="pwdForm.newPassword" type="password" placeholder="Enter a new password" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
          </div>
        </div>
        <div class="flex items-start gap-3">
          <label class="w-20 pt-2 text-sm text-gray-600 text-right flex-shrink-0">Confirm password</label>
          <div class="flex-1">
            <input v-model="pwdForm.confirmPassword" type="password" placeholder="Confirm your new password" class="w-full h-9 px-3 rounded-lg border border-gray-300 text-sm outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"/>
          </div>
        </div>
      </form>
      <template #footer>
        <button @click="submitPwd" class="h-9 px-5 rounded-lg text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] transition-colors">Save</button>
        <button @click="pwdOpen = false" class="h-9 px-5 rounded-lg text-sm font-medium text-gray-600 border border-gray-300 bg-white hover:bg-gray-50 transition-colors">Cancel</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import useUserStore from "@/stores/modules/userStore.js";
import {computed, onMounted, reactive, ref} from "vue";
import {getInfo} from "@/api/login.js";
import {getToken} from "@/utils/auth.js";
import {ElMessage} from "@/utils/toast.js";
import {updateProfile, updatePwd} from "@/api/system/user.js";
import axios from "axios";

const userStore = useUserStore()
const state = reactive({ user: {} })

const isAdmin = computed(() => state.user.roleName === 'admin')
const sexText = computed(() => state.user.sex === 0 ? 'Male' : state.user.sex === 1 ? 'Female' : '—')

// ---------- Change password ----------
const pwdOpen = ref(false)
const pwdForm = ref({ oldPassword: '', newPassword: '', confirmPassword: '' })

const editPassword = () => {
  pwdForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
  pwdOpen.value = true
}

const submitPwd = () => {
  if (!pwdForm.value.oldPassword || !pwdForm.value.newPassword) {
    ElMessage.error('Complete all password fields')
    return
  }
  if (pwdForm.value.newPassword !== pwdForm.value.confirmPassword) {
    ElMessage.error('The passwords do not match')
    return
  }
  updatePwd({...pwdForm.value}).then(() => {
    pwdOpen.value = false
    ElMessage.success('Password changed. Please sign in again.')
    //The backend revoked the current token. Clear the local session and return to sign-in.
    userStore.logOut().then(() => { location.href = '/login' })
  })
}

// ---------- Edit profile ----------
const userInfoOpen = ref(false)
const form = ref({})

const editUserInfo = () => {
  form.value = { userName: state.user.userName, sex: state.user.sex }
  userInfoOpen.value = true
}

const submitUserInfo = () => {
  updateProfile({...form.value}).then(() => {
    userInfoOpen.value = false
    ElMessage.success('Changes saved')
    getUser()
    userStore.name = form.value.userName
  })
}

// ---------- Avatar upload ----------
const avatarInput = ref(null)

const triggerUpload = () => { avatarInput.value?.click() }

const handleAvatarChange = async (e) => {
  const file = e.target.files[0]
  if (!file) return

  const isJpg = file.type === 'image/jpeg' || file.type === 'image/png'
  if (!isJpg) {
    ElMessage.error('Avatar images must be JPG or PNG')
    return
  }

  const formData = new FormData()
  formData.append('file', file)
  const uploadUrl = import.meta.env.VITE_APP_BASE_API + "/system/user/profile/avatar"

  try {
    const res = await axios.post(uploadUrl, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': 'Bearer ' + getToken()
      }
    })
    if (res.data.code === 200) {
      userStore.avatar = import.meta.env.VITE_APP_BASE_API + res.data.imgUrl
    } else {
      ElMessage.error(res.data.msg || 'Could not save changes')
    }
  } catch {
    ElMessage.error('Upload failed')
  } finally {
    // Allow selecting the same image again
    e.target.value = ''
  }
}

// ---------- Load data ----------
const getUser = () => {
  getInfo().then(res => {
    state.user = res.data
  })
}

onMounted(() => { getUser() })
</script>

<style scoped>
.profile-in {
  animation: profile-in 0.4s ease-out both;
}
@keyframes profile-in {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
