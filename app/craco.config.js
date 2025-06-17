module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // Override the HtmlWebpackPlugin configuration
      const htmlWebpackPlugin = webpackConfig.plugins.find(
        (plugin) => plugin.constructor.name === 'HtmlWebpackPlugin'
      );
      
      if (htmlWebpackPlugin) {
        htmlWebpackPlugin.options.template = './src/index.html';
      }
      
      return webpackConfig;
    },
  },
}; 