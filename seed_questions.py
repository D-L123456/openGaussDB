import sqlite3
import uuid
from datetime import datetime

db_path = r"C:\Users\11523\Desktop\新建文件夹\opengauss-agent\backend\opengauss_agent.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

now = datetime.now().isoformat()

questions = [
    {
        "id": str(uuid.uuid4()),
        "chapter": "第2章",
        "title": "创建银行业务数据库",
        "description": "请编写SQL语句，创建一个名为bankdb的数据库。",
        "difficulty": "easy",
        "hint": "使用CREATE DATABASE语句",
        "reference_sql": "CREATE DATABASE bankdb;",
        "setup_sql": None,
        "tags": '{"type": "DDL", "keyword": "CREATE DATABASE"}',
        "created_at": now,
    },
    {
        "id": str(uuid.uuid4()),
        "chapter": "第2章",
        "title": "创建用户信息表",
        "description": "请编写SQL语句，在bankdb中创建userInfo表，包含以下字段：\ncustomerID SERIAL PRIMARY KEY\ncustomerName CHAR(8) NOT NULL\nPID CHAR(18) NOT NULL\ntelephone CHAR(20) NOT NULL\naddress VARCHAR(50)",
        "difficulty": "easy",
        "hint": "使用CREATE TABLE语句，注意SERIAL类型用于自增主键",
        "reference_sql": "CREATE TABLE userInfo (\n  customerID SERIAL PRIMARY KEY,\n  customerName CHAR(8) NOT NULL,\n  PID CHAR(18) NOT NULL,\n  telephone CHAR(20) NOT NULL,\n  address VARCHAR(50)\n);",
        "setup_sql": None,
        "tags": '{"type": "DDL", "keyword": "CREATE TABLE"}',
        "created_at": now,
    },
    {
        "id": str(uuid.uuid4()),
        "chapter": "第2章",
        "title": "创建银行卡信息表",
        "description": "请编写SQL语句，创建cardInfo表，包含以下字段：\ncardID CHAR(17) PRIMARY KEY\ncurID VARCHAR(10) DEFAULT 'RMB' NOT NULL\nsavingID INTEGER NOT NULL\nopenDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP\nopenMoney DECIMAL(18,2) NOT NULL\nbalance DECIMAL(18,2) NOT NULL\npass CHAR(6) NOT NULL\nIsReportLoss VARCHAR(3) NOT NULL DEFAULT '否'",
        "difficulty": "medium",
        "hint": "注意DEFAULT关键字设置默认值，DECIMAL用于金额类型",
        "reference_sql": "CREATE TABLE cardInfo (\n  cardID CHAR(17) PRIMARY KEY,\n  curID VARCHAR(10) DEFAULT 'RMB' NOT NULL,\n  savingID INTEGER NOT NULL,\n  openDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\n  openMoney DECIMAL(18,2) NOT NULL,\n  balance DECIMAL(18,2) NOT NULL,\n  pass CHAR(6) NOT NULL,\n  IsReportLoss VARCHAR(3) NOT NULL DEFAULT '否'\n);",
        "setup_sql": None,
        "tags": '{"type": "DDL", "keyword": "CREATE TABLE, DEFAULT"}',
        "created_at": now,
    },
    {
        "id": str(uuid.uuid4()),
        "chapter": "第2章",
        "title": "插入存款类型数据",
        "description": "请编写SQL语句，向deposit表中插入一条存款类型记录：存款名称为'活期'，描述为'按存款日结算利息'。",
        "difficulty": "easy",
        "hint": "使用INSERT INTO ... VALUES语句",
        "reference_sql": "INSERT INTO deposit (savingName, descrip) VALUES ('活期', '按存款日结算利息');",
        "setup_sql": None,
        "tags": '{"type": "DML", "keyword": "INSERT INTO"}',
        "created_at": now,
    },
    {
        "id": str(uuid.uuid4()),
        "chapter": "第2章",
        "title": "修改银行卡密码",
        "description": "请编写SQL语句，将cardInfo表中卡号为'1010357600000010'的银行卡密码修改为'123456'。",
        "difficulty": "easy",
        "hint": "使用UPDATE ... SET ... WHERE语句",
        "reference_sql": "UPDATE cardInfo SET pass = '123456' WHERE cardID = '1010357600000010';",
        "setup_sql": None,
        "tags": '{"type": "DML", "keyword": "UPDATE, SET, WHERE"}',
        "created_at": now,
    },
    {
        "id": str(uuid.uuid4()),
        "chapter": "第2章",
        "title": "添加外键约束",
        "description": "请编写SQL语句，为cardInfo表添加一个外键约束FK_customerID，使customerID列引用userInfo表的customerID列。",
        "difficulty": "medium",
        "hint": "使用ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY ... REFERENCES语句",
        "reference_sql": "ALTER TABLE cardInfo ADD CONSTRAINT FK_customerID FOREIGN KEY(customerID) REFERENCES userInfo(customerID);",
        "setup_sql": None,
        "tags": '{"type": "DDL", "keyword": "ALTER TABLE, FOREIGN KEY, REFERENCES"}',
        "created_at": now,
    },
    {
        "id": str(uuid.uuid4()),
        "chapter": "第2章",
        "title": "查询客户银行卡信息",
        "description": "请编写SQL语句，查询所有客户的姓名、卡号和账户余额，要求显示客户姓名、卡号和余额三列。",
        "difficulty": "easy",
        "hint": "使用SELECT ... FROM ... JOIN语句连接userInfo和cardInfo表",
        "reference_sql": "SELECT u.customerName, c.cardID, c.balance FROM userInfo u JOIN cardInfo c ON u.customerID = c.customerID;",
        "setup_sql": None,
        "tags": '{"type": "DQL", "keyword": "SELECT, JOIN"}',
        "created_at": now,
    },
]

for q in questions:
    c.execute(
        "INSERT INTO sql_questions (id, chapter, title, description, difficulty, hint, reference_sql, setup_sql, tags, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (q["id"], q["chapter"], q["title"], q["description"], q["difficulty"], q["hint"], q["reference_sql"], q["setup_sql"], q["tags"], q["created_at"]),
    )

conn.commit()
print(f"Inserted {len(questions)} questions")

c.execute("SELECT COUNT(*) FROM sql_questions")
print(f"Total questions: {c.fetchone()[0]}")

conn.close()