import sqlite3

db_path = r"C:\Users\11523\Desktop\新建文件夹\opengauss-agent\backend\opengauss_agent.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT title, content FROM knowledge_nodes WHERE content LIKE '%/images/%' LIMIT 10")
rows = c.fetchall()
for title, content in rows:
    print(f"=== {title} ===")
    import re
    imgs = re.findall(r'/images/([^\s\)]+)', content)
    print(f"  Image refs: {imgs}")
    print()