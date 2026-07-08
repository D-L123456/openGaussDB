import sqlite3, re

db_path = r"C:\Users\11523\Desktop\新建文件夹\opengauss-agent\backend\opengauss_agent.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT title, content FROM knowledge_nodes WHERE content LIKE '%/images/%' AND content LIKE '%第1章%' LIMIT 3")
rows = c.fetchall()
for title, content in rows:
    print(f"=== {title} ===")
    img_refs = re.findall(r'!\[.*?\]\((/images/[^)]+)\)', content)
    for ref in img_refs[:3]:
        print(f"  {ref}")
    print()