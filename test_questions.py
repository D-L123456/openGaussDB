import httpx
r = httpx.get("http://localhost:8000/api/sql-practice/questions")
print("Status:", r.status_code)
d = r.json()
print(f"Questions: {len(d)}")
for q in d:
    print(f"  {q['title']} ({q['difficulty']})")