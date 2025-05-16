# HTML Obfuscator API

Easily obfuscate your HTML code with our lightweight and developer-friendly API.

## Features

- Built with **FastAPI** for high performance.
- Interactive API Documentation.
- Simple and intuitive endpoints.
- Easily obfuscates HTML code.
- Supports JSON responses.
- Lightweight and fast.
- Made for developers.

## Endpoints

### Home
- **Description**: Displays the homepage with an HTML interface.
- **Method**: `GET`
- **Endpoint**: `/`
- **Example**: [http://localhost:8000/](http://localhost:8000/)

### HTML Obfuscator
- **Description**: Obfuscates the provided HTML code.
- **Method**: `GET`
- **Endpoint**: `/html-obfuscator`
- **Query Parameter**: 
  - `code` (required): The HTML code to obfuscate.
- **Example**: [http://localhost:8000/html-obfuscator?code=<html_code>](http://localhost:8000/html-obfuscator?code=<html_code>)

## Example Request

```bash
curl -X GET "http://localhost:8000/html-obfuscator?code=<html_code>" \
     -H "accept: application/json"
```

## Response Example

```json
{
    "obfuscated_code": "<!-- Obfuscated Code Here -->"
}
```

## Error Handling

### Missing Code Parameter
- **Error Message**:
  ```json
  {
      "error": "Please provide code parameter for obfuscation."
  }
  ```

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/html-obfuscator-api.git
   ```

2. Navigate to the project directory:
   ```bash
   cd html-obfuscator-api
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

5. Access the API at [http://localhost:8000](http://localhost:8000).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Made with ❤️ by [Kaizenji](https://kaizenji-info.pages.dev).  
&copy; 2025 All rights reserved.
