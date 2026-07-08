import sqlite3
conn = sqlite3.connect(r"C:\Users\11523\Desktop\新建文件夹\opengauss-agent\backend\opengauss_agent.db")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM knowledge_nodes WHERE content LIKE '%/images/%'")
print("With images:", cur.fetchone()[0])

# Check root node order
cur.execute("SELECT title, sort_order FROM knowledge_nodes WHERE parent_id IS NULL ORDER BY sort_order")
for r in cur.fetchall():
    print(f"  {r[0]} sort={r[1]}")