<template>
  <router-link :to="to">
    <!-- The slot renders the content inside this component's tags -->
    <slot/>
  </router-link>
</template>

<script setup>
//The to prop specifies the route to open
defineProps({
  //The to prop is the link destination
  to: {
    type: String,
    required: true
  }
})

</script>
