from fastapi import FastAPI, Query, Request
from fastapi.responses import PlainTextResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from bs4 import BeautifulSoup

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/html-obfuscator", response_class=PlainTextResponse)
def obfuscate_html(code: str = Query(...)):
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
    return soup.find('textarea', {'name': 'ocode'}).text
