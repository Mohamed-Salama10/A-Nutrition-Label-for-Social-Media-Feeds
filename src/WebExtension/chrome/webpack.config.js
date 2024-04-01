const path = require('path');

module.exports = {
  entry: {
    contentScript: './JS/contentScript.js', // Replace with the entry file of your Chrome extension
    utils: './JS/utils/utils.js' // Add the path to your utils.js file
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].bundle.js', // Use [name] to generate the respective bundle names
  },
  mode: 'development', // Set to 'production' for production builds
};
