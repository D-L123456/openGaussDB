import sys
import os
sys.path.insert(0, r"C:\Users\11523\Desktop\新建文件夹\opengauss-agent\backend")

import docx
from app.services.knowledge_tree import extract_images_from_para, NSMAP

docx_dir = r"C:\Users\11523\Desktop\教材文稿"
files = sorted(os.listdir(docx_dir))
first_docx = [f for f in files if f.endswith(".docx")][0]
print(f"Testing: {first_docx}")

filepath = os.path.join(docx_dir, first_docx)
doc = docx.Document(filepath)
chapter_name = first_docx.replace(".docx", "")

for i, para in enumerate(doc.paragraphs[:50]):
    refs = extract_images_from_para(para, doc, chapter_name, i)
    if refs:
        print(f"  Para {i}: Found {len(refs)} images: {refs[0][:60]}")