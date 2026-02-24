import type { Config } from 'tailwindcss'
export default {
  content: ['./app/**/*.{ts,tsx}','./components/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: { extend: { colors: { bg:'#0b0f14', panel:'#121923', muted:'#7f8ea3', accent:'#3b82f6' } } },
  plugins: [],
} satisfies Config
