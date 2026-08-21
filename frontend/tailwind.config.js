/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'neon-blue': '#00C8FF',
        'dark-bg': '#050505',
        'dark-card': '#101114',
        'dark-border': '#1a1a1f',
      },
    },
  },
  plugins: [],
}
