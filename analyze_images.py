import docx
import os
from lxml import etree

doc_dir = r'C:\Users\11523\Desktop\教材文稿'
files = sorted(os.listdir(doc_dir))
doc_file = [f for f in files if f.endswith('.docx') and '第1章' in f][0]
doc = docx.Document(os.path.join(doc_dir, doc_file))

nsmap = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}

for i, para in enumerate(doc.paragraphs[:80]):
    text = para.text.strip()
    if not text and not para._element.findall('.//w:drawing', nsmap):
        continue
    
    drawings = para._element.findall('.//w:drawing', nsmap)
    has_image = len(drawings) > 0
    
    if has_image:
        blips = para._element.findall('.//a:blip', nsmap)
        rids = [b.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed') for b in blips]
        img_desc = []
        for rid in rids:
            if rid:
                try:
                    rel = doc.part.rels[rid]
                    img_desc.append(f"rid={rid} type={rel.reltype.split('/')[-1]}")
                except:
                    img_desc.append(f"rid={rid} (not found)")
        print(f"Para {i}: IMAGE [{', '.join(img_desc)}], text='{text[:50]}'")
    elif '如图' in text or '见图' in text or '下图' in text:
        print(f"Para {i}: FIG_REF, text='{text[:80]}'")