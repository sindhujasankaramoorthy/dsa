import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse

# Ensure backend package is in python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.api import inspection, batch, dashboard, produce_types, admin, auth, farmer_api, industry_guide_api
from backend.app.services.inference_service import inference_service

app = FastAPI(
    title="FreshGrade AI",
    description="Fruit & Vegetable Quality Intelligence Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware for smartphone & web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(inspection.router)
app.include_router(farmer_api.router)
app.include_router(industry_guide_api.router)
app.include_router(batch.router)
app.include_router(dashboard.router)
app.include_router(produce_types.router)
app.include_router(admin.router)
app.include_router(auth.router)

@app.get("/health")
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "FreshGrade AI",
        "tagline": "Turn Produce Images Into Actionable Quality Insights.",
        "version": "1.0.0"
    }

# Backward compatibility endpoint for original fruit repo callers
@app.post("/detect")
async def legacy_detect(request: Request):
    """Backward compatibility endpoint for legacy fruit pipeline."""
    form_data = await request.form()
    file = form_data.get("file")
    image_bytes = await file.read() if file else None
    
    if not image_bytes:
        return JSONResponse(status_code=400, content={"error": "No image provided."})

    res = inference_service.analyze_image(image_bytes=image_bytes)
    return res

# Static UI serving
FRONTEND_DIR = BASE_DIR / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
@app.get("/industry-guide", response_class=HTMLResponse)
@app.get("/guide", response_class=HTMLResponse)
def index():
    """Serves the FreshGrade AI Single Page Application & Standalone Grade-to-Industry Guide."""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>FreshGrade AI API Service is running. Frontend index.html not found.</h1>"
