import httpx, json

r = httpx.get("http://localhost:8000/api/knowledge-tree/tree")
data = r.json()
print("Type:", type(data))
if isinstance(data, dict):
    print("Keys:", list(data.keys()))
    for k, v in data.items():
        if isinstance(v, list):
            print(f"  {k}: list of {len(v)}")
            if v and isinstance(v[0], dict):
                print(f"    First item keys: {list(v[0].keys())}")
                print(f"    First item title: {v[0].get('title')}")
        else:
            print(f"  {k}: {v}")
elif isinstance(data, list):
    print(f"List of {len(data)}")
    if data and isinstance(data[0], dict):
        print(f"  First item keys: {list(data[0].keys())}")