import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles/globals.css"; // adjust path if your css file name differs

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
