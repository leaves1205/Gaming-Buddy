import axios from "axios";
import {ElMessage, ElMessageBox} from "@/utils/toast.js";
import {getToken} from '@/utils/auth'
import useUserStore from "@/stores/modules/userStore.js";

/* Global settings */

//Track whether the sign-in dialog is already open
//Use this flag during session expiry handling
export let isReLogin = { show: false }

//Set JSON as the default Axios request format
axios.defaults.headers['Content-Type'] = 'application/json;charset=utf-8'

//Create a configured Axios client
const service = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API, //Server URL from configuration
  timeout: 20000, //Fail requests without a response after 20 seconds
})

/* Reauthentication */
const handleReLogin = () => {
  //Keep at most one sign-in dialog open
  if (isReLogin.show) return

  //Mark the dialog as open
  isReLogin.show = true

  //Ask the user whether to sign in again
  ElMessageBox.confirm(
      'Your session has expired. You can stay on this page or sign in again.',
      'System Notice',
      {
        confirmButtonText: 'Sign In Again',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
  )
      .then(() => {
        //The user chose to sign in again
        isReLogin.show = false
        //Clear user details by signing out
        useUserStore().logOut().then(() => {
          //Redirect to the sign-in page after sign-out
          location.href = '/login' //Navigate the browser directly to this URL
        })
      })
      .catch(() => {
        //The user canceled
        isReLogin.show = false
      })
}

/* Request interceptor */

service.interceptors.request.use(
    config => {
      //1. Check whether this request needs authentication
      const isToken = config.headers?.isToken !== false
      const isRepeatSubmit = config.headers?.repeatSubmit !== false

      //A token is available and the request needs it
      if (getToken() && isToken) {
        //Add the token to the request header
        config.headers['Authorization'] = 'Bearer ' + getToken()
      }

      //2. Prevent duplicate submissions
      if (!isRepeatSubmit && ['post', 'put'].includes(config.method)) {
        //Skip duplicate detection for FormData uploads
        if (!(config.data instanceof FormData)) {
          //Track a timestamp per URL and request payload
          const repeatKey = 'repeat:' + config.url + ':' + JSON.stringify(config.data)
          const now = new Date().getTime()

          //Read the previous request timestamp from session storage
          const lastTime = sessionStorage.getItem(repeatKey)

          //Block repeat submissions of the same request within one second
          if (lastTime && now - Number(lastTime) < 1000) {
            //Reject a duplicate request
            const message = 'This request was just submitted. Please wait.'
            ElMessage.error(message)
            return Promise.reject(new Error(message))
          }

          //Save the timestamp to check later requests
          sessionStorage.setItem(repeatKey, String(now))
        }
      }
      //Let the request proceed
      return config;
    },
    error => {
      ElMessage.error(error)
    }
)

/* Response interceptor */
service.interceptors.response.use(
    res => {
      if (['blob'].includes(res.request.responseType)) {
        //Return the raw data without applying application response handling
        return res.data
      }

      //Read the application status code and message
      const code = res.data.code || 200
      const msg = res.data.msg || 'Operation failed'

      //Handle the response according to its status code
      if (code === 401) {
        handleReLogin()
        return Promise.reject('Your session has expired. Please sign in again.')
      }

      //The application status code differs from 200
      if (code !== 200) {
        ElMessage.error(msg)
        return Promise.reject(new Error(msg))
      }
      //Return the data on success
      return res.data
    },
    error => {
      //Handle HTTP errors such as 500 and 404
      let { message, response } = error

      //1. Handle HTTP 401
      if (response?.status === 401) {
        handleReLogin()
        return Promise.reject('Your session has expired. Please sign in again.')
      }

      //2. Translate errors and prefer explicit backend messages
      if (response) {
        //Use the backend {code, msg} message when available, such as "Invalid parameter: pageSize must be an integer"
        message = (response.data && typeof response.data.msg === 'string' && response.data.msg)
            || 'API returned HTTP ' + response.status
      } else if (message.includes('Network Error')) {
        //The network connection was lost
        message = 'Could not connect to the API'
      } else if (message.includes('timeout')) {
        //The request timed out
        message = 'The API request timed out'
      }

      //3. Show the error
      ElMessage.error(message)

      //4. Propagate the error
      return Promise.reject(error)
    }
)

//Export the configured Axios client
export default service
