module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      [
        'module:react-native-dotenv',
        {
          moduleName: '@env',
          path: '.env',
          blacklist: null,
          whitelist: null,
          safe: false,
          allowUndefined: true,
        },
      ],
      // Add other plugins here if needed, e.g., 'react-native-reanimated/plugin'
      // Ensure 'react-native-reanimated/plugin' is listed last if you use it.
    ],
  };
};