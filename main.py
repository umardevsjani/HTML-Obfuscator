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

        obfuscated_code = re.sub(
            r'<!-- Obfuscated at (.*?) on https://www\.phpkobo\.com/html-obfuscator -->',
            r'<!-- Obfuscated at \1 on HTML-OBFUSCATOR FastAPI -->',
            obfuscated_code
        )

        return JSONResponse(content={"obfuscated_code": obfuscated_code})  # ✅ Fixed

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
