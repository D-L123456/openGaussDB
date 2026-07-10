import os
import re
import hashlib

NSMAP = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "images")


def natural_sort_key(s: str) -> list:
    def convert(text):
        return int(text) if text.isdigit() else text.lower()
    return [convert(c) for c in re.split(r'(\d+)', s)]


def extract_images_from_para(para, doc, chapter_name, para_idx, use_markdown: bool = True) -> list[str]:
    image_refs = []
    blips = para._element.findall('.//a:blip', NSMAP)
    for blip in blips:
        rid = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
        if not rid:
            continue
        try:
            rel = doc.part.rels[rid]
            image_blob = rel.target_part.blob
            content_type = rel.target_part.content_type
            ext_map = {
                'image/png': '.png',
                'image/jpeg': '.jpg',
                'image/gif': '.gif',
                'image/bmp': '.bmp',
                'image/tiff': '.tiff',
                'image/x-emf': '.emf',
                'image/x-wmf': '.wmf',
            }
            ext = ext_map.get(content_type, '.png')
            img_hash = hashlib.md5(image_blob).hexdigest()[:12]
            img_filename = f"{chapter_name}_{para_idx}_{img_hash}{ext}"
            img_path = os.path.join(IMAGES_DIR, img_filename)
            if not os.path.exists(img_path):
                os.makedirs(IMAGES_DIR, exist_ok=True)
                with open(img_path, 'wb') as f:
                    f.write(image_blob)
            url_safe_name = img_filename.replace(" ", "%20")
            if use_markdown:
                image_refs.append(f"![图片](/images/{url_safe_name})")
            else:
                image_refs.append(f"[图片: /images/{url_safe_name}]")
        except Exception:
            pass
    return image_refs


def clean_figure_references(text: str) -> str:
    text = re.sub(r'如[图图]\s*\d+[\.\d]*\s*所[示述]', '', text)
    text = re.sub(r'[见参看][图图]\s*\d+[\.\d]*', '', text)
    text = re.sub(r'[上下]图\s*\d+[\.\d]*', '', text)
    text = re.sub(r'图\s*\d+[\.\d]*\s*[所示]', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()