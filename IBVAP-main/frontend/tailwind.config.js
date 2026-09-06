/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'tactical-dark': '#0a0e1a',
        'tactical-panel': 'rgba(15, 23, 42, 0.7)',
        'tactical-border': 'rgba(0, 240, 255, 0.2)',
        'cyan-accent': '#00f0ff',
        'alert-red': '#ff3366',
        'alert-amber': '#ffaa00',
        'alert-green': '#00ff88',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      backgroundImage: {
        'tactical-grid': 'linear-gradient(rgba(0, 240, 255, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 240, 255, 0.05) 1px, transparent 1px)',
      },
      backgroundSize: {
        'tactical-grid': '30px 30px',
      }
    },
  },
  plugins: [],
}
