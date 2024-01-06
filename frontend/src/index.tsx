import "@fontsource/inter";
import CssBaseline from "@mui/joy/CssBaseline";
import { CssVarsProvider } from "@mui/joy/styles";
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import theme from "./theme";

const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);

root.render(
  <React.StrictMode>
    <CssVarsProvider defaultMode="dark" theme={theme}>
      <CssBaseline>
        <App />
      </CssBaseline>
    </CssVarsProvider>
  </React.StrictMode>,
);
