from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
import requests
from bs4 import BeautifulSoup
import re
import os
import json

app = FastAPI()
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
        return Response(
            content=json.dumps({"error": "Please provide 'code' parameter for obfuscation."}, indent=4),
            media_type="application/json"
        )

    try:
        session = requests.Session()

        # Step 1: GET to initialize session cookies
        init_url = "https://www.phpkobo.com/html-obfuscator"
        session.get(init_url, headers={
            'User-Agent': 'Mozilla/5.0'
        })

        # Step 2: POST the code to obfuscate
        data = {
            'cmd': 'obfuscate',
            'icode': code,
            'remove-script': 'y',
            'remove-comment': 'y',
            'ocode': ''
        }

        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': init_url,
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = session.post(init_url, data=data, headers=headers)
        response.raise_for_status()

        # Step 3: Parse obfuscated result
        soup = BeautifulSoup(response.text, 'html.parser')
        textarea = soup.find('textarea', {'name': 'ocode'})

        if not textarea:
            return Response(
                content=json.dumps({"error": "Obfuscated code not found in response."}, indent=4),
                media_type="application/json",
                status_code=500
            )

        obfuscated_code = textarea.get_text(strip=False)  # Do NOT strip or modify!
        
        # Optional branding replace
        obfuscated_code = re.sub(
            r'<!-- Obfuscated at (.*?) on https://www\.phpkobo\.com/html-obfuscator -->',
            r'<!-- Obfuscated at \1 on HTML-OBFUSCATOR FastAPI -->',
            obfuscated_code
        )

        # ✅ Return clean raw JS in JSON
        return Response(
            content=json.dumps({"obfuscated_code": obfuscated_code}, indent=4, ensure_ascii=False),
            media_type="application/json"
        )

    except requests.RequestException as req_err:
        return Response(
            content=json.dumps({"error": f"Request failed: {str(req_err)}"}, indent=4),
            media_type="application/json",
            status_code=502
        )
    except Exception as e:
        return Response(
            content=json.dumps({"error": f"Unexpected server error: {str(e)}"}, indent=4),
            media_type="application/json",
            status_code=500
        )


# Optional: Live preview route to test obfuscated HTML
@app.get("/preview", response_class=HTMLResponse)
def preview(code: str = Query(...)):
    return HTMLResponse(content=code)
