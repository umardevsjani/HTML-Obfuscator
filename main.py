from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import requests
from bs4 import BeautifulSoup
import re
import os
import json  # <-- Required for manual JSON formatting

app = FastAPI()

# Static folder mount
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open(os.path.join("static", "index.html"), "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>index.html not found</h1>", status_code=404)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Unexpected error: {str(e)}</h1>", status_code=500)


@app.get("/html-obfuscator")
def obfuscate_html(code: str = Query(None)):
    if not code:
        return JSONResponse(
            content={"error": "Please provide 'code' parameter for obfuscation."},
            status_code=400
        )

    data = {
        'cmd': 'obfuscate',
        'icode': code,
        'remove-script': 'y',
        'remove-comment': 'y',
        'ocode': ''
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Origin': 'https://www.phpkobo.com',
        'Referer': 'https://www.phpkobo.com/html-obfuscator',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.post('https://www.phpkobo.com/html-obfuscator', data=data, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        textarea = soup.find('textarea', {'name': 'ocode'})

        if not textarea:
            return JSONResponse(
                content={"error": "Could not find obfuscated code in response."},
                status_code=500
            )

        obfuscated_code = textarea.text

        # Branding replace (optional)
        obfuscated_code = re.sub(
            r'<!-- Obfuscated at (.*?) on https://www\.phpkobo\.com/html-obfuscator -->',
            r'<!-- Obfuscated at \1 on HTML-OBFUSCATOR FastAPI -->',
            obfuscated_code
        )

        # Return pretty-printed JSON manually
        formatted_json = json.dumps({"obfuscated_code": obfuscated_code}, indent=4)
        return HTMLResponse(content=formatted_json, media_type="application/json")

    except requests.RequestException as req_err:
        return JSONResponse(
            content={"error": f"Request to obfuscator failed: {str(req_err)}"},
            status_code=502
        )

    except Exception as e:
        return JSONResponse(
            content={"error": f"Unexpected server error: {str(e)}"},
            status_code=500
        )
