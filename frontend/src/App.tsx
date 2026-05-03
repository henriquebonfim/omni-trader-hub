import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import { Toaster as Sonner } from "@/shared/ui/molecules/sonner";
import { Toaster } from "@/shared/ui/molecules/toaster";
import { TooltipProvider } from "@/shared/ui/molecules/tooltip";
import { Layout } from "@/app/layout/Layout";
import Dashboard from "./pages/Dashboard";
import BotsAssets from "./pages/BotsAssets";
import Intelligence from "./pages/Intelligence";
import Charts from "./pages/Charts";
import Backtesting from "./pages/Backtesting";
import RiskMonitor from "./pages/RiskMonitor";
import TradeHistory from "./pages/TradeHistory";
import StrategyLab from "./pages/StrategyLab";
import SettingsPage from "./pages/Settings";
import { AnalyticsPage } from "./features/analytics/pages/AnalyticsPage";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";
import { getStoredApiKey } from "@/core/api";
import { useEffect, useState } from "react";

const queryClient = new QueryClient();

// Protected route component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const [isChecking, setIsChecking] = useState(true);
  const [hasAuth, setHasAuth] = useState(false);

  useEffect(() => {
    const apiKey = getStoredApiKey();
    setHasAuth(!!apiKey);
    setIsChecking(false);
  }, []);

  if (isChecking) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  if (!hasAuth) {
    return <Navigate to="/login" replace />;
  }

  return <Layout>{children}</Layout>;
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/bots" element={<BotsAssets />} />
                  <Route path="/intelligence" element={<Intelligence />} />
                  <Route path="/charts" element={<Charts />} />
                  <Route path="/backtesting" element={<Backtesting />} />
                  <Route path="/risk" element={<RiskMonitor />} />
                  <Route path="/history" element={<TradeHistory />} />
                  <Route path="/analytics" element={<AnalyticsPage />} />
                  <Route path="/strategy-lab" element={<StrategyLab />} />
                  <Route path="/settings" element={<SettingsPage />} />
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
