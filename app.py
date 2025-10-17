from fastapi import FastAPI, Request, Form, HTTPException, Query, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import os
import uuid
import threading
import time
import smtplib
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
import json
import pandas as pd
from scraper_fixed import scrape_company_data
#from scraper.send_email import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD
import urllib.parse
from scraper_fixed import build_carriersource_url, run_batched_scrape

# Create FastAPI app
app = FastAPI(
    title="WebScraper Pro API",
    description="An advanced web scraping API that extracts data from websites and returns it as structured data.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware for simple login
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET", "change-me-please"),
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Store ongoing scraping jobs
scraping_jobs = {}

# Store metadata about jobs
job_metadata = {}

def is_authenticated(request: Request) -> bool:
    return bool(request.session.get("authenticated"))

def require_auth_or_redirect(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    return None

def require_auth_or_401(request: Request):
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    redirect = require_auth_or_redirect(request)
    if redirect is not None:
        return redirect
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    valid_email = "carrierscraper@gmail.com"
    valid_password = "scraper123carr"
    if email.strip().lower() == valid_email and password == valid_password:
        request.session["authenticated"] = True
        request.session["user_email"] = email.strip().lower()
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid email or password"},
        status_code=401,
    )

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.post("/generate-url")
async def generate_url(
    request: Request,
    origin: Optional[str] = Form(None),
    destination: Optional[str] = Form(None),
    company_type: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    truck_type: Optional[Union[List[str], str]] = Form(None),
    shipment_type: Optional[Union[List[str], str]] = Form(None),
    specialized_service: Optional[Union[List[str], str]] = Form(None),
    freight: Optional[Union[List[str], str]] = Form(None),
    safety_rating: Optional[Union[List[str], str]] = Form(None),
    operation: Optional[Union[List[str], str]] = Form(None),
    insurance_minimum: Optional[str] = Form(None),
    authority_maintained: Optional[str] = Form(None),
    fleet_min: Optional[str] = Form(None),
    fleet_max: Optional[str] = Form(None)
):
    require_auth_or_401(request)
    final_url = build_carriersource_url(
        company_name=company_name,
        fleet_min=fleet_min,
        fleet_max=fleet_max,
        company_type=company_type,
        origin=origin,
        destination=destination,
        truck_type=truck_type,
        shipment_type=shipment_type,
        specialized_service=specialized_service,
        freight=freight,
        safety_rating=safety_rating,
        operation=operation,
        insurance_minimum=insurance_minimum,
        authority_maintained=authority_maintained,
    )
    return JSONResponse({"url": final_url})

@app.post("/scrape")
async def scrape(
    request: Request,
    url: str = Form(...),
    depth: int = Form(1, description="Scraping depth level"),
    wait_time: int = Form(3, description="Wait time between requests in seconds"),
    follow_pagination: bool = Form(False, description="Whether to follow pagination links"),
    include_images: bool = Form(False, description="Whether to include images in results")
):
    require_auth_or_401(request)
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Create a dictionary to store job status
    job_status = {
        "status": "in_progress",
        "message": "Initializing scraper...",
        "csv_path": None,
        "preview_data": None,
        "progress": 0
    }
    scraping_jobs[job_id] = job_status
    
    # Store metadata about the job
    job_metadata[job_id] = {
        "url": url,
        "start_time": datetime.now().isoformat(),
        "options": {
            "depth": depth,
            "wait_time": wait_time,
            "follow_pagination": follow_pagination,
            "include_images": include_images
        },
        "end_time": None,
        "total_records": 0,
        "total_pages": 0,
        "duration_seconds": 0
    }
    
    # Start scraping in a separate thread
    thread = threading.Thread(
        target=run_scraper, 
        args=(url, job_id, depth, wait_time, follow_pagination, include_images)
    )
    thread.daemon = True
    thread.start()
    
    return {"status": "success", "job_id": job_id}

@app.get("/job_status/{job_id}")
async def job_status(job_id: str, request: Request):
    require_auth_or_401(request)
    if job_id not in scraping_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get the job status
    status = scraping_jobs[job_id]
    
    # Add metadata if available
    if job_id in job_metadata:
        status["metadata"] = job_metadata[job_id]
    
    return status

@app.get("/preview/{job_id}")
async def get_preview(job_id: str, request: Request, limit: int = Query(10, ge=1, le=50)):
    require_auth_or_401(request)
    """Get a preview of the scraped data"""
    if job_id not in scraping_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if scraping_jobs[job_id]["status"] != "ready":
        raise HTTPException(status_code=400, detail="Data not ready yet")
    
    if not scraping_jobs[job_id]["csv_path"]:
        raise HTTPException(status_code=404, detail="CSV file not found")
    
    try:
        # Read the CSV file
        df = pd.read_csv(scraping_jobs[job_id]["csv_path"]).drop_duplicates()
        
        # Clean rows: drop any row containing 'Error'
        clean_df = df[~df.apply(lambda r: r.astype(str).str.contains("Error").any(), axis=1)]
        preview = clean_df.head(limit).to_dict(orient="records")
        columns = df.columns.tolist()
        
        return {
            "columns": columns,
            "data": preview,
            "total_records": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading preview data: {str(e)}")

@app.get("/download/{job_id}")
async def download_csv(job_id: str, request: Request):
    require_auth_or_401(request)
    if job_id not in scraping_jobs or scraping_jobs[job_id]["csv_path"] is None:
        raise HTTPException(status_code=404, detail="CSV file not available")
    
    csv_path = scraping_jobs[job_id]["csv_path"]
    
    # Create a callback to remove the file after response
    def cleanup_file():
        try:
            os.remove(csv_path)
            # Update job status
            scraping_jobs[job_id]["status"] = "completed"
            scraping_jobs[job_id]["message"] = "CSV downloaded and removed from server"
            scraping_jobs[job_id]["csv_path"] = None
            
            # Keep job metadata for a while
            # In a production app, you might want to clean this up after some time
        except Exception as e:
            print(f"Error removing file {csv_path}: {e}")
    
    return FileResponse(
        path=csv_path,
        filename="scraped_data.csv",
        media_type="text/csv",
        background=BackgroundTask(cleanup_file)
    )

@app.get("/jobs", response_model=List[Dict[str, Any]])
async def list_jobs(request: Request):
    require_auth_or_401(request)
    """List all active and recently completed jobs"""
    result = []
    
    for job_id, status in scraping_jobs.items():
        job_info = {
            "job_id": job_id,
            "status": status["status"],
            "message": status["message"]
        }
        
        if job_id in job_metadata:
            job_info.update({
                "url": job_metadata[job_id]["url"],
                "start_time": job_metadata[job_id]["start_time"],
                "end_time": job_metadata[job_id]["end_time"],
                "total_records": job_metadata[job_id]["total_records"]
            })
        
        result.append(job_info)
    
    return result

def update_progress(job_id, progress, message):
    """Update the progress of a job"""
    if job_id in scraping_jobs:
        scraping_jobs[job_id]["progress"] = progress
        scraping_jobs[job_id]["message"] = message

def run_scraper(url, job_id, depth=1, wait_time=3, follow_pagination=False, include_images=False):
    try:
        start_time = time.time()
        
        # Update progress - starting
        update_progress(job_id, 10, "Starting the scraper...")
        
        # Ensure directory exists
        os.makedirs("static/temp", exist_ok=True)
        
        # Generate a unique filename
        csv_path = f"static/temp/{job_id}.csv"
        
        # Update progress - connecting
        update_progress(job_id, 20, "Connecting to the website...")
        
        # Use scraper_fixed batched flow so it matches CLI behavior
        companies_data = run_batched_scrape(url)
        
        # Update progress - processing
        update_progress(job_id, 70, "Processing scraped data...")
        
        if companies_data:
            # Create DataFrame and save to CSV
            df = pd.DataFrame(companies_data)
            df.to_csv(csv_path, index=False)
            
            # Generate preview data
            preview_data = df.head(5).to_dict(orient="records")
            
            # Calculate duration
            end_time = time.time()
            duration = end_time - start_time
            
            # Update job metadata
            if job_id in job_metadata:
                job_metadata[job_id].update({
                    "end_time": datetime.now().isoformat(),
                    "total_records": len(df),
                    "total_pages": 1,  # For now, just one page
                    "duration_seconds": round(duration, 2)
                })
            
            # Update job status
            scraping_jobs[job_id].update({
                "status": "ready",
                "message": f"Successfully scraped {len(df)} records",
                "csv_path": csv_path,
                "preview_data": preview_data,
                "progress": 100
            })
        else:
            # No data was scraped
            scraping_jobs[job_id].update({
                "status": "error",
                "message": "No data was scraped",
                "progress": 100
            })
    except Exception as e:
        # Update job status on error
        scraping_jobs[job_id].update({
            "status": "error",
            "message": f"Error: {str(e)}",
            "progress": 100
        })



                

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 