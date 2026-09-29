# FreshGrade AI — Deployment Guide

This guide covers deployment options for **FreshGrade AI**, including instant live public tunneling, Cloud Web Services (Render, Railway, Hugging Face Spaces), and Docker containerization.

---

## 🌐 Instant Live Public URL (Active Now)

Your local FreshGrade AI server is currently live on the public internet via LocalTunnel:

- **Live Public App URL**: `https://grumpy-trams-sip.loca.lt`
- **Live OpenAPI Docs**: `https://grumpy-trams-sip.loca.lt/docs`
- **Local Application URL**: `http://localhost:8000`

---

## ☁️ Free Cloud Hosting Options

### Option A: Render.com (Recommended for Free Tier)
1. Push this repository to GitHub/GitLab.
2. Sign up on [Render.com](https://render.com).
3. Click **New +** -> **Blueprint**.
4. Connect your GitHub repository. Render will automatically detect [`render.yaml`](file:///c:/Users/DELL/Desktop/Sindhuja%20Sankaramoorthy/hack/render.yaml).
5. Click **Apply**. Render will automatically build and deploy your app with a free HTTPS URL (`https://freshgrade-ai.onrender.com`).

---

### Option B: Railway.app
1. Go to [Railway.app](https://railway.app).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select your repo. Railway will automatically pick up [`Procfile`](file:///c:/Users/DELL/Desktop/Sindhuja%20Sankaramoorthy/hack/Procfile) and deploy your app.

---

### Option C: Hugging Face Spaces (Docker Space)
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Select SDK: **Docker**.
3. Push your repository to the Hugging Face Space git remote. It will automatically build using [`Dockerfile`](file:///c:/Users/DELL/Desktop/Sindhuja%20Sankaramoorthy/hack/Dockerfile) and expose your app publicly.

---


## 🐳 Option 1: Container Deployment with Docker Compose (Recommended)

Docker Compose starts both the **FreshGrade AI application** container and a persistent **MongoDB database** container.

### Step 1: Build & Start Container Stack
```bash
docker-compose up --build -d
```

### Step 2: Verify Deployment
Check the container health and logs:
```bash
docker-compose ps
docker-compose logs -f freshgrade-app
```

Navigate to:
- **Web Interface**: `http://localhost:8000`
- **API Health Check**: `http://localhost:8000/health`
- **Interactive OpenAPI Docs**: `http://localhost:8000/docs`

### Step 3: Stop Container Stack
```bash
docker-compose down
```

---

## 📦 Option 2: Standalone Docker Image Build

If deploying to cloud platforms like AWS ECS, GCP Cloud Run, Azure Container Instances, or Render:

### Build Docker Image
```bash
docker build -t freshgrade-ai:latest .
```

### Run Container
```bash
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY="your_api_key_here" \
  --name freshgrade_instance \
  freshgrade-ai:latest
```

---

## ⚡ Option 3: Direct Python Server Deployment

To run directly on a VM or local developer machine:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Production Server
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🔑 Environment Variables Reference

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `PORT` | `8000` | HTTP port for application service |
| `MONGODB_URI` | `mongodb://localhost:27017` | MongoDB connection URI string |
| `MONGODB_DB_NAME` | `freshgrade_db` | Target MongoDB database name |
| `GEMINI_API_KEY` | *(Optional)* | Google Gemini API key for Multimodal Vision AI fallback |

---

## 🧪 Verification & Testing

Before deploying to production, run automated test suites:
```bash
python -m pytest tests/ -v
```
