/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
      colors: {
        custombg: '#2f2f2f',
        custombg1: '#1d586eba',
        custombg2: '#393938c9',
        custombg3: '#3e3e43e3',
        customtxt: '#b4b4b4',
      },
    },
  },
  plugins: [],
};
