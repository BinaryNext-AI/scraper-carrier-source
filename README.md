# WebScraper Pro

An advanced web application that allows users to input a URL, scrape data from the provided website, and download the data as a CSV file. The application automatically deletes the CSV file from the server after download.

## Features

- Modern, responsive web interface with dark mode support
- Real-time progress updates during scraping
- Data preview before download
- Advanced scraping options:
  - Multi-level scraping depth
  - Pagination support
  - Wait time configuration
  - Image inclusion options
- Automatic data cleaning and formatting
- CSV export with one-click download
- Automatic file deletion after download
- Built with FastAPI for high performance
- **Email Marketing Features**:
  - Send personalized emails to scraped contacts
  - Template system with variable substitution
  - Real-time email sending status updates
  - SMTP server configuration options

## Screenshots

- Modern UI with dark mode support
- Real-time progress tracking
- Data preview functionality
- Advanced configuration options
- Email marketing interface

## Setup Instructions

1. **Clone the repository**

2. **Create a virtual environment**
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   - Windows:
     ```
     venv\Scripts\activate
     ```
   
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

5. **Install Chrome browser** (if not already installed)
   
   The scraper uses Chrome browser, so make sure it's installed on your system.

6. **Run the application**
   ```
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

7. **Access the web interface**
   
   Open your browser and navigate to http://127.0.0.1:8000

## Usage

1. Enter the URL of the website you want to scrape in the input field
2. Configure advanced options if needed:
   - Scraping depth: Choose how many levels deep to scrape
   - Wait time: Set delay between requests to avoid rate limiting
   - Follow pagination: Enable to scrape multiple pages
   - Include images: Option to include image data in results
3. Click the "Scrape Data" button to start scraping
4. Monitor real-time progress with detailed status updates
5. Once scraping is complete, preview the data before downloading
6. Click the "Download CSV" button to download the data
7. The CSV file will be automatically deleted from the server after download

### Email Marketing

1. After scraping data, scroll down to the "Send Emails to Contacts" section
2. Enter your email credentials and SMTP server information
3. Compose your email subject and body
4. Use placeholders like `{{Company Name}}` or `{{Email}}` to personalize your message
5. Click "Send Emails" to start the email campaign
6. Monitor real-time progress of email sending

## API Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### API Endpoints

- `GET /`: Web interface
- `POST /scrape`: Start a new scraping job
- `GET /job_status/{job_id}`: Check the status of a job
- `GET /preview/{job_id}`: Get a preview of scraped data
- `GET /download/{job_id}`: Download the scraped data as CSV
- `GET /jobs`: List all active and recent jobs
- `POST /send-emails/{job_id}`: Send emails to contacts in CSV
- `GET /email-status/{job_id}/{email_job_id}`: Check email sending status

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Backend**: FastAPI, Python 3.10+
- **Scraping**: Selenium, Undetected ChromeDriver
- **Data Processing**: Pandas
- **Email**: SMTP, MIMEText, MIMEMultipart

## Notes

- The scraper is configured to work with websites that require login
- For websites with CAPTCHA, manual intervention may be required
- Scraping performance depends on website structure and size
- Respect website terms of service and robots.txt when scraping
- For email sending, you may need to enable "Less secure app access" in Gmail or use an App Password 