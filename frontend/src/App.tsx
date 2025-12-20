import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { useEffect } from "react";
import Layout from "./components/Layout";
import Toaster from "./components/Toast";
import HomePage from "./pages/HomePage";
import ScriptGenerationPage from "./pages/ScriptGenerationPage";
import ManagementPage from "./pages/ManagementPage";
import { useScriptStore } from "./stores/scriptStore";

function App() {
  const loadModels = useScriptStore((state) => state.loadModels);

  useEffect(() => {
    // Initialize dark mode from localStorage
    const theme = localStorage.getItem("theme");
    if (
      theme === "dark" ||
      (!theme && window.matchMedia("(prefers-color-scheme: dark)").matches)
    ) {
      document.documentElement.classList.add("dark");
    }

    // Load available models from API
    loadModels();
  }, [loadModels]);

  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/scripts" element={<ScriptGenerationPage />} />
          <Route path="/management" element={<ManagementPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
      <Toaster />
    </Router>
  );
}

export default App;
