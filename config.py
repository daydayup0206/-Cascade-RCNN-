# category_mapping = {
#     0: ["无疵点"],
#     1: ["破洞"],
#     2: ["水渍", "油渍", "污渍"],
#     3: ["三丝"],
#     4: ["结头"],
#     5: ["花板跳"],
#     6: ["百脚"],
#     7: ["毛粒"],
#     8: ["粗经"],
#     9: ["松经"],
#     10: ["断经"],
#     11: ["吊经"],
#     12: ["粗维"],
#     13: ["纬缩"],
#     14: ["浆斑"],
#     15: ["整经结"],
#     16: ["星跳", "跳花"],
#     17: ["断氨纶"],
#     18: ["稀密档", "浪纹档", "色差档"],
#     19: ["磨痕", "轧痕", "修痕", "烧毛痕"],
#     20: ["死皱", "云织", "双维", "双经", "跳纱", "筘路", "纬纱不良"],
#     21: ["unidentification"],
# }
category_mapping = {
    0: ["area defects"],
    1: ["Warp and weft defects"],
    2: ["Point defects"],
}

threshold = 0.5
# 测试
# print(category_mapping[0])   # 输出: ['无疵点']
# print(category_mapping[1])   # 输出: ['破洞']
# print(category_mapping[2])   # 输出: ['水渍', '油渍', '污渍']
# print(category_mapping[16])  # 输出: ['星跳', '跳花']