# 检测一个coco数据集的关键点数量对不对
# 使用方法：
# 修改下面这个字典，key是类别的id，value是这个类别应当有的关键点数量
# 例如：
# 对于一个 category为: [{id:1, name:"蓝色未击打"}] 的数据集，如果要限制其“蓝色未击打”标签的关键点数量为4，那么就应该写成：
# KEYPOINTS_NUM = {1:4}
KEYPOINTS_NUM = {}
# 再修改下面这个路径，改成待检测coco数据集的路径
COCO_FILE_PATH = ""


from pycocotools import coco
import os


def count_keypoints(coco_file_path, keypoints_num=KEYPOINTS_NUM):
    wrong_annotations = []
    coco_file = coco.COCO(coco_file_path)
    for image_id in coco_file.imgs:
        anns = coco_file.loadAnns(coco_file.getAnnIds(imgIds=image_id))
        for ann in anns:
            if ann["category_id"] in keypoints_num:
                if len(ann["segmentation"][0]) != keypoints_num[ann["category_id"]] * 2:

                    wrong_annotations.append(ann)
    return wrong_annotations


def main():
    global COCO_FILE_PATH
    if KEYPOINTS_NUM == {}:
        print("请先修改KEYPOINTS_NUM字典！")
        return
    if not os.path.exists(COCO_FILE_PATH):
        choice = ''
        while not os.path.isfile(choice):
            choice = input("请输入coco数据集的路径：")
        COCO_FILE_PATH = choice
    
    coco_file = coco.COCO(COCO_FILE_PATH)
    wrong_annotations = count_keypoints(COCO_FILE_PATH)
    if len(wrong_annotations) == 0:
        print("这个数据集的关键点数量都是对的！")
    else:
        print("以下图片的关键点数量存在问题：")
        for ann in wrong_annotations:
            print(coco_file.loadImgs(ann["image_id"])[0]["file_name"])


if __name__ == "__main__":
    main()