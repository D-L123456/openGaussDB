import sqlite3
conn = sqlite3.connect(r"C:\Users\11523\Desktop\新建文件夹\opengauss-agent\backend\opengauss_agent.db")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", cur.fetchall())
cur.execute("SELECT COUNT(*) FROM knowledge_nodes")
print("Nodes:", cur.fetchone()[0])
cur.execute("SELECT COUNT(*) FROM knowledge_nodes WHERE content LIKE '%/images/%'")
print("With images:", cur.fetchone()[0])