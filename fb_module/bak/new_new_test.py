import requests

url = "https://minerva-drab.vercel.app/api/reports/submit"
headers = {
    "x-api-key": "d3deab80460763d8cfaa9159f9f2f64ef8cfac26a650ab97a736f192f4a7e204"
}

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.text)