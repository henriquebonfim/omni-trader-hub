import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { MainLayout } from "@/components/layout/MainLayout";
import { useMockLiveFeed } from "@/lib/ws";
import Dashboard from "./pages/Dashboard";
import Intelligence from "./pages/Intelligence";
import ChartAnalysis from "./pages/ChartAnalysis";
import Backtesting from "./pages/Backtesting";
import TradeExecution from "./pages/TradeExecution";
import RiskMonitor from "./pages/RiskMonitor";
import TradeHistory from "./pages/TradeHistory";
import Configuration from "./pages/Configuration";
import NotFound from "./pages/NotFound";

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
