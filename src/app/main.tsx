import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";
import "@/core/api/firebase";

createRoot(document.getElementById("root")!).render(<App />);
