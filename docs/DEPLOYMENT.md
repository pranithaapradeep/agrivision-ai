# AgriVision AI — Deployment Guide

## Option 1: Local / Hackathon Demo (Docker, 5 minutes)

```bash
# Prerequisites: Docker Desktop installed

git clone https://github.com/your-team/agrivision-ai
cd agrivision-ai

# Copy and configure environment
cp backend/.env.example backend/.env
# Optionally add your OpenWeatherMap free API key

# Start all services
docker compose up --build

# Visit http://localhost
```

All 5 services start: PostgreSQL, Redis, FastAPI backend, Celery worker, React frontend via Nginx.

---

## Option 2: Cloud Deployment (AWS/GCP/Azure)

### Minimum server specs:
- 2 vCPU, 4 GB RAM (e.g., AWS t3.medium ~₹2,500/month)
- 20 GB storage for uploaded imagery

```bash
# On Ubuntu 22.04 server
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git

git clone https://github.com/your-team/agrivision-ai
cd agrivision-ai
cp backend/.env.example backend/.env
nano backend/.env  # Set SECRET_KEY, DB password, API keys

docker compose -f docker-compose.yml up -d

# Check status
docker compose ps
curl http://localhost/health
```

### Point a domain (optional):
Add to `docker/nginx.conf`: `server_name yourdomain.com;`
Use Certbot for free HTTPS:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## Option 3: Train Models Before Demo

```bash
cd ml_research/training

# Step 1: Generate synthetic training data (fast, no downloads)
python prepare_datasets.py --dataset synthetic

# Step 2: Train RF and LSTM on synthetic data (5–10 min)
python train_models.py --model rf --synthetic
python train_models.py --model lstm --synthetic --epochs 20

# Step 3: (Optional) Train CNN on PlantVillage images
# Download from Kaggle first, then:
python train_models.py --model cnn --data-dir /path/to/plantvillage

# Weights are saved to: backend/app/ml/weights/
```

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://agrivision:password@db:5432/agrivision_db

# Redis
REDIS_URL=redis://redis:6379

# Security
SECRET_KEY=your-256-bit-secret-key-here

# External APIs (optional — demo fallbacks exist)
OPENWEATHER_API_KEY=your_key_here

# Storage
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE_MB=10

# ML
ML_MODELS_DIR=/app/ml/weights
ENVIRONMENT=production
```

---

## Useful Commands

```bash
# View logs
docker compose logs backend -f
docker compose logs celery_worker -f

# Restart a service
docker compose restart backend

# Database shell
docker compose exec db psql -U agrivision -d agrivision_db

# Redis CLI
docker compose exec redis redis-cli ping

# API health check
curl http://localhost/health
```
