/**
 * Central Vite plugin factory for the frontend
 */

//Import the Vue Vite plugin
import vue from '@vitejs/plugin-vue'

import createSvgIcon from './svg-icon'

export default function createVitePlugins(viteEnv, isBuild = false) {
  //1. Initialize the plugin array with Vue
  //vue() enables Vue 3 single-file components in Vite
  const vitePlugins = [vue()]

  //2. Add the auto-import plugin
  vitePlugins.push(createSvgIcon())

  //3. Return the plugins
  return vitePlugins;
}
