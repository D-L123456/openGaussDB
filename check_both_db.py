import sqlite3

# Check root-level DB (used by rebuild script)
conn = sqlite3.connect(r"C:\Users\11523\Desktop\新建文件夹\opengauss-agent\opengauss_agent.db")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM knowledge_nodes")
print("Root DB - Nodes:", cur.fetchone()[0])
cur.execute("SELECT COUNT(*) FROM knowledge_nodes WHERE content LIKE '%/images/%'")
print("Root DB - With images:", cur.fetchone()[0])

# Check backend DB (used by the app)
conn2 = sqlite3.connect(r"C:\Users\11523\Desktop\新建文件夹\opengauss-agent\backend\opengauss_agent.db")
cur2 = conn2.cursor()
cur2.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur2.fetchall()
print("\nBackend DB - Tables:", tables)
if tables:
    cur2.execute("SELECT COUNT(*) FROM knowledge_nodes")
    print("Backend DB - Nodes:", cur2.fetchone()[0])