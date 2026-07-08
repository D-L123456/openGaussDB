import sqlite3, re

db_path = r"C:\Users\11523\Desktop\新建文件夹\opengauss-agent\backend\opengauss_agent.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT title, content FROM knowledge_nodes WHERE content LIKE '%/images/%' LIMIT 20")
rows = c.fetchall()
for title, content in rows:
    full_refs = re.findall(r'!\[.*?\]\((/images/[^)]+)\)', content)
    if full_refs:
        broken = [r for r in full_refs if not r.endswith('.png')]
        if broken:
            print(f"=== {title} ===")
            print(f"  All refs: {full_refs[:5]}")
            print(f"  Broken: {broken[:5]}")
            idx = content.find(broken[0])
            print(f"  Context: ...{content[max(0,idx-30):idx+len(broken[0])+30]}...")
            print()