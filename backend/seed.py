import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import async_session, init_db
from app.models.sql_practice import SqlQuestion
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import vector_store
from app.services.knowledge_tree import knowledge_tree_service


SQL_QUESTIONS = [
    {
        "chapter": "第1章",
        "title": "创建数据库和表",
        "description": "创建一个名为student_db的数据库，并在其中创建一个学生表student，包含字段：id（整数，主键）、name（变长字符串，最大50）、age（整数）、major（变长字符串，最大100）。",
        "difficulty": "easy",
        "hint": "使用CREATE DATABASE和CREATE TABLE语句，注意openGauss的语法规范。",
        "reference_sql": "CREATE DATABASE student_db;\n\\c student_db\nCREATE TABLE student (\n    id INTEGER PRIMARY KEY,\n    name VARCHAR(50),\n    age INTEGER,\n    major VARCHAR(100)\n);",
        "setup_sql": "",
        "verify_sql": "SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename = 'student';",
        "tags": {"topic": "DDL", "chapter": "1"}
    },
    {
        "chapter": "第1章",
        "title": "插入和查询数据",
        "description": "向student表中插入3条学生记录，然后查询所有年龄大于20岁的学生姓名和专业。",
        "difficulty": "easy",
        "hint": "使用INSERT INTO插入数据，使用SELECT ... WHERE查询。",
        "reference_sql": "INSERT INTO student VALUES (1, '张三', 21, '计算机科学');\nINSERT INTO student VALUES (2, '李四', 19, '数学');\nINSERT INTO student VALUES (3, '王五', 22, '物理');\nSELECT name, major FROM student WHERE age > 20;",
        "setup_sql": "CREATE TABLE student (id INTEGER PRIMARY KEY, name VARCHAR(50), age INTEGER, major VARCHAR(100));",
        "tags": {"topic": "DML", "chapter": "1"}
    },
    {
        "chapter": "第2章",
        "title": "创建视图",
        "description": "基于student表创建一个视图student_view，只包含name和major字段，然后通过该视图查询所有记录。",
        "difficulty": "easy",
        "hint": "使用CREATE VIEW ... AS SELECT语句。",
        "reference_sql": "CREATE VIEW student_view AS SELECT name, major FROM student;\nSELECT * FROM student_view;",
        "setup_sql": "CREATE TABLE student (id INTEGER PRIMARY KEY, name VARCHAR(50), age INTEGER, major VARCHAR(100));\nINSERT INTO student VALUES (1, '张三', 21, '计算机科学');\nINSERT INTO student VALUES (2, '李四', 19, '数学');",
        "tags": {"topic": "视图", "chapter": "2"}
    },
    {
        "chapter": "第2章",
        "title": "创建索引",
        "description": "在student表的name字段上创建一个B-tree索引idx_student_name，并验证索引是否创建成功。",
        "difficulty": "medium",
        "hint": "使用CREATE INDEX语句，查询pg_indexes视图验证。",
        "reference_sql": "CREATE INDEX idx_student_name ON student(name);\nSELECT indexname FROM pg_indexes WHERE tablename = 'student';",
        "setup_sql": "CREATE TABLE student (id INTEGER PRIMARY KEY, name VARCHAR(50), age INTEGER, major VARCHAR(100));",
        "tags": {"topic": "索引", "chapter": "2"}
    },
    {
        "chapter": "第2章",
        "title": "创建存储过程",
        "description": "创建一个存储过程get_student_by_age，接受一个整数参数p_age，查询并返回所有年龄等于该参数的学生记录。",
        "difficulty": "medium",
        "hint": "使用CREATE OR REPLACE PROCEDURE，openGauss中使用REF CURSOR返回结果集。",
        "reference_sql": "CREATE OR REPLACE PROCEDURE get_student_by_age(p_age INTEGER)\nAS\nBEGIN\n    SELECT * FROM student WHERE age = p_age;\nEND;\n/",
        "setup_sql": "CREATE TABLE student (id INTEGER PRIMARY KEY, name VARCHAR(50), age INTEGER, major VARCHAR(100));\nINSERT INTO student VALUES (1, '张三', 21, '计算机科学');\nINSERT INTO student VALUES (2, '李四', 19, '数学');",
        "tags": {"topic": "存储过程", "chapter": "2"}
    },
    {
        "chapter": "第6章",
        "title": "使用EXPLAIN分析查询",
        "description": "对student表执行EXPLAIN分析查询SELECT * FROM student WHERE name = '张三'，并说明执行计划中是否使用了索引。",
        "difficulty": "medium",
        "hint": "使用EXPLAIN关键字前缀查询语句，查看是否出现Index Scan。",
        "reference_sql": "EXPLAIN SELECT * FROM student WHERE name = '张三';",
        "setup_sql": "CREATE TABLE student (id INTEGER PRIMARY KEY, name VARCHAR(50), age INTEGER, major VARCHAR(100));\nCREATE INDEX idx_student_name ON student(name);\nINSERT INTO student SELECT i, 'name'||i, 18+(i%10), 'major'||i FROM generate_series(1,1000) i;",
        "tags": {"topic": "执行计划", "chapter": "6"}
    },
    {
        "chapter": "第6章",
        "title": "生成WDR报告",
        "description": "写出开启WDR快照、创建快照、生成WDR报告的完整SQL语句序列。",
        "difficulty": "hard",
        "hint": "需要先开启enable_wdr_snapshot参数，然后使用create_wdr_snapshot()函数，最后使用generate_wdr_report()函数。",
        "reference_sql": "ALTER SYSTEM SET enable_wdr_snapshot TO on;\nSELECT create_wdr_snapshot();\n\\a \\t \\o ~/wdr_report.html\nSELECT generate_wdr_report(1, 2, 'all', 'cluster', null);",
        "tags": {"topic": "WDR报告", "chapter": "6"}
    },
    {
        "chapter": "第7章",
        "title": "创建全密态表",
        "description": "写出创建客户端主密钥CMK、列加密密钥CEK、以及使用CEK创建加密表的完整SQL语句。",
        "difficulty": "hard",
        "hint": "需要先创建CMK，再创建CEK，最后在CREATE TABLE中使用encrypted with子句。",
        "reference_sql": "CREATE CLIENT MASTER KEY cmk_demo WITH (KEY_STORE = localkms, KEY_PATH = \"key_path_demo\", ALGORITHM = RSA_2048);\nCREATE COLUMN ENCRYPTION KEY cek_demo WITH VALUES (CLIENT_MASTER_KEY = cmk_demo, ALGORITHM = AEAD_AES_256_CBC_HMAC_SHA256);\nCREATE TABLE encrypted_table (id INT, name TEXT ENCRYPTED WITH (COLUMN_ENCRYPTION_KEY = cek_demo, ENCRYPTION_TYPE = DETERMINISTIC));",
        "tags": {"topic": "全密态数据库", "chapter": "7"}
    },
]


async def seed_questions():
    async with async_session() as db:
        for q_data in SQL_QUESTIONS:
            q = SqlQuestion(**q_data)
            db.add(q)
        await db.commit()
    print(f"已导入 {len(SQL_QUESTIONS)} 道SQL练习题")


async def ingest_documents(docx_dir: str):
    processor = DocumentProcessor()
    chunks = processor.extract_documents(docx_dir)
    print(f"提取到 {len(chunks)} 个文档块")

    count = vector_store.add_documents(chunks)
    print(f"已存入 {count} 个向量到Chroma")

    async with async_session() as db:
        result = await knowledge_tree_service.build_tree(docx_dir, db)
        print(f"知识树构建完成: {result}")


async def main():
    await init_db()
    print("数据库初始化完成")

    from app.core.config import settings
    docx_dir = os.environ.get("DOCX_DIR", "") or settings.docx_dir
    if docx_dir and os.path.isdir(docx_dir):
        await ingest_documents(docx_dir)
    else:
        print("未设置DOCX_DIR环境变量，跳过文档导入")

    await seed_questions()
    print("种子数据导入完成")


if __name__ == "__main__":
    asyncio.run(main())