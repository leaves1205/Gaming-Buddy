<template>
  <svg aria-hidden="true" class="scg-icon">
    <use :href="iconName" :fill="color" />
  </svg>
</template>

<script setup>
import {computed} from "vue";

const props = defineProps({
  iconClass: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: ''
  }
})

// Keep the original icon IDs from existing database records working.
const legacyIconNames = new Map([
  ['\u9996\u9875', 'home'],
  ['\u7cfb\u7edf\u7ba1\u7406', 'system-management'],
  ['\u7528\u6237\u7ba1\u7406', 'user-management'],
  ['\u89d2\u8272\u7ba1\u7406', 'role-management'],
  ['\u83dc\u5355\u7ba1\u7406', 'menu-management']
])

const iconName = computed(() => `#icon-${legacyIconNames.get(props.iconClass) ?? props.iconClass}`)
</script>

<style scoped>
.scg-icon {
  font-size: 25px;
  width: 1em;
  height: 1em;
  position: relative;
  fill: currentColor;
  vertical-align: -2px;
}
</style>
