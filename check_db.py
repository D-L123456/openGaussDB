import sqlite3

db_path = r"C:\Users\11523\Desktop\新建文件夹\opengauss-agent\backend\opengauss_agent.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM knowledge_nodes")
print(f"Total nodes: {c.fetchone()[0]}")

c.execute("SELECT COUNT(*) FROM knowledge_nodes WHERE content LIKE '%/images/%'")
print(f"With images: {c.fetchone()[0]}")

c.execute("SELECT title, sort_order FROM knowledge_nodes WHERE parent_id IS NULL ORDER BY sort_order")
rows = c.fetchall()
print("Root nodes:")
for r in rows:
    print(f"  {r[0]} (sort={r[1]})")

conn.close()
