import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Layout } from "@/components/layout/Layout";
import Dashboard from "./pages/Dashboard";
import BotsAssets from "./pages/BotsAssets";
import Intelligence from "./pages/Intelligence";
import Charts from "./pages/Charts";
import Backtesting from "./pages/Backtesting";
import RiskMonitor from "./pages/RiskMonitor";
import TradeHistory from "./pages/TradeHistory";
import StrategyLab from "./pages/StrategyLab";
import SettingsPage from "./pages/Settings";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/bots" element={<BotsAssets />} />
            <Route path="/intelligence" element={<Intelligence />} />
            <Route path="/charts" element={<Charts />} />
            <Route path="/backtesting" element={<Backtesting />} />
            <Route path="/risk" element={<RiskMonitor />} />
            <Route path="/history" element={<TradeHistory />} />
            <Route path="/strategy-lab" element={<StrategyLab />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
