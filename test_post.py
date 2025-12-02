import requests, json

payload = {
  "title": "Тест через Python 2025",
  "slug": "test-py-2025",
  "level": "Всерос",
  "subjects": ["Тест"],
  "prize": "Тест",
  "source_url": "https://example.com",
  "is_active": True,
  "content_hash": "py-test-001"
}

r = requests.post("http://localhost:8000/api/v1/olympiads/", json=payload, timeout=10)
print("status:", r.status_code)
print("text:", r.text)
