from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
import json
import os
import re
from playwright.sync_api import sync_playwright

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
            media_type="application/json",
            status_code=400
        )

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.phpkobo.com/html-obfuscator", timeout=15000)

            # Fill form
            page.fill('textarea[name="icode"]', code)
            page.check('input[name="remove-script"]')
            page.check('input[name="remove-comment"]')
            page.click('input[type="submit"]')

            # Wait for result
            page.wait_for_selector('textarea[name="ocode"]', timeout=10000)

            # Get obfuscated code
            obfuscated_code = page.locator('textarea[name="ocode"]').input_value()

            browser.close()

        # Branding replacement
        obfuscated_code = re.sub(
            r'<!-- Obfuscated at (.*?) on https://www\.phpkobo\.com/html-obfuscator -->',
            r'<!-- Obfuscated at \1 on HTML-OBFUSCATOR FastAPI -->',
            obfuscated_code
        )

        # Return JSON pretty printed
        return Response(
            content=json.dumps({"obfuscated_code": obfuscated_code}, indent=4, ensure_ascii=False),
            media_type="application/json"
        )

    except Exception as e:
        return Response(
            content=json.dumps({"error": f"Headless browser error: {str(e)}"}, indent=4),
            media_type="application/json",
            status_code=500
        )
