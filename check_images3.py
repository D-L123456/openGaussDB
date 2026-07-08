import sqlite3, re

db_path = r"C:\Users\11523\Desktop\新建文件夹\opengauss-agent\backend\opengauss_agent.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT title, content FROM knowledge_nodes WHERE content LIKE '%/images/%' LIMIT 20")
rows = c.fetchall()
for title, content in rows:
    all_img_refs = re.findall(r'/images/[^\s\)\"]+', content)
    non_png = [r for r in all_img_refs if not r.endswith('.png')]
    if non_png:
        print(f"=== {title} ===")
        for ref in non_png[:3]:
            idx = content.find(ref)
            start = max(0, idx - 40)
            end = min(len(content), idx + len(ref) + 40)
            print(f"  Ref: {ref}")
            print(f"  Context: {content[start:end]}")
            print()