import httpx

r = httpx.get("http://localhost:8000/api/knowledge-tree/tree")
data = r.json()["nodes"]
print(f"Root count: {len(data)}")
for n in data:
    print(f"  {n['title']} (sort={n['sort_order']})")

img_count = 0
def count_images(nodes):
    global img_count
    for n in nodes:
        if "/images/" in (n.get("content") or ""):
            img_count += 1
        children = n.get("children") or []
        count_images(children)

count_images(data)
print(f"\nNodes with images: {img_count}")

first_with_img = None
def find_first_img(nodes):
    global first_with_img
    for n in nodes:
        if "/images/" in (n.get("content") or ""):
            first_with_img = n
            return
        children = n.get("children") or []
        find_first_img(children)

find_first_img(data)
if first_with_img:
    print(f"\nFirst node with image: {first_with_img['title']}")
    content = first_with_img["content"]
    idx = content.find("/images/")
    print(f"Image URL sample: ...{content[max(0,idx-10):idx+40]}...")