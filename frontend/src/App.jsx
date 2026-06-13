import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Provider } from "react-redux";
import { store } from "./store";
import Layout from "./components/layout/Layout";
import Dashboard from "./pages/Dashboard";
import CropHealth from "./pages/CropHealth";
import SoilAnalysis from "./pages/SoilAnalysis";
import PestPrediction from "./pages/PestPrediction";
import Forecasting from "./pages/Forecasting";
import Reports from "./pages/Reports";
import Admin from "./pages/Admin";

export default function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/crop-health" element={<CropHealth />} />
            <Route path="/soil-analysis" element={<SoilAnalysis />} />
            <Route path="/pest-prediction" element={<PestPrediction />} />
            <Route path="/forecasting" element={<Forecasting />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </Provider>
  );
}
