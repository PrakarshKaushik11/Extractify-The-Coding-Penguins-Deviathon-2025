import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import CrawlSettings from "./pages/CrawlSettings";
import Extraction from "./pages/Extraction";
import Results from "./pages/Results";
import SystemInfo from "./pages/SystemInfo";
import NotFound from "./pages/NotFound";
import Navigation from "./components/Navigation";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <div className="min-h-screen dark">
          <Navigation />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/crawl" element={<CrawlSettings />} />
            <Route path="/extraction" element={<Extraction />} />
            <Route path="/results" element={<Results />} />
            <Route path="/system" element={<SystemInfo />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
