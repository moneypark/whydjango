module.exports = {
    "extends": "standard",
    "installedESLint": true,
    "globals": {
        "gettext": false
    },
    "plugins": [
        "standard",
        "promise"
    ],
    "rules": {
        "indent": ["error", 4],
        "semi": ["error", "always"],
        "space-before-function-paren": ["off"],
        "one-var": ["off"],
        "camelcase": ["off"],
        "padded-blocks": ["off"],
        "brace-style": ["warn"],
        "no-redeclare": ["warn"],
        "no-multi-str": ["warn"],
        "operator-linebreak": ["warn"]
    }
};
