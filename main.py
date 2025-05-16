from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI()

@app.get("/")
async def home():
    return {
        "endpoints": {
            "/html-obfuscator": {
                "method": "GET",
                "params": {
                    "code": "string - HTML code to obfuscate (required)"
                },
                "description": "Obfuscates the given HTML code and returns the obfuscated version."
            }
        }
    }

@app.get("/html-obfuscator")
def obfuscate_html(code: str = Query(None)):
    if not code:
        return JSONResponse(content={"error": "Please provide code parameter for obfuscation."}, status_code=400)
    data = {
        'cmd': 'obfuscate',
        'icode': code,
        'remove-script': 'y',
        'remove-comment': 'y',
        'ocode': ''
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Origin': 'https://www.phpkobo.com',
        'Referer': 'https://www.phpkobo.com/html-obfuscator',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post('https://www.phpkobo.com/html-obfuscator', data=data, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    obfuscated_code = soup.find('textarea', {'name': 'ocode'}).text
    obfuscated_code = re.sub(
        r'<!-- Obfuscated at (.*?) on https://www\.phpkobo\.com/html-obfuscator -->',
        r'<!-- Obfuscated at \1 on HTML-OBFUSCATOR FastAPI -->',
        obfuscated_code
    )
    return JSONResponse(content={"obfuscated_code": obfuscated_code}, indent=4)