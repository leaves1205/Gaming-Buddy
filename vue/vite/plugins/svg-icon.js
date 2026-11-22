//Import the plugin factory
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
//Import path for file path handling
import path from 'path'

/**
 * Create the SVG icon plugin configuration
 */
export default function createSvgIcons() {
  return createSvgIconsPlugin({
    // Icon directory paths
    iconDirs: [path.resolve(process.cwd(), 'src/assets/icons/svg')],
    // Icon ID naming convention
    symbolId: 'icon-[dir]-[name]'
  })
}
