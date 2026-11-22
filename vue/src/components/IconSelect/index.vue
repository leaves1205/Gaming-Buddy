<template>
  <!--
    Fixed-height container (200 pixels).
    This picker is often displayed in a dialog or dropdown.
    The fixed height keeps it compact and lets overflow scroll.
  -->
  <div style="height: 200px;">
    <!--
      Flex container
      display: flex -> Arrange items in a row
      flex-wrap: wrap -> Wrap items onto the next row when needed
      This container arranges the icon items
    -->
    <div style="display: flex; flex-wrap: wrap;">
      <!--
        v-for renders a div for each entry in iconList
        item is the current icon name, such as "home" or "user"
        index is the current array position (0, 1, 2...)

        :key="index":
        - Vue requires a unique key for each v-for item
        - The index is used because names are unique and their order is fixed
        - Use a stable ID when available

        class="icon-item-wrapper" applies the CSS class
        @click="selectedIcon(item)": Handle clicks
          - Call selectedIcon when the icon is clicked
          - Pass the current icon name as an argument
      -->
      <div
          v-for="(item, index) in iconList"
          class="icon-item-wrapper"
          :key="index"
          @click="selectedIcon(item)"
      >
        <!--
          Icon content container
          Contains the icon and its name
        -->
        <div class="icon-item">
          <!--
            svg-icon component
            Renders SVG icons

            :icon-class="item":
            - Pass the current icon name to svg-icon
            - svg-icon looks up and renders the matching SVG

            style="height: 25px; width: 16px;":
            - Render icons at 25px high and 16px wide
            - Keep icon dimensions consistent
          -->
          <svg-icon :icon-class="item" style="height: 25px; width: 16px;"/>

          <!--
            Display the icon name
            {{ item }} renders the icon name using Vue text interpolation.
            For example, if item is "home", the displayed text is "home".

            Why show the name?
            1. Show users what the icon is called
            2. Make icons easier to find or recognize
            3. Clarify icons whose meaning is ambiguous
          -->
          <span>{{ item }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

// Load all SVG icons dynamically
/*
  How can the picker discover every SVG icon?
  Use Vite's import.meta.glob

  What does import.meta.glob do?
  - Vite provides it as a build feature, similar to a feature in webpack
  - It imports files that match a pattern
  - It returns paths mapped to asynchronous import functions

  Example
  Suppose the icons folder contains home.svg, user.svg and settings.svg
  The modules object then looks like this
  {
    '@/assets/icons/svg/home.svg': () => import('@/assets/icons/svg/home.svg'),
    '@/assets/icons/svg/user.svg': () => import('@/assets/icons/svg/user.svg'),
    '@/assets/icons/svg/settings.svg': () => import('@/assets/icons/svg/settings.svg')
  }
*/
const modules = import.meta.glob('@/assets/icons/svg/*.svg');

// Extract icon names from file paths
/*
  The modules object contains full paths. The picker uses the icon names.
  Extract the names with string operations

  Steps
  1. Object.keys(modules) -> Get the array of file paths
    For example: ['@/assets/icons/svg/home.svg', '@/assets/icons/svg/user.svg']

  2. .map(path => ...) -> Process each path

  3. path.split('assets/icons/svg/')[1]
    For example: '@/assets/icons/svg/home.svg'.split('assets/icons/svg/')
    Result: ['@/', 'home.svg']
    Take index 1 to get 'home.svg'.

  4. .split('.svg')[0]
    For example: 'home.svg'.split('.svg')
    Result: ['home', '']
    Take index 0 to get 'home'.

  The resulting icons array contains strings such as 'home', 'user' and 'settings'.
*/
const icons = Object.keys(modules).map(path =>
    path.split('assets/icons/svg/')[1].split('.svg')[0]
);

// Icon list
const iconList = ref(icons);

/*
  Events emitted by this component
  This declares a 'selected' event.
  How does the child notify its parent?
  Call emit('eventName', argument).
  How does the parent listen?
  <icon-selector @selected="handleSelected" />
*/
const emit = defineEmits(['selected']);

/*
  Icon click handler
  Runs when the user clicks an icon

  name is the clicked icon's name

  This handler does the following
  1. Emit the 'selected' event with the icon name
     The parent receives the selected icon name

  2. document.body.click()
     Simulate a click on the document body
     Why simulate the click?
     The picker appears in a dropdown or dialog
     - Selecting an icon should close the dropdown
     - The body click triggers the existing outside-click handler
     - This tells other components that the user clicked outside
*/
const selectedIcon = (name) => {
  // Notify the parent which icon was selected
  emit('selected', name);

  // Simulate a body click to trigger dropdown dismissal
  document.body.click();
};
</script>

<style scoped>
/* Each icon container takes one-third of the width and has a fixed height */
.icon-item-wrapper {
  width: calc(100% / 3);  /* Show three icons per row */
  height: 25px;           /* Fixed height */
  line-height: 25px;      /* Vertically center the text */
  cursor: pointer;        /* Use a pointer cursor */
  display: flex;          /* Use flex layout inside */
}

/* Icon content area */
.icon-item {
  display: flex;          /* Arrange the icon and text horizontally */
  max-width: 100%;        /* Prevent content overflow */
  height: 100%;           /* Inherit the parent's height */
  padding: 0 5px;         /* Horizontal padding */
}

/* Hover state */
.icon-item:hover {
  background: #ececec;    /* Light gray background */
}
</style>
