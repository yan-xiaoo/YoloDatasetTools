# 本文件的功能是
# 输入一个coco文件，一个包含了coco文件对应的图片的文件夹
# 该文件需要和 coco_to_yolo.py放在同一文件夹下
# 输出整理好的一个yolo格式数据集
# - output_yolo
#  - images
#    - 1.png
#    - 2.png
#  - labels
#    - classes.txt
#    - 1.txt
#    - 2.txt
# 大概长这样

# 用法
# 把下面的 COCO_FILE_PATH 改成你的coco文件的路径
# 把下面的 IMAGE_PATH 改成你的图片文件夹的路径
# 把下面的 OUTPUT_PATH 改成你想要输出的文件夹的路径
# 需要安装 pycocotools
# pip install pycocotools

COCO_FILE_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/高云天做的东西/labels_my-project-name_2023-05-15-02-13-16.json"
IMAGE_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/高云天做的东西/energy"
OUTPUT_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/高云天做的东西/yolo_dataset"


import os
from shutil import copyfile
from pycocotools import coco

try:
    from coco_to_yolo import parseJsonFile
except ImportError:
    print("请把 coco_to_yolo.py 和本文件放在同一文件夹下")


"""
由于类Unix系统在移动文件时会静默覆盖文件，就算文件已经存在也不会报错
所以设计了这个当文件移动目标存在时就报错的函数
"""
def move(src:str, dst:str) -> None:
    if os.path.exists(dst):
        raise FileExistsError(f"移动目标位置 {dst} 已存在文件")
    os.rename(src, dst)


"""
给一个file（文件名，不包含路径），一个path（待搜索的文件夹路径，会递归搜索）
返回path文件夹中叫file的文件的路径
"""
def find_file_in_path(file:str, path:str) -> str:
    for root, dirs, files in os.walk(path):
        if file in files:
            return os.path.join(root, file)
    return None


"""
给一个文件名的列表，待查找的文件夹路径
返回一个列表，包含了所有文件的路径
"""
def find_files_in_path(files:list, path:str) -> list:
    return [find_file_in_path(file, path) for file in files]


def main():
    coco_file = coco.COCO(COCO_FILE_PATH)
    file_names = [img['file_name'] for img in coco_file.imgs.values()]
    full_path = find_files_in_path(file_names, IMAGE_PATH)
    choice = None

    while choice not in ['1', '2']:
        choice = input("复制还是移动图片? (1/2): ")
    
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    if not os.path.exists(os.path.join(OUTPUT_PATH, "images")):
        os.makedirs(os.path.join(OUTPUT_PATH, "images"))
    if not os.path.exists(os.path.join(OUTPUT_PATH, "labels")):
        os.makedirs(os.path.join(OUTPUT_PATH, "labels"))
    parseJsonFile(COCO_FILE_PATH, os.path.join(OUTPUT_PATH, "labels"))

    for path in range(len(full_path)):
        if choice  == '1':
            copyfile(full_path[path], os.path.join(OUTPUT_PATH, "images", file_names[path]))
        else:
            move(full_path[path], os.path.join(OUTPUT_PATH, "images", file_names[path]))

if __name__ == '__main__':
    main()