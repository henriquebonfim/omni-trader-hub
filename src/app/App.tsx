import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/core/ui/sonner";
import { Toaster } from "@/core/ui/toaster";
import { TooltipProvider } from "@/core/ui/tooltip";
import { MainLayout } from "@/core/layouts/MainLayout";
import { useMockLiveFeed } from "@/core/api/ws";
import Dashboard from "@/domains/trading/pages/Dashboard";
import Intelligence from "@/domains/market-analysis/pages/Intelligence";
import ChartAnalysis from "@/domains/market-analysis/pages/ChartAnalysis";
import Backtesting from "@/domains/backtesting/pages/Backtesting";
import TradeExecution from "@/domains/trading/pages/TradeExecution";
import RiskMonitor from "@/domains/risk-management/pages/RiskMonitor";
import TradeHistory from "@/domains/trading/pages/TradeHistory";
import Configuration from "@/domains/system/pages/Configuration";
import NotFound from "./NotFound";

const queryClient = new QueryClient();

function AppContent() {
  const { message, status } = useMockLiveFeed();

  return (
    <MainLayout wsStatus={status}>
      <Routes>
        <Route path="/" element={<Dashboard data={message} />} />
        <Route path="/intelligence" element={<Intelligence data={message} />} />
        <Route path="/charts" element={<ChartAnalysis />} />
        <Route path="/backtesting" element={<Backtesting />} />
        <Route path="/execution" element={<TradeExecution data={message} />} />
        <Route path="/risk" element={<RiskMonitor data={message} />} />
        <Route path="/history" element={<TradeHistory />} />
        <Route path="/config" element={<Configuration />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </MainLayout>
  );
}

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
