<template>
  <div style="border: 1px solid #ccc; z-index: 1005;">
    <!-- Show the toolbar only when editing is enabled -->
    <Toolbar
        v-if="!props.readOnly"
        style="border-bottom: 1px solid #ccc"
        :editor="editorRef"
        :defaultConfig="toolbarConfig"
        :mode="mode"
    />
    <Editor
        style="overflow-y: hidden;"
        :style="{ height: editorHeight + 'px' }"
        v-model="content"
        :defaultConfig="editorConfig"
        :mode="mode"
        @onCreated="handleCreated"
        @onChange="handleChange"
        @onFocus="handleFocus"
        @onBlur="handleBlur"
    />
  </div>
</template>

<script setup>
import {onBeforeUnmount, ref, shallowRef, onMounted, computed, watch} from 'vue'
import { i18nChangeLanguage } from '@wangeditor/editor'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import '@wangeditor/editor/dist/css/style.css'
import { getToken } from "@/utils/auth"
import axios from 'axios'
import { ElMessage } from "@/utils/toast.js"

i18nChangeLanguage('en')

// API URL
const uploadUrl = ref(import.meta.env.VITE_APP_BASE_API + "/file/upload")
const headers = ref({
  Authorization: "Bearer " + getToken()
})

const props = defineProps({
  /* Editor content */
  modelValue: {
    type: String,
    default: ''
  },
  /* Height */
  height: {
    type: Number,
    default: 300
  },
  /* Minimum height */
  minHeight: {
    type: Number,
    default: null,
  },
  /* Read-only */
  readOnly: {
    type: Boolean,
    default: false,
  },
  /* Upload size limit (MB) */
  fileSize: {
    type: Number,
    default: 5,
  },
  /* Format (base64 or URL) */
  type: {
    type: String,
    default: "url",
  }
})

const emit = defineEmits(['update:modelValue'])

// Store the editor instance in a shallowRef
const editorRef = shallowRef()

const mode = 'default' // or 'simple'

// Content
const content = ref('')

// Subtract the toolbar height from the editor height
const editorHeight = computed(() => {
  return props.height - 45 // Approximate toolbar height is 45px
})

// Watch for content changes
watch(() => props.modelValue, (val) => {
  if (val !== content.value) {
    content.value = val || ''
  }
}, { immediate: true })

// Toolbar configuration
const toolbarConfig = {}

// Editor configuration
const editorConfig = ref({
  placeholder: 'Enter content...',
  readOnly: props.readOnly,
  autoFocus: false,
  scroll: true,
  MENU_CONF: {},
  hoverbarKeys: {
    // Custom hover menu
    text: {
      menuKeys: ['bold', 'italic', 'through', 'underline', 'code', 'sub', 'sup', 'color', 'bgColor', '|',
        'fontSize', 'fontFamily', 'justify', 'indent', '|', 'clearStyle']
    },
    link: {
      menuKeys: ['editLink', 'unLink', 'viewLink']
    }
  }
})

// Enable Markdown shortcuts
editorConfig.value.MENU_CONF['markdown'] = {
  enable: true
}

// Code block configuration
editorConfig.value.MENU_CONF['codeBlock'] = {
  language: 'javascript',  // Default language
  theme: 'default'
}

// Image upload configuration
editorConfig.value.MENU_CONF['uploadImage'] = {
  server: uploadUrl.value,
  fieldName: 'file',
  maxFileSize: props.fileSize * 1024 * 1024, // Convert to bytes
  headers: headers.value,
  onError(file, err, res) {
    console.error('Image upload error', err, res)
    ElMessage.error("Image upload failed")
  },
  onSuccess(res) {
    console.log('Image uploaded', res)
  }
}

// Custom image upload
if (props.type == 'url') {
  editorConfig.value.MENU_CONF['uploadImage'] = {
    async customUpload(file, insertFn) {
      // Custom JavaScript upload
      const formData = new FormData()
      formData.append("file", file)

      // Check file type
      const allowedTypes = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/svg+xml"]
      if (!allowedTypes.includes(file.type)) {
        ElMessage.error("Unsupported image format")
        return
      }

      // Check file size
      if (props.fileSize && file.size / 1024 / 1024 > props.fileSize) {
        ElMessage.error(`The file must be ${props.fileSize} MB or smaller`)
        return
      }

      try {
        const response = await axios.post(uploadUrl.value, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
            "Authorization": headers.value.Authorization
          }
        })

        if (response.data.code === 200) {
          // Insert the image
          insertFn(import.meta.env.VITE_APP_BASE_API + response.data.fileName, '', '')
        } else {
          ElMessage.error(`The file must be ${props.fileSize} MB or smaller`)
        }
      } catch (err) {
        ElMessage.error("Image upload failed")
        console.error('Upload failed', err)
      }
    }
  }
}

// Handle pasted images
const handlePaste = async (event) => {
  if (props.type !== 'url') return

  const editor = editorRef.value
  if (!editor) return

  // Read clipboard data
  const clipboardData = event.clipboardData || window.clipboardData
  if (!clipboardData) return

  // Check for file data
  const items = clipboardData.items
  if (items) {
    for (let i = 0; i < items.length; i++) {
      const item = items[i]
      // Check whether the file is an image
      if (item.type.indexOf('image') !== -1) {
        event.preventDefault()
        const file = item.getAsFile()
        if (file) {
          // Upload and insert the image into the editor
          try {
            const imageUrl = await uploadImage(file)
            editor.insertNode({
              type: 'image',
              src: imageUrl,
              alt: file.name,
              children: [{ text: '' }],
            })
          } catch (error) {
            console.error('Image upload failed', error)
          }
        }
        return
      }
    }
  }

  // Handle pasted HTML
  const html = clipboardData.getData('text/html')
  if (html) {
    // WangEditor handles pasted HTML automatically
    return
  }
}

// Image upload handler
const uploadImage = (file) => {
  return new Promise((resolve, reject) => {
    // Check file type
    const allowedTypes = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/svg+xml"]
    if (!allowedTypes.includes(file.type)) {
      ElMessage.error('Unsupported image format')
      return reject(new Error('Unsupported image format'))
    }

    // Check file size
    if (props.fileSize && file.size / 1024 / 1024 > props.fileSize) {
      ElMessage.error(`The file must be ${props.fileSize} MB or smaller`)
      return reject(new Error('The file exceeds the size limit'))
    }

    const formData = new FormData()
    formData.append("file", file)

    axios.post(uploadUrl.value, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        "Authorization": headers.value.Authorization
      }
    }).then(response => {
      if (response.data.code === 200) {
        resolve(import.meta.env.VITE_APP_BASE_API + response.data.data.fileName)
      } else {
        ElMessage.error('Could not insert the image')
        reject(new Error('Could not insert the image'))
      }
    }).catch(err => {
      ElMessage.error("Image upload failed")
      reject(err)
    })
  })
}


// Handle keyboard shortcuts
const handleKeyDown = (event) => {
  // Check for Ctrl + Alt + a digit from 1 to 6
  if (event.ctrlKey && event.altKey && !event.shiftKey) {
    const editor = editorRef.value
    if (!editor) return

    // Digits 1–6 select heading levels 1–6
    if (event.keyCode >= 49 && event.keyCode <= 54) { // Key codes 49 and 54 are '1' and '6'
      event.preventDefault()

      // Get the heading level (1–6)
      const level = event.keyCode - 48

      // Apply the heading level
      editor.insertNode({ type: 'header', level, children: [{ text: '' }] })
      editor.focus()
    }
  }
}

onMounted(() => {
  // Listen for paste events
  document.addEventListener('paste', handlePaste)
  // Listen for keyboard events
  document.addEventListener('keydown', handleKeyDown)
})

// Destroy the editor when the component unmounts
onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor == null) return
  editor.destroy()
  document.removeEventListener('paste', handlePaste)
  document.removeEventListener('keydown', handleKeyDown)
})

const handleCreated = (editor) => {
  console.log('editor created', editor)
  editorRef.value = editor // Store the editor instance
}

const handleChange = (editor) => {
  emit('update:modelValue', editor.getHtml())
}

const handleFocus = (editor) => {
  console.log('focus', editor)
}

const handleBlur = (editor) => {
  console.log('blur', editor)
}
</script>

<style>
.editor-img-uploader {
  display: none;
}

.w-e-toolbar {
  z-index: 1005 !important;
}

.w-e-text-container [data-slate-editor] p {
  margin: 0;
}

.editor, .ql-toolbar {
  white-space: pre-wrap !important;
  line-height: normal !important;
}

/* Code block styles */
pre.code-content {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  font-family: monospace;
}

/* Code block toolbar styles */
.w-e-bar-item button[name="codeBlock"]::after {
  content: "Code Block";
}

/* Keyboard shortcut hint styles */
.w-e-text-container [data-slate-editor] p.hint {
  color: #999;
  font-size: 12px;
}
</style>
