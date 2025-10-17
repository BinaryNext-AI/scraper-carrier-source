# Deployment Guide for Render.com

## Chrome Installation

The application requires Google Chrome to be installed on the deployment environment. 

### Option 1: Use the provided build script
Add this to your Render build command:
```bash
chmod +x build.sh && ./build.sh && pip install -r requirements.txt
```

### Option 2: Manual Chrome installation
Add this to your Render build command:
```bash
apt-get update && apt-get install -y wget gnupg && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && apt-get update && apt-get install -y google-chrome-stable && pip install -r requirements.txt
```

## Environment Variables

Set these environment variables in your Render dashboard:
- `RENDER=true` (automatically set by Render)
- `SESSION_SECRET=your-secret-key-here`

## Build Command
```bash
chmod +x build.sh && ./build.sh && pip install -r requirements.txt
```

## Start Command
```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

## Notes
- The application will automatically detect deployment environment and use headless Chrome
- If undetected-chromedriver fails, it will fallback to regular selenium
- Chrome binary paths are automatically detected in deployment environments
