/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        cream: "#ffedd7",
        ink: "#100904",
        brown: "#382416",
        greyBrown: "#6c5f51",
        green: "#445231",
        greenLight: "#5d6c49",
        greenLightest: "#f6e0c6",
        orange: "#dc5000",
      },
      fontFamily: {
        display: ['"Archivo"', "system-ui", "sans-serif"],
        text: ['"Archivo"', "system-ui", "sans-serif"],
        mono: ['"DM Mono"', "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
}
