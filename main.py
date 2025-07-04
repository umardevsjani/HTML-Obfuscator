from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import requests
from bs4 import BeautifulSoup
import re
import io
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_form():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.post("/obfuscate")
async def obfuscate_html(code: str = Form(...)):
    try:
        session = requests.Session()

        # Step 1: GET to init session
        init_url = "https://www.phpkobo.com/html-obfuscator"
        session.get(init_url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html,application/xhtml+xml'
        })

        # Step 2: POST with code
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
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml'
        }

        response = session.post(init_url, data=data, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        textarea = soup.find('textarea', {'name': 'ocode'})
        if not textarea:
            return HTMLResponse("<h2>Obfuscation failed. Please try again.</h2>", status_code=500)

        obfuscated_code = textarea.get_text(strip=False)

        # Optional: change branding comment
        obfuscated_code = re.sub(
            r'<!-- Obfuscated at (.*?) on https://www\.phpkobo\.com/html-obfuscator -->',
            r'<!-- Obfuscated at \1 on HTML-OBFUSCATOR FastAPI -->',
            obfuscated_code
        )

        # Return as downloadable file
        file_stream = io.BytesIO(obfuscated_code.encode("utf-8"))
        return StreamingResponse(file_stream,
                                 media_type="text/html",
                                 headers={
                                     "Content-Disposition": "attachment; filename=obfuscated.html"
                                 })

    except Exception as e:
        return HTMLResponse(f"<h2>Error: {str(e)}</h2>", status_code=500)
