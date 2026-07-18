import js from "@eslint/js";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";

export default [
  {
    ignores: ["dist/", "node_modules/"],
  },
  js.configs.recommended,
  {
    plugins: {
      react,
      "react-hooks": reactHooks,
    },
    rules: {
      "react/react-in-jsx-scope": "off", // Not needed in modern React/Vite
      "no-unused-vars": "warn",
    },
    settings: {
      react: { version: "detect" },
    },
  },
];
