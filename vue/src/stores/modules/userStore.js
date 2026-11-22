import {defineStore} from "pinia";
import {getToken, removeToken, setToken} from "@/utils/auth.js";
import {getInfo, login, logout} from "@/api/login.js";
import defaultAvatar from '@/assets/images/profile.jpg'

const useUserStore = defineStore(
    'user', //This key must be globally unique
    {
      //State
      state: () => ({
        token: getToken(), //Authentication token
        id: '', //User ID
        name: '', //Username
        avatar: '', //User avatar URL
        sex: null, //Gender (0 = male, 1 = female, null = private), shown on the user profile
        createTime: '', //Registration time (yyyy-MM-dd HH:mm:ss) used to calculate days since joining
        roleName: '', //Role name (admin, companion, or user) used to select the page view
        loaded: false //The route guard uses this flag to tell whether user details are loaded, even if the username is empty
      }),

      //Actions
      actions: {
        /**
         * Sign in
         * Send the sign-in request and save the token
         */
        login(userInfo) {
          //Return a Promise for the asynchronous operation
          return new Promise((resolve, reject) => {
            //Call the sign-in endpoint
            login(userInfo).then(res => {
              //Sign-in succeeded
              //1. Save the token locally so it survives a refresh
              setToken(res.token)

              //2. Update the token in the store
              this.token = res.token

              //3. Resolve the promise
              resolve()

            }).catch(error => {
              //Sign-in failed
              reject(error)
            })
          })
        },

        /**
         * Load user details
         * Fetch the user ID, name, avatar and other details
         */
        getInfo() {
          return new Promise((resolve, reject) => {
            //Call the user details endpoint
            getInfo().then(res => {
              //Read the user details from the response
              const user = res.data

              //Resolve the avatar URL
              let avatar = user.avatar || ""

              //Check whether the avatar URL contains http:// or https://
              if (avatar.indexOf('http://') === -1 && avatar.indexOf('https://') === -1) {
                //The avatar URL is relative
                if (avatar) {
                  avatar = import.meta.env.VITE_APP_BASE_API + avatar
                } else {
                  //Use the default avatar if none was supplied
                  avatar = defaultAvatar
                }
              }

              //Update user details
              this.id = user.userId
              this.name = user.userName
              this.avatar = avatar
              this.sex = user.sex ?? null
              this.createTime = user.createTime || ''
              this.roleName = user.roleName || ''
              this.loaded = true //Mark user details as loaded

              //3. Resolve the promise
              resolve(res) //Return the full response
            }).catch(error => {
              //Could not load user details
              reject(error)
            })
          })
        },

        /**
         * Sign out
         * Clear local state even if the backend sign-out request fails
         */
        logOut() {
          return new Promise(resolve => {
            //Call the sign-out endpoint. A failure does not block local cleanup.
            logout().catch(() => {}).finally(() => {
              //1. Clear the token and reset session fields in the store
              this.token = ''
              this.loaded = false
              this.roleName = ''
              this.sex = null
              this.createTime = ''

              //2. Remove the locally stored token
              removeToken()

              //3. Resolve after local cleanup
              resolve()
            })
          })
        }
      }
    }
)

//Export the store for other modules
export default useUserStore
