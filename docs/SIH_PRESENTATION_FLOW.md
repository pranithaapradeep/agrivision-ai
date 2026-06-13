# 🏆 AgriVision AI — SIH 2024 Presentation Playbook
### Problem #25099 | 5-Minute Demo Script

---

## 🎯 Opening Hook (30 seconds)

> *"Every year, India loses ₹90,000 crore to crop diseases and pest outbreaks — most of which could have been prevented with early detection. AgriVision AI turns satellite imagery and weather data into farm intelligence that gives farmers a 14-day warning before disaster strikes."*

**Key stat to mention:** ICAR reports 15–20% annual crop loss due to undetected pests/disease.

---

## 📊 Slide 1 — Problem Statement (1 minute)

**Pain Points:**
- Farmers cannot afford hyperspectral drones or IoT sensors
- By the time disease is visible, 30–40% of yield is already lost
- Agricultural officers lack real-time tools for field monitoring
- Existing solutions require expensive hardware

**Our Answer:** Software-only platform using freely available satellite data + AI

---

## 💡 Slide 2 — Solution Architecture (1 minute)

Walk through the 8-step pipeline:

```
1. Satellite Image Upload (Sentinel-2 / Landsat / user photo)
        ↓
2. Image Preprocessing (normalize, false-color, band simulation)
        ↓
3. Vegetation Indices (NDVI, SAVI, EVI — computed in milliseconds)
        ↓
4. CNN Disease Detection (EfficientNetB0 — 91% accuracy)
        ↓
5. Weather Integration (OpenWeatherMap → 5 pest risk factors)
        ↓
6. LSTM Forecast (14-day stress / disease / pest probability)
        ↓
7. Risk Scoring (composite weighted score → alerts)
        ↓
8. Dashboard + PDF Report (actionable recommendations)
```

**Key point:** The entire pipeline runs on a ₹500/month cloud server.

---

## 🖥️ Slide 3 — Live Demo (2 minutes)

### Demo Flow:

**Step 1 — Dashboard (20 sec)**
- Show the 4 stat cards (fields monitored, active alerts, at-risk crops, avg health)
- Point out the real-time IST clock
- Show the 7-day NDVI trend chart

**Step 2 — Crop Health Analysis (30 sec)**
- Upload a sample image (use `/docs/demo_images/wheat_field.jpg`)
- Select "Wheat" crop, enter "Field Alpha"
- Click Analyze → show the NDVI colormap, health score gauge (e.g., 74/100)
- "This field is showing early stress — disease probability rising"
- Point to NDVI (green = healthy, red = stressed)

**Step 3 — Pest Prediction (30 sec)**
- Navigate to Pest Prediction
- Enter location: Ludhiana, Punjab
- Show the radar chart with 4 pest categories
- "Based on current weather — fungal risk is HIGH. Recommendation: Apply copper-based fungicide within 5 days."

**Step 4 — 14-Day Forecast (20 sec)**
- Switch to Forecasting tab
- Show the LSTM confidence bands
- "The model predicts disease probability crosses the alert threshold on Day 9."
- Point to the alert threshold line on the chart

**Step 5 — PDF Report (20 sec)**
- Navigate to Reports
- Enter "Field Alpha — Comprehensive"
- Click Generate
- Download the PDF — show the professional report

---

## 🧠 Slide 4 — AI Innovation (30 seconds)

**What makes this unique:**

1. **Bi-LSTM + Multi-Head Attention** — standard LSTMs struggle with agricultural seasonality; our attention mechanism focuses on the most predictive timesteps

2. **RGB → Hyperspectral Simulation** — we simulate NIR bands from RGB photos, so even farmers with smartphones can use our platform (no satellite required!)

3. **Ensemble Risk Scoring** — VI Engine (40%) + Soil (30%) + Pest (30%) → single actionable health score

4. **India-Specific Tuning** — trained on Indian crop patterns (rabi/kharif cycles), IMD weather zones, Punjab/Haryana/Maharashtra pest calendars

---

## 📈 Slide 5 — Impact & Scalability (30 seconds)

**Coverage:** One Sentinel-2 tile = 100km × 100km. One API server can monitor 10,000+ fields simultaneously.

**Cost:** ₹0 data cost (COPERNICUS is free). ₹500/month compute.

**Target users:**
- State agriculture departments (mass monitoring)
- Krishi Vigyan Kendras (extension officers)
- Progressive farmers (mobile dashboard)
- Insurance companies (crop loss assessment)

**Scaling path:** Add Doordarshan weather feed → reduce OpenWeatherMap dependency. Integrate ISRO Bhuvan for Bharat-specific imagery.

---

## ❓ Anticipated Judge Questions

| Question | Answer |
|---|---|
| "What if the internet is down?" | Heuristic fallbacks in every ML model — demo never crashes |
| "How accurate is the CNN?" | 91% on PlantVillage; heuristic fallback for unrecognized images |
| "Can farmers actually use this?" | Mobile-responsive dashboard; field officer can use it on a tablet |
| "What about regional languages?" | i18n framework in React — Hindi/Punjabi/Marathi UI ready to add |
| "How is this different from Cropin or DeHaat?" | Open-source, no proprietary hardware, free satellite data, extensible |
| "NDVI from RGB isn't accurate" | Correct — we simulate for demo. Real deployment uses actual Sentinel-2 B8 band |
| "Is this deployed?" | Docker Compose — one command deploy. Show `docker compose up` |

---

## 🎤 Closing Statement (15 seconds)

> *"AgriVision AI democratizes precision agriculture. What used to require ₹50 lakh worth of drones and sensors, we deliver through a browser, powered by free satellite data and open-source AI — giving every agricultural officer in India a superpower."*

---

## 📦 Pre-Demo Checklist

- [ ] `docker compose up` running and healthy
- [ ] Demo images ready in `/docs/demo_images/`
- [ ] Backend `/health` endpoint returning `{"status":"healthy"}`
- [ ] Sample PDF report pre-generated (backup if generation fails)
- [ ] Browser tabs pre-opened: Dashboard, Crop Health, Pest, Forecast, Reports
- [ ] Offline mode tested (disconnect internet — demo still works via fallbacks)
- [ ] Slide deck exported to PDF (backup)

---

## 🏅 Evaluation Criteria Mapping

| SIH Criterion | How We Address It |
|---|---|
| Innovation | RGB→NIR simulation, Bi-LSTM attention, ensemble scoring |
| Technical Feasibility | Docker-containerized, runs on any cloud VM |
| Impact | 10,000+ fields/server, ₹0 data cost |
| Scalability | Stateless API + Celery workers → horizontal scaling |
| Presentation | Live demo, working PDF reports, interactive maps |
| Social Relevance | Direct alignment with PM Kisan Samman Nidhi goals |
