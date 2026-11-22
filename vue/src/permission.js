//Import the router instance
import router from './router'
import {getToken} from "@/utils/auth.js";
import useUserStore from "@/stores/modules/userStore.js";
import {isReLogin} from "@/utils/request.js";
import {ElMessage} from "@/utils/toast.js";
import useRouteStore from "@/stores/modules/routeStore.js";

//Routes that can be accessed without signing in
const whiteList = ['/login', '/register']

//Check whether this route is public
const isWhiteList = (path) => {
  return whiteList.includes(path)
}

//On load failure, show the reason, sign out and return to the sign-in page
const failHandler = (err, next) => {
  isReLogin.show = false  //Reset the dialog flag so future 401 responses can prompt for sign-in
  const msg = typeof err === 'string' ? err : (err?.msg || err?.message || 'Could not load user information')
  ElMessage.error(msg)
  useUserStore().logOut().then(() => {
    next({path: '/login'})
  })
}

//Global guard that runs before every navigation
router.beforeEach((to, from, next) => {
  //Check whether the user has a token
  if (getToken()) {
    //Case 1: The user has a token and is signed in

    //Case 1.1: The user is signed in and requests sign-in or registration
    if (to.path === '/login' || to.path === '/register') {
      //Redirect signed-in users to Home
      next({path: '/'})
      return
    }

    //Case 1.2: The signed-in user requests another page
    //Use the store's dedicated loaded flag so an empty username does not affect this check
    if (!useUserStore().loaded) {
      //Fetch the user details if they have not been loaded

      //Set the reauthentication flag
      isReLogin.show = true

      //Fetch the user details
      useUserStore().getInfo().then(res => {
        //Clear the flag
        isReLogin.show = false

        //Get the route store
        useRouteStore().generateRoutes().then(accessRoutes => {
          //Generate accessible routes from the role's permissions
          accessRoutes.forEach(route => {
            router.addRoute(route) //Register the accessible routes dynamically
          })

          //Choose the redirect based on the role name
          const userRoleName = res.data.roleName
          //Redirect from the root based on the user's role. Unknown roles use the public-facing user area.
          let redirectPath = to.path
          if (to.path === '/' || to.path === '/index' || to.path === '/user') {
            redirectPath = userRoleName === 'admin' ? '/index' : '/user/home'
          }
          //The user requested a specific page
          if (redirectPath !== to.path) {
            next({ path: redirectPath, replace: true })
          } else {
            next({ ...to, replace: true })
          }
        }).catch(err => {
          //Handle dynamic route failures the same way as user details failures
          failHandler(err, next)
        })
      }).catch(err => {
        //Could not load user information. The token may have expired.
        failHandler(err, next)
      })
    } else {
      //Continue because user details are already loaded
      next()
    }
  } else {
    //The token is missing
    if (isWhiteList(to.path)) {
      //Allow public routes without sign-in
      next()
    } else {
      //Redirect all other routes to the sign-in page
      next({path: '/login'})
    }
  }
})
