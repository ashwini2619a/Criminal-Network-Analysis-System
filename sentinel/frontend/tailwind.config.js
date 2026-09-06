/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'ui-sans-serif', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'monospace'],
      },
      colors: {
        surface: {
          ground: '#f8fafc',
          panel: '#ffffff',
          card: '#ffffff',
          'card-hover': '#f8fafc',
          'card-elevated': '#ffffff',
          border: 'rgba(226, 232, 240, 0.9)',
          'border-accent': 'rgba(14, 165, 233, 0.35)',
        },
        primary: {
          DEFAULT: '#0284c7',
          light: '#38bdf8',
          dark: '#0369a1',
          foreground: '#ffffff',
        },
        azure: {
          DEFAULT: '#0284c7',
          glow: '#38bdf8',
          muted: 'rgba(14, 165, 233, 0.08)',
          border: 'rgba(14, 165, 233, 0.25)',
        },
        crimson: {
          DEFAULT: '#e11d48',
          glow: '#fb7185',
          muted: 'rgba(225, 29, 72, 0.08)',
          border: 'rgba(225, 29, 72, 0.25)',
        },
        amber: {
          DEFAULT: '#d97706',
          glow: '#fbbf24',
          muted: 'rgba(217, 119, 6, 0.08)',
          border: 'rgba(217, 119, 6, 0.25)',
        },
        emerald: {
          DEFAULT: '#059669',
          glow: '#34d399',
          muted: 'rgba(5, 150, 105, 0.08)',
          border: 'rgba(5, 150, 105, 0.25)',
        },
        indigo: {
          DEFAULT: '#4f46e5',
          glow: '#818cf8',
          muted: 'rgba(79, 70, 229, 0.08)',
          border: 'rgba(79, 70, 229, 0.25)',
        },
        cyber: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        }
      },
      boxShadow: {
        'glow-sm': '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 0 12px -2px rgba(2, 132, 199, 0.15)',
        'glow-md': '0 4px 14px -2px rgba(0, 0, 0, 0.08), 0 0 20px -3px rgba(2, 132, 199, 0.2)',
        'glow-red': '0 2px 8px -1px rgba(225, 29, 72, 0.25)',
        'glow-amber': '0 2px 8px -1px rgba(217, 119, 6, 0.25)',
        'glow-emerald': '0 2px 8px -1px rgba(5, 150, 105, 0.25)',
        'card-elevated': '0 4px 20px -2px rgba(15, 23, 42, 0.06), 0 2px 6px -1px rgba(15, 23, 42, 0.04)',
        'chat-widget': '0 20px 40px -8px rgba(15, 23, 42, 0.18), 0 0 0 1px rgba(2, 132, 199, 0.15)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
        'fade-in-up': 'fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-in': 'slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-up': 'slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
        'scale-in': 'scaleIn 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
        'pulse-subtle': 'pulseSubtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-emerald': 'pulseEmerald 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2.5s infinite linear',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { transform: 'translateX(-10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(14px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.96)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.65' },
        },
        pulseEmerald: {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 0 0 rgba(5, 150, 105, 0.5)' },
          '50%': { opacity: '0.85', boxShadow: '0 0 0 6px rgba(5, 150, 105, 0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-3px)' },
        }
      }
    },
  },
  plugins: [],
}
