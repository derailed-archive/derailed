/** @type {import('tailwindcss').Config} */
const twConfig = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    // './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}'
  ],
  theme: {
    extend: {
      colors: {
        'quite-blue': '#181a1f',
        'unrailed': '#7364FF',
        'blackbird': '#979CA7',
        'quite-more-blue': '#22252b',
      },
      backgroundImage: {
        'trains-away': "url('/trains-away.jpg')"
      }
    },
  },
  plugins: [],
}

module.exports = twConfig
