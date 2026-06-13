import { configureStore } from "@reduxjs/toolkit";

// Simple slices — expand as needed
import { createSlice } from "@reduxjs/toolkit";

const alertsSlice = createSlice({
  name: "alerts",
  initialState: {
    items: [
      { id: 1, severity: "high", message: "High pest risk detected in Field Alpha", type: "pest_risk", time: "2 min ago" },
      { id: 2, severity: "medium", message: "Soil moisture below optimal threshold", type: "soil_degradation", time: "18 min ago" },
    ],
  },
  reducers: {
    dismissAlert: (state, action) => {
      state.items = state.items.filter((a) => a.id !== action.payload);
    },
    addAlert: (state, action) => {
      state.items.unshift(action.payload);
    },
  },
});

const authSlice = createSlice({
  name: "auth",
  initialState: {
    user: { name: "Admin User", email: "admin@agrivision.ai", role: "admin" },
    token: null,
  },
  reducers: {
    setUser: (state, action) => { state.user = action.payload; },
    setToken: (state, action) => { state.token = action.payload; },
    logout: (state) => { state.user = null; state.token = null; },
  },
});

export const { dismissAlert, addAlert } = alertsSlice.actions;
export const { setUser, setToken, logout } = authSlice.actions;

export const store = configureStore({
  reducer: {
    alerts: alertsSlice.reducer,
    auth: authSlice.reducer,
  },
});
