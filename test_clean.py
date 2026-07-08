import sys
sys.path.insert(0, r"C:\Users\11523\Desktop\新建文件夹\opengauss-agent\backend")

from app.services.knowledge_tree import clean_figure_references

test = "（1）openGauss 体系结构\n![图片](/images/前言-已同步_24_0d93d4b5c1fa.png)\n图2.3 openGauss体系结构\n如图2.3所示"
result = clean_figure_references(test)
print("Before:", repr(test[:100]))
print("After:", repr(result[:100]))
print("Has image before:", "/images/" in test)
print("Has image after:", "/images/" in result)