<template>
  <!-- Check whether to show the menu item -->
  <div v-if="!item.hidden">
    <!-- Render a simple menu item when it has no children -->
    <template v-if="shouldShowSingleItem">
      <app-link :to="singleItemPath">
        <el-menu-item :index="singleItemPath">
          <svg-icon :icon-class="onlyOneChild.meta.icon || (item.meta && item.meta.icon)"
                    style="margin-right: 6px"/>
          <template #title>
            <span style="margin-left: 2px">
              {{ onlyOneChild.meta.title }}
            </span>
          </template>
        </el-menu-item>
      </app-link>
    </template>

    <!-- Render an expandable menu when it has children -->
    <el-sub-menu v-else :index="resolvePath(item.path)" teleported>
      <template v-if="item.meta" #title>
        <span @click.stop="goFirstChild" style="display: flex;align-items: center">
          <svg-icon :icon-class="item.meta.icon" style="margin-right: 6px"/>
          <span style="margin-left: 2px">
                {{ item.meta.title }}
          </span>
        </span>
      </template>

      <!-- Render child menu items recursively -->
      <sidebar-item v-for="child in item.children"
                    :key="child.path"
                    :item="child"
                    :base-path="resolvePath(child.path)"
                    is-next
      />
    </el-sub-menu>
  </div>
</template>

<script setup>
import {computed} from "vue";
import {useRouter} from "vue-router";
import AppLink from "@/views/layout/components/Sidebar/AppLink.vue";
import SvgIcon from "@/components/SvgIcon/index.vue";

const router = useRouter()

const props = defineProps({
  //Menu item data is required
  item: {
    type: Object,
    required: true
  },
  //Indicates whether the call is nested
  isNext: {
    type: Boolean,
    default: false
  },
  //Base path used to build full route paths
  basePath: {
    type: String,
    default: ''
  }
})

//Recursively find the first visible leaf route
const findFirstLeaf = (node, base) => {
  //Full path of this node
  const fullPath = resolvePath(node.path, base)

  //Get visible children
  const children = (node.children || []).filter(c => !c.hidden)

  //With no children, the current node is a leaf
  if (children.length === 0) {
    return fullPath
  }

  //Search the first child for a leaf route
  return findFirstLeaf(children[0], fullPath)
}

//Open the first child when the parent is clicked
const goFirstChild = () => {
  //Get visible children
  const visibleChildren = (props.item.children || []).filter(c => !c.hidden)
  if (visibleChildren.length === 0) return

  //Start from the first child and use the current component's basePath
  const targetPath = findFirstLeaf(visibleChildren[0], props.basePath)
  if (targetPath) {
    router.push(targetPath)
  }
}

//Find the sole visible child
const onlyOneChild = computed(() => {
  //Read the children or use an empty array
  const children = props.item.children || []

  //Keep visible children
  const showingChildren = children.filter(item => !item.hidden)

  //Case 1: Exactly one child is visible
  if (showingChildren.length === 1) {
    //Return the only visible child
    return showingChildren[0]
  }

  //Case 2: No children are visible
  if (showingChildren.length === 0) {
    return {
      ...props.item, //Copy the parent item's properties
      path: '', //Use an empty path
      noShowingChildren: true //Mark the item as having no visible children
    }
  }

  //Case 3: Multiple children are visible
  return null
})

//Decide whether to render a single menu item
const shouldShowSingleItem = computed(() => {
  //1. onlyOneChild is set because there is one visible child or none
  //2. That item has no children or is marked noShowingChildren
  //3. The parent does not force an expandable menu
  return onlyOneChild.value && (!onlyOneChild.value.children || onlyOneChild.value.noShowingChildren)
      && !props.item.alwaysShow
})

//Build the destination path for a single menu item
const singleItemPath = computed(() => {
  return resolvePath(onlyOneChild.value.path)
})

//Resolve and join route paths
const resolvePath = (routePath, base) => {
  //Join the relative path to the supplied base or to props.basePath
  const basePath = base !== undefined ? base : props.basePath
  const fullPath = basePath + '/' + routePath

  //Return immediately if the path is empty
  if (!fullPath) return fullPath

  //Handle special cases
  return fullPath.replace('//', '/')
      .replace(/\/$/, '')
}

</script>

<style scoped>

</style>
