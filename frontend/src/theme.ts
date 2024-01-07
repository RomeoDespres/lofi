import { extendTheme } from "@mui/joy/styles";

const theme = extendTheme({
  colorSchemes: {
    dark: {
      palette: {
        background: {
          body: "#101418",
          level1: "rgba(0, 7, 14, 0.75)",
          level2: "rgba(20, 26, 31, 0.8)",
        },
        primary: {
          50: "#F0F7FF",
          100: "#C2E0FF",
          200: "#99CCF3",
          300: "#66B2FF",
          400: "#3399FF",
          500: "#007FFF",
          600: "#0072E5",
          700: "#0059B2",
          800: "#004C99",
          900: "#003A75",
        },
      },
    },
  },
});

export default theme;
