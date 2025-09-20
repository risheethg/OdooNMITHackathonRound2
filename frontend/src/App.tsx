import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import SignUp from "./pages/SignUp";
import ForgotPassword from "./pages/ForgotPassword";
import Dashboard from "./pages/Dashboard";
import WorkOrders from "./pages/WorkOrders";
import WorkCenters from "./pages/WorkCenters";
import StockLedger from "./pages/StockLedger";
import BOM from "./pages/BOM";
import Analytics from "./pages/Analytics";
import AppLayout from "./components/layout/AppLayout";
import NotFound from "./pages/NotFound";
import { Root } from "./Root";
import ProtectedRoute from "./ProtectedRoute";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route element={<Root />}>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />

            {/* Protected routes */}
            <Route element={<ProtectedRoute />}>
              <Route path="/" element={<AppLayout />}>
                <Route index element={<Dashboard />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="work-orders" element={<WorkOrders />} />
                <Route path="work-centers" element={<WorkCenters />} />
                <Route path="stock-ledger" element={<StockLedger />} />
                <Route path="bom" element={<BOM />} />
                <Route path="analytics" element={<Analytics />} />
              </Route>
            </Route>

            {/* Catch-all Route */}
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
