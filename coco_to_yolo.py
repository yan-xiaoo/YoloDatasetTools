# 原始来源： https://github.com/KKKSQJ/DeepLearning/blob/master/others/label_convert/coco2yolo.py
# 作者github仓库: https://github.com/KKKSQJ/DeepLearning
# 在原作者基础上进行了一定修改，输出yolo-pose而不是作者写的yolo格式

# 用法1: 
# python coco_to_yolo.py --json-path /home/xxx/xxx.json --save-path /home/xxx/xxx
# 或者
# python coco_to_yolo.py -jp /home/xxx/xxx.json -s /home/xxx/xxx
# --json-path 或者 -jp: coco格式的json文件路径
# --save-path 或者 -s: 保存yolo格式的许多txt的文件夹

# 用法2:
# 把下面那个 COCO_FILE_PATH 的值从None改成需要转换的coco文件的路径
# 把下面那个 YOLO_OUTPUT_DIRECTORY 的值从None改成需要保存的yolo格式的txt文件的文件夹（可以是不存在的文件夹，会自动创建）
# 然后直接运行这个文件

# 使用前需要安装pycocotools和tqdm
# pip install pycocotools
# pip install tqdm


COCO_FILE_PATH = None
YOLO_OUTPUT_DIRECTORY = None

from pycocotools.coco import COCO
import os
import shutil
from tqdm import tqdm
import sys
import argparse

images_nums = 0
category_nums = 0
bbox_nums = 0

# 将类别名字和id建立索引
def catid2name(coco):
    classes = dict()
    for cat in coco.dataset['categories']:
        classes[cat['id']] = cat['name']
    return classes


# 将[xmin,ymin,xmax,ymax]转换为yolo格式[x_center, y_center, w, h](做归一化)
def xyxy2xywhn(object, width, height):
    cat_id = object[0]
    xn = object[1] / width
    yn = object[2] / height
    wn = object[3] / width
    hn = object[4] / height
    for index in range(5, len(object)):
        object[index][0] = object[index][0] / width
        object[index][1] = object[index][1] / height
    out = "{} {} {} {} {}".format(cat_id, xn, yn, wn, hn)
    for index in range(5, len(object)):
        out += " {} {}".format(object[index][0], object[index][1])
    return out


def save_anno_to_txt(images_info, save_path):
    filename = images_info['filename']
    txt_name = filename[:-3] + "txt"
    with open(os.path.join(save_path, txt_name), "w") as f:
        for obj in images_info['objects']:
            line = xyxy2xywhn(obj, images_info['width'], images_info['height'])
            f.write("{}\n".format(line))


# 利用cocoAPI从json中加载信息
def load_coco(anno_file, xml_save_path):
    if os.path.exists(xml_save_path):
        shutil.rmtree(xml_save_path)
    os.makedirs(xml_save_path)

    coco = COCO(anno_file)
    classes = catid2name(coco)
    imgIds = coco.getImgIds()
    classesIds = coco.getCatIds()

    with open(os.path.join(xml_save_path, "classes.txt"), 'w') as f:
        for id in classesIds:
            f.write("{}\n".format(classes[id]))

    for imgId in tqdm(imgIds):
        info = {}
        img = coco.loadImgs(imgId)[0]
        filename = img['file_name']
        width = img['width']
        height = img['height']
        info['filename'] = filename
        info['width'] = width
        info['height'] = height
        annIds = coco.getAnnIds(imgIds=img['id'], iscrowd=None)
        anns = coco.loadAnns(annIds)

        categories = coco.dataset['categories']
        min_category = 100000
        for cate in categories:
            if cate['id'] < min_category:
                min_category = cate['id']

        objs = []
        for ann in anns:
            object_name = classes[ann['category_id']]
            # bbox:[x,y,w,h]
            
            bbox = list(map(float, ann['bbox']))
            xc = bbox[0] + bbox[2] / 2.
            yc = bbox[1] + bbox[3] / 2.
            w = bbox[2]
            h = bbox[3]

            segmentation = []
            for index in range(0,len(ann['segmentation'][0]),2):
                segmentation.append([float(ann['segmentation'][0][index]), float(ann['segmentation'][0][index+1])])

            obj = [ann['category_id'] - min_category, xc, yc, w, h]
            obj.extend(segmentation)
            objs.append(obj)
        info['objects'] = objs
        save_anno_to_txt(info, xml_save_path)


def parseJsonFile(json_path, txt_save_path):
    assert os.path.exists(json_path), "json path:{} does not exists".format(json_path)
    if os.path.exists(txt_save_path):
        shutil.rmtree(txt_save_path)
    os.makedirs(txt_save_path)

    assert json_path.endswith('json'), "json file:{} It is not json file!".format(json_path)

    load_coco(json_path, txt_save_path)


if __name__ == '__main__':
    """
    脚本说明：
        该脚本用于将coco格式的json文件转换为yolo格式的txt文件
    参数说明：
        json_path:json文件的路径
        txt_save_path:txt保存的路径
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-jp', '--json-path', type=str, default='./data/labels/coco/train.json', help='json path')
    parser.add_argument('-s', '--save-path', type=str, default='./data/convert/yolo', help='txt save path')
    opt = parser.parse_args()

    if len(sys.argv) > 1:
        print(opt)
        parseJsonFile(opt.json_path, opt.save_path)
        # print("image nums: {}".format(images_nums))
        # print("category nums: {}".format(category_nums))
        # print("bbox nums: {}".format(bbox_nums))
    elif COCO_FILE_PATH is not None and os.path.exists(COCO_FILE_PATH):
        if YOLO_OUTPUT_DIRECTORY is not None and not os.path.isdir(YOLO_OUTPUT_DIRECTORY):
            choice = input(f"输出目录 {YOLO_OUTPUT_DIRECTORY} 不存在，是否创建? [y/n]")
            if choice == "y":
                os.makedirs(YOLO_OUTPUT_DIRECTORY)
            else:
                exit(0)
            parseJsonFile(COCO_FILE_PATH, YOLO_OUTPUT_DIRECTORY)
        elif YOLO_OUTPUT_DIRECTORY is not None:
            parseJsonFile(COCO_FILE_PATH, YOLO_OUTPUT_DIRECTORY)
        else:
            print("没有填写YOLO文件输出位置，请阅读该脚本开头的注释部分，按照方法使用")
    else:
        print("用法不正确，请阅读该脚本开头的注释部分，按照方法使用")
