import requests
import json

url = "https://minerva-drab.vercel.app/api/reports/submit"
headers = {
    "x-api-key": "d3deab80460763d8cfaa9159f9f2f64ef8cfac26a650ab97a736f192f4a7e204"
}

# Construct the multipart form data correctly
with open('./test.png', 'rb') as img_file:
    files = {
        # Send JSON string as a field with application/json MIME type
        'data': (None, json.dumps({
            "description": "Worker injury incident",
            "location": {"address": "Site Location"},
            "date": "2024-01-15T10:30:00Z"
        }), 'application/json'),

        # Attach image with filename and mimetype
        'image': ('test.png', img_file, 'image/png')
    }

    response = requests.post(url, headers=headers, files=files)

print(response.status_code)
print(response.text)