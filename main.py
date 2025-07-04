from fastapi import Form
from fastapi.responses import StreamingResponse
from io import BytesIO

@app.post("/obfuscate-download")
def obfuscate_download(code: str = Form(...)):
    try:
        session = requests.Session()

        # Session setup
        init_url = "https://www.phpkobo.com/html-obfuscator"
        session.get(init_url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*'
        })

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

        soup = BeautifulSoup(response.text, 'html.parser')
        textarea = soup.find('textarea', {'name': 'ocode'})
        obfuscated_code = textarea.get_text(strip=False)

        # Branding replace
        obfuscated_code = re.sub(
            r'<!-- Obfuscated at (.*?) on https://www\.phpkobo\.com/html-obfuscator -->',
            r'<!-- Obfuscated at \1 on HTML-OBFUSCATOR FastAPI -->',
            obfuscated_code
        )

        # Create downloadable stream
        file_stream = BytesIO(obfuscated_code.encode('utf-8'))
        return StreamingResponse(
            file_stream,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=obfuscated_output.html"
            }
        )

    except Exception as e:
        return Response(
            content=f"Error: {str(e)}",
            media_type="text/plain",
            status_code=500
        )
