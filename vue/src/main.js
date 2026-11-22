import { createApp, defineAsyncComponent } from 'vue'
import { createPinia } from 'pinia'

import '@/assets/styles/tailwind.css'

import App from './App.vue'
import router from './router'
//Import the route guard
import './permission'

import SvgIcon from '@/components/SvgIcon'
import 'virtual:svg-icons-register'

//Pagination component
import Pagination from '@/components/Pagination'

//Custom modal component
import Modal from '@/components/Modal'

//Custom select component
import Select from '@/components/Select'

//Lazy-load the icon picker to reduce the initial bundle size
const IconSelect = defineAsyncComponent(() => import('@/components/IconSelect'))

// Lazy-load the image preview to reduce the initial bundle size
const ImagePreview = defineAsyncComponent(() => import('@/components/ImagePreview'))

// Lazy-load image upload to reduce the initial bundle size
const ImageUpload = defineAsyncComponent(() => import('@/components/ImageUpload'))

// Lazy-load file upload to reduce the initial bundle size
const FileUpload = defineAsyncComponent(() => import('@/components/FileUpload'))

// Lazy-load the rich text editor because of its size
const Editor = defineAsyncComponent(() => import('@/components/Editor'))

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.component('Pagination', Pagination)

app.component('svg-icon', SvgIcon)

app.component('IconSelect', IconSelect)

app.component('ImagePreview', ImagePreview)

app.component('ImageUpload', ImageUpload)

app.component('FileUpload', FileUpload)

app.component('Editor', Editor)

app.component('Modal', Modal)

app.component('Select', Select)

app.mount('#app')
