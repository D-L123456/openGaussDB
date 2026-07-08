import httpx
import json

# Check tree
r = httpx.get('http://127.0.0.1:8000/api/knowledge-tree/tree')
data = r.json()
roots = data.get('nodes', [])
print(f"Root nodes: {len(roots)}")
for n in roots:
    print(f"  {n['title']} sort={n.get('sort_order', '?')}")

# Check stats
r2 = httpx.get('http://127.0.0.1:8000/api/knowledge-tree/stats')
print(f"\nStats: {r2.json()}")

# Check images in content
for n in roots:
    if n.get('children'):
        for child in n['children'][:3]:
            content = child.get('content', '')
            has_img = '/images/' in content
            print(f"  {child['title']}: has_image={has_img}, content_len={len(content)}")
            if has_img:
                idx = content.find('/images/')
                print(f"    Image ref: ...{content[max(0,idx-10):idx+60]}...")
