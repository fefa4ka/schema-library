const path = require('path')

module.exports = {
    plugins: {
        'postcss-import': {},
        'postcss-mixins': {
            mixinsFiles: path.join(__dirname, 'src/components', "**/*.mixin") // https://github.com/postcss/postcss-mixins#mixinsfiles
        },
        'postcss-simple-vars': {},
        'postcss-cssnext': {}
    }
};
