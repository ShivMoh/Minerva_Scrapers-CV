import requests
import json

response = requests.post(
    "https://minerva-drab.vercel.app/api/reports/submit",
    headers={"x-api-key": "d3deab80460763d8cfaa9159f9f2f64ef8cfac26a650ab97a736f192f4a7e204"},
    files={
        'data': (None, json.dumps({
            "description": "Worker injury incident",
            "location": {"address": "Site Location"},
            "date": "2024-01-15T10:30:00Z"
        })),
        'image': open('./test.png', 'rb')
    }
)

print(response)