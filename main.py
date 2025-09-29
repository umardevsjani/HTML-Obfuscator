from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import requests
from bs4 import BeautifulSoup
import re
import io
import logging
from http import HTTPStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Check if static/index.html exists
STATIC_FILE_PATH = "static/index.html"
if not os.path.exists(STATIC_FILE_PATH):
    logger.error(f"Static file {STATIC_FILE_PATH} not found. Ensure it exists in the 'static' directory.")

@app.get("/", response_class=HTMLResponse)
async def serve_form():
    """Serve the HTML form from static/index.html."""
    try:
        with open(STATIC_FILE_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        logger.error("index.html not found in static directory.")
        return HTMLResponse(
            "<h2>Error: Form file not found. Please ensure static/index.html exists.</h2>",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

@app.post("/obfuscate", response_class=HTMLResponse)
async def obfuscate_html(code: str = Form(...)):
    """Obfuscate HTML code using phpkobo.com or return an error."""
    init_url = "https://www.phpkobo.com/html-obfuscator"
    
    try:
        session = requests.Session()
        # Set more comprehensive headers to mimic a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": init_url,
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
        }

        # Step 1: Test website availability with a GET request
        logger.info(f"Checking availability of {init_url}")
        init_response = session.get(init_url, headers=headers, timeout=10)
        init_response.raise_for_status()
        logger.info("Initial GET request successful.")

        # Step 2: POST the code for obfuscation
        data = {
            "cmd": "obfuscate",
            "icode": code,
            "remove-script": "y",
            "remove-comment": "y",
            "ocode": "",
        }

        logger.info("Sending POST request for obfuscation.")
        response = session.post(init_url, data=data, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse the response
        soup = BeautifulSoup(response.text, "html.parser")
        textarea = soup.find("textarea", {"name": "ocode"})
        if not textarea:
            logger.error("Textarea with name 'ocode' not found in response.")
            return HTMLResponse(
                "<h2>Obfuscation failed: Could not find obfuscated code in response. The website may have changed.</h2>",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        obfuscated_code = textarea.get_text(strip=False)
        logger.info("Obfuscation successful.")

        # Replace branding comment
        obfuscated_code = re.sub(
            r"<!-- Obfuscated at (.*?) on https://www\.phpkobo\.com/html-obfuscator -->",
            r"<!-- Obfuscated at \1 on HTML-OBFUSCATOR FastAPI -->",
            obfuscated_code,
        )

        # Return as downloadable file
        file_stream = io.BytesIO(obfuscated_code.encode("utf-8"))
        return StreamingResponse(
            file_stream,
            media_type="text/html",
            headers={"Content-Disposition": "attachment; filename=obfuscated.html"},
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while accessing {init_url}: {str(e)}")
        return HTMLResponse(
            f"<h2>Error: Failed to connect to the obfuscation service. Please try again later. ({str(e)})</h2>",
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
        )
    except Exception as e:
        logger.error(f"Unexpected error during obfuscation: {str(e)}")
        return HTMLResponse(
            f"<h2>Error: An unexpected error occurred. ({str(e)})</h2>",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
