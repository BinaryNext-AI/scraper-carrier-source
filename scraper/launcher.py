import os
import sys

# Add parent directory to path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import and run the FastAPI app
import uvicorn

if __name__ == "__main__":
    print("Starting WebScraper Pro from scraper directory...")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 