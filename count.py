# 统计一个文件夹下所有标签数量
# 用法：
# 修改下面的PATH为待统计的文件夹，然后直接运行


PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/高云天做的东西/yolo_dataset"

import os
import json


NUMBER_TO_LABEL_NAME = {
    0:'哨兵-蓝色',
    1:"一号-蓝色",
    2:"二号-蓝色",
    3:"三号-蓝色",
    4:"四号-蓝色",
    5:"五号-蓝色",
    6:"前哨站-蓝色",
    7:"基地-蓝色",
    8:"基地大装甲-蓝色",
    9:"哨兵-红色",
    10:"一号-红色",
    11:"二号-红色",
    12:"三号-红色",
    13:"四号-红色",
    14:"五号-红色",
    15:"前哨站-红色",
    16:"基地-红色",
    17:"基地大装甲-红色",
    18:"哨兵-熄灭",
    19:"一号-熄灭",
    20:"二号-熄灭",
    21:"三号-熄灭",
    22:"四号-熄灭",
    23:"五号-熄灭",
    24:"前哨站-熄灭",
    25:"基地-熄灭",
    26:"基地大装甲-熄灭",
    27:"哨兵-紫色",
    28:"一号-紫色",
    29:"二号-紫色",
    30:"三号-紫色",
    31:"四号-紫色",
    32:"五号-紫色",
    33:"前哨站-紫色",
    34:"基地-紫色",
    35:"基地大装甲-紫色",
}
    
"""
检查一个标签文件中的许多标签到底属于哪一类
返回一个字典：
    key: 类别数字，类型为int
    value: 该类别的数量，类型为int
通过NUMBER_TO_LABEL_NAME可以将类别数字转换为类别名称（能看懂的）
"""
def type_of_label(path:str, encoding='utf-8') -> dict:
    result = {}
    with open(path, 'r',encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip().split()
            try:
                float(line[0])
            except ValueError:
                raise ValueError(f"标签文件 {path} 格式错误")
            if int(float(line[0])) in result:
                result[int(float((line[0])))] += 1
            else:
                result[int(float(line[0]))] = 1
    return result


"""
把dict2中的内容合并到dict1中
对于dict1中已有的标签，dict2中的标签数量会被加到dict1中
对于dict1中没有的标签，直接添加到dict1中
为了方便各种形式的调用，会返回dict1
"""
def merge_dict(dict1, dict2):
    for key in dict2.keys():
        if key in dict1.keys():
            dict1[key] += dict2[key]
        else:
            dict1[key] = dict2[key]
    return dict1


def sort_dict(d:dict) -> dict:
    new_dict = {}
    for i in range(0,36):
        new_dict[i] = d.get(i,0)
    return new_dict

"""
以递归的方式统计一个文件夹下所有标签文件内部的所有标签的类别
directory: 待遍历的目录
在寻找时，会寻找directory与其子目录下所有txt文件并尝试提取标签的类别

返回:一个字典：
    key: 类别数字，类型为int
    value: 该类别的数量，类型为int
通过NUMBER_TO_LABEL_NAME可以将类别数字转换为类别名称（能看懂的）
"""
def type_of_labels(directory:str):
    result = {};
    for (root, dirs, files) in os.walk(directory):
        for file in files:
            if (file.endswith('.txt')):
                try:
                    file_result = type_of_label(os.path.join(root, file))
                except ValueError as e:
                    print(e)
                    print("该错误可能是因为该txt文件并不是标签文件，已跳过该文件的统计\n")
                merge_dict(result, file_result)
    return result


def main():
    global PATH
    if not os.path.exists(PATH):
        while not os.path.exists(PATH):
            PATH = input("请输入待统计标签的路径: ")
    
    result = type_of_labels(PATH)
    print("""请选择统计数据输出方式:
1. 将类别数字-数量字典输出到output.json
2. 将类别名称-数量输出到output.json
3. 在控制台输出类别数字-数量
4. 在控制台输出类别名称-数量
（示例：类别数字1 对应类别名称为：一号-蓝色""")
    choice = 0
    while choice not in ['1','2','3','4']:
        choice = input("请选择： ")
    if choice == '1':
        result = sort_dict(result)
        with open("output.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
    elif choice == '2':
        result = sort_dict(result)
        new_result = {}
        for label_type, label_num in result.items():
            label_name = NUMBER_TO_LABEL_NAME[label_type]
            new_result[label_name] = label_num
        with open("output.json", 'w', encoding='utf-8') as f:
            json.dump(new_result, f, indent=4, ensure_ascii=False)
    elif choice == '3':
        print("类别数字: 数量")
        for i in range(0,36):
            print(f"{i} : {result.get(i,0)}")
    elif choice == '4':
        print("类别名: 数量")
        for i in range(0,36):
            print(f"{NUMBER_TO_LABEL_NAME[i]} : {result.get(i,0)}")



if __name__ == '__main__':
    main()