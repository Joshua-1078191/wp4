const path = require('path');

module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // Override the HtmlWebpackPlugin configuration
      const htmlWebpackPlugin = webpackConfig.plugins.find(
        (plugin) => plugin.constructor.name === 'HtmlWebpackPlugin'
      );
      
      if (htmlWebpackPlugin) {
        htmlWebpackPlugin.options.template = path.resolve(__dirname, 'src/index.html');
        // Override the public path
        webpackConfig.output.publicPath = '/';
      }
      
      return webpackConfig;
    },
  },
  // Override the paths configuration
  paths: {
    appPublic: path.resolve(__dirname, 'src'),
    appHtml: path.resolve(__dirname, 'src/index.html'),
  },
}; 