/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,html}",  // adjust this to your project structure
  ],
  theme: {
    extend: {
      fontFamily: {
        cascadia: ['"Cascadia Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
