from marked import marked
test = '![图片](/images/第1章 数据库概论-已同步_40_7e938f6abb13.png)'
result = marked.parse(test)
print("Output:", result)

test2 = '![图片](/images/前言-已同步_2_535ed87ae8de.png)'
result2 = marked.parse(test2)
print("Output2:", result2)