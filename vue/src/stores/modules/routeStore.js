import {defineStore} from "pinia";
import {getRouters} from "@/api/system/menu.js";
import { constantRouters } from '@/router/index.js'
import Layout from '@/views/layout/index.vue'
import ParentView from '@/views/layout/components/ParentView.vue'

//Use Vite to discover all .vue files under views
const modules = import.meta.glob('./../../views/**/*.vue')

//Build a view path to loader map once, such as system/user/index, for repeated lookups
const viewModules = {}
for (const path in modules) {
  //Map ./../../views/system/user/index.vue to its relative key system/user/index
  viewModules[path.split('views/')[1].split('.vue')[0]] = modules[path]
}

const useRouteStore = defineStore(
    'permission', //This key must be globally unique
    {
      state: () => ({
        sidebarRouters: [], //Store static and user-specific routes for the sidebar
      }),
      actions: {
        //Generate the user's accessible routes
        generateRoutes() {
          return new Promise((resolve, reject) => {
            //Fetch routes from the backend and reject on failure so the guard does not hang
            getRouters().then(res => {
              //Convert backend data into frontend route records
              const sidebarRoutes = convertToRoutes(res.data);

              //The sidebar displays static and user-specific routes
              this.sidebarRouters = constantRouters.concat(sidebarRoutes)

              //Return the processed routes to the caller
              resolve(sidebarRoutes);
            }).catch(err => reject(err))
          })
        }
      }
    }
)

/**
 * Convert backend data into frontend route records
 * Example backend format
 * [
 *   {
 *     "name": "System",
 *     "path": "/system/xxx",
 *     "component": "Layout",
 *     "children": [...]
 *   }
 * ]
 *
 * Expected frontend format
 * [
 *   {
 *     "name": "System",
 *     "path": "/system/xxx",
 *     "component": Layout component object,
 *     "children": [...]
 *   }
 * ]
 *
 * @param routes Route records returned by the backend
 */
const convertToRoutes = (routes) => {
  //Process each route
  return routes.map(route => {
    //1. Resolve component names to components
    if (route.component){
      if (route.component === 'Layout') {
        //Use the imported main layout for Layout
        route.component = Layout
      } else if (route.component === 'ParentView') {
        //Parent wrapper that only renders child routes
        route.component = ParentView
      } else {
        //Load page components dynamically
        //For example, resolve 'system/user/index' to its Vue component
        route.component = loadView(route.component)
      }
    }

    //2. Process child routes recursively
    if (route.children && route.children.length ) {
      //Continue processing child routes
      route.children = convertToRoutes(route.children)
    } else {
      //Remove children when there are no child routes
      delete route.children
    }

    return route
  })
}

//Load the view component dynamically
const loadView = (view) => {
  //Look up the view in the prebuilt map and use the 404 page if it is missing
  return viewModules[view] || (() => import('@/views/404.vue'))
}

//Export the store for other modules
export default useRouteStore
