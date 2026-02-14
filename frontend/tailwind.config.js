/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        critical: '#ff1744',
        high: '#ff5722',
        medium: '#ff9800',
        low: '#4caf50',
      },
      backgroundImage: {
        'gradient-dark': 'linear-gradient(135deg, #0f0c29, #302b63, #24243e)',
      },
    },
  },
  plugins: [],
}
