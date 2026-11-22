import {createRouter, createWebHistory} from 'vue-router'
//Import the layout component
import Layout from '@/views/layout'

//Route configuration
export const constantRouters = [
  {
    path: '/login',
    component: () => import('@/views/login'),
    hidden: true
  },
  {
    path: '/register',
    component: () => import('@/views/register'),
    hidden: true
  },
  {
    path: '/:pathMatch(.*)*',
    component: () => import('@/views/404'),
    hidden: true
  },
  {
    // Use /profile under Layout for the admin profile so it has a distinct URL from /user/profile
    path: '/profile',
    component: Layout,
    hidden: true,
    children: [
      {
        path: '',
        name: 'Profile',
        component: () => import('@/views/system/user/profile'),
        meta: {title: 'Profile'}
      },
    ]
  },
  {
    path: '/user',
    component: () => import('@/views/userPage/index'),
    redirect: '/user/home',
    hidden: true,
    children: [
      {
        path: 'home',
        component: () => import('@/views/userPage/home'),
        hidden: true,
      },
      {
        path: 'self',
        component: () => import('@/views/system/user/profile'),
        hidden: true,
      },
      // {
      //   path: 'profile',
      //   component: () => import('@/views/userPage/profile'),
      //   hidden: true,
      // },
    ]
  }
]

//Create the router
const router = createRouter({
  history: createWebHistory(),
  routes: constantRouters,
  scrollBehavior(to, from, savedPosition) {
    //Configure scroll positioning for console navigation
    if (savedPosition) {
      //Restore the saved scroll position when available
      return savedPosition
    }
    //Otherwise scroll to the top
    return {top: 0}
  }
})

export default router
