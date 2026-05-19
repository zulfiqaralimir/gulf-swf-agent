/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          900: "#0a0f1e",
          800: "#0d1530",
          700: "#111d42",
          600: "#1a2855",
        },
        gold: {
          400: "#f5c842",
          500: "#d4a017",
          600: "#b8860b",
        },
      },
    },
  },
  plugins: [],
};
