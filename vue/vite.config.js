/*
This file configures Vite for the project.

1. Load settings for each environment
2. Configure plugins
3. Simplify imports with path aliases
4. Configure hot reload and request proxying for development
5. Configure the production build

Main features
- Function configuration with dynamic parameters
- Environment variable loading
- Path aliases
- Development proxy for cross-origin requests
- Extensible plugin configuration
*/

// Import the Vite utilities
import { defineConfig, loadEnv } from 'vite'
// Import Node.js path utilities
import path from 'path'
// Import the application's plugin factory
import createVitePlugins from './vite/plugins'
// Tailwind CSS
import tailwindcss from '@tailwindcss/vite'

// Export the Vite configuration
// defineConfig provides Vite type hints
export default defineConfig(({ mode, command }) => {
  // 1. Load environment variables
  // loadEnv() loads the .env file for the current mode
  // For example, development loads .env.development
  const env = loadEnv(mode, process.cwd())

  // 2. Return the Vite configuration object
  return {
    // ============== Base configuration ==============
    base: '/', // Base deployment path

    // ============== Plugins ==============
    // Create the plugins through the plugin factory
    // command === 'build' identifies production builds
    plugins: [
      tailwindcss(),
      ...createVitePlugins(env, command === 'build')
    ],

    // ============== Module resolution ==============
    resolve: {
      // Path aliases, similar to webpack alias
      alias: {
        // '~' points to the project root
        '~': path.resolve(__dirname, './'),

        // '@' points to src
        '@': path.resolve(__dirname, './src')
      },

      // Extensions that can be omitted from imports
      extensions: [
        '.mjs',  // ES module files
        '.js',   // JavaScript files
        '.json', // JSON files
        '.vue'   // Vue single-file components
      ]
    },

    // ============== Build optimization ==============
    build: {
      rollupOptions: {
        output: {
          // Split third-party libraries by purpose to avoid one large entry bundle
          manualChunks: {
            'vue-vendor': ['vue', 'vue-router', 'pinia'],  // Vue and related packages
            'axios': ['axios'],  // HTTP client
            'wangeditor': ['@wangeditor/editor', '@wangeditor/editor-for-vue']  // Separate chunk for the large rich text editor
          }
        }
      }
    },

    // ============== Development server ==============
    server: {
      // Port
      port: 90,

      // Host binding
      // true listens on all interfaces, including LAN addresses
      // A particular address can also be set, such as '0.0.0.0' or '192.168.1.100'
      host: true,

      // Open the browser when the server starts
      open: true,

      // Proxy configuration for cross-origin requests
      proxy: {
        // Proxy all requests under /base to the backend
        '/base': {
          // Target server address
          target: 'http://localhost:8080',

          // Set the Origin header to match the target
          changeOrigin: true,

          /**
           * Proxy flow
           * Frontend: http://localhost:90/base/selectUserByUserName/{userName} →
           * Vite proxy →
           * Backend: http://localhost:8080/selectUserByUserName/{userName}
           * Why use a proxy?
           * - During development the frontend and backend use different ports (90 and 8080)
           * - Browsers enforce the same-origin policy
           * - The proxy makes the backend appear under the frontend origin
           */
          rewrite: (p) => p.replace(/^\/base/, '')
        }
      }
    },
  }
})
