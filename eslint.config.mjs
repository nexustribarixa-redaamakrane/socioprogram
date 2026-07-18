import js from "@eslint/js";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import globals from "globals"; // Add this import

export default [
  {
    ignores: ["dist/", "node_modules/", "vite.config.js"],
  },
  js.configs.recommended,
  {
    languageOptions: {
      globals: {
        ...globals.browser, // This tells ESLint "Assume fetch, console, etc., exist"
      },
    },
    plugins: {
      react,
      "react-hooks": reactHooks,
    },
    rules: {
      "react/react-in-jsx-scope": "off",
      "no-unused-vars": "warn",
    },
    settings: {
      react: { version: "detect" },
    },
  },
];
