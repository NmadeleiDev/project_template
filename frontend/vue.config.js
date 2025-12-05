const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/api': {
        target: 'http://app-local.com:80',
        changeOrigin: true
      }
    },
    allowedHosts: 'all',
  }
})
