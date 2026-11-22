<template>
<div class="min-h-screen flex items-center justify-center bg-[var(--color-bg-page)]">
  <div class="text-center">
    <h1 class="text-7xl font-bold text-[var(--color-text-light)] mb-2">404</h1>
    <p class="text-base text-[var(--color-text-medium)] mb-8">Page not found</p>
    <button @click="router.go(-1)"
      class="inline-flex items-center justify-center h-10 px-6 rounded-lg text-sm font-medium text-white bg-[var(--color-primary)] hover:bg-[var(--color-primary-dark)] transition-colors cursor-pointer">
      Go Back
    </button>
  </div>
</div>
</template>

<script setup>
import {useRouter} from "vue-router";

// Router instance
const router = useRouter()
</script>
