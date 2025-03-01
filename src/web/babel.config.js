module.exports = {
  presets: [
    [
      '@babel/preset-env',
      {
        targets: {
          browsers: [
            'last 2 Chrome versions',
            'last 2 Firefox versions',
            'last 2 Safari versions',
            'last 2 Edge versions',
            'not IE 11',
            '> 1%',
          ],
        },
        useBuiltIns: 'usage',
        corejs: 3,
        modules: false, // Preserve ES modules for tree shaking
        loose: true,
      },
    ],
    [
      '@babel/preset-react',
      {
        runtime: 'automatic', // Use the new JSX transform from React 17+
        development: process.env.NODE_ENV === 'development',
      },
    ],
    [
      '@babel/preset-typescript',
      {
        isTSX: true,
        allExtensions: true,
        allowDeclareFields: true,
        optimizeConstEnums: true,
      },
    ],
  ],
  plugins: [
    '@babel/plugin-transform-runtime',
    '@babel/plugin-proposal-class-properties',
    '@babel/plugin-proposal-object-rest-spread',
    '@babel/plugin-syntax-dynamic-import',
    [
      'babel-plugin-styled-components',
      {
        displayName: process.env.NODE_ENV !== 'production',
        pure: true,
      },
    ],
  ],
  // Environment-specific configurations
  env: {
    development: {
      plugins: ['react-refresh/babel'],
    },
    test: {
      presets: [
        [
          '@babel/preset-env',
          {
            targets: {
              node: 'current',
            },
            modules: 'commonjs', // Use commonjs for Jest compatibility
          },
        ],
      ],
      plugins: ['dynamic-import-node'],
    },
    production: {
      plugins: [
        'transform-react-remove-prop-types',
        '@babel/plugin-transform-react-constant-elements',
        '@babel/plugin-transform-react-inline-elements',
        [
          'babel-plugin-transform-imports',
          {
            '@material-ui/core': {
              transform: '@material-ui/core/esm/${member}',
              preventFullImport: true,
            },
            '@material-ui/icons': {
              transform: '@material-ui/icons/esm/${member}',
              preventFullImport: true,
            },
          },
        ],
      ],
    },
  },
};