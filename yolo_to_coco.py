# yolo_to_coco.py
# 将yolo格式的txt标签转换为coco格式的json
# 用法：
# 修改下面那个YOLO_LABELS_DIRECTORY的值为yolo格式的labels那个文件夹的路径
# 修改下面那个YOLO_IMAGES_DIRECTORY的值为yolo格式的images那个文件夹的路径（因为需要获取图片的信息）
# 修改COCO_PATH为输出的COCO文件的路径
# (可选) 如果YOLO_DIRECTORY文件夹中没有classes.txt, 可以手动指定CLASS_PATH为classes.txt的路径

# 使用前需要安装opencv-python, tqdm
# pip install opencv-python
# pip install tqdm


YOLO_LABELS_DIRECTORY = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/windmill/energyTrain_yolo/labels"
YOLO_IMAGES_DIRECTORY = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/windmill/energyTrain_yolo/images"
COCO_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/windmill/energyTrain_yolo/coco.json"
CLASS_PATH = None


import os
import cv2
import json
from tqdm import tqdm


def get_classes(classes_path):
    with open(classes_path) as f:
        content = f.readlines()
    class_names = [{"id":index+1, "name":line.strip()} for index, line in enumerate(content)]
    return class_names


def get_size(image_path):
    image = cv2.imread(image_path)
    height, width, _ = image.shape
    return width, height


def get_image(image_path, image_id):
    width, height = get_size(image_path)
    return {"id": image_id, "width": width, "height": height, "file_name": os.path.basename(image_path)}


def get_images(image_directory):
    image_paths = [os.path.join(image_directory, file_name) for file_name in os.listdir(image_directory)]
    images = []
    name_to_image_id = {}
    for image_id, image_path in tqdm(enumerate(image_paths), "生成图片信息中"):
        name_to_image_id[os.path.basename(image_path).split('.')[0]] = image_id+1
        images.append(get_image(image_path, image_id+1))
    return images, name_to_image_id


def get_annotation(label_path, name_to_image_id, annotation_id, width, height):
    # yolo_bbox
    # [x_center, y_center, w, h]
    # coco_bbox
    # [x, y, w, h]
    # x,y为box左上角的坐标
    annotations = []
    with open(label_path) as f:
        content = f.readlines()
    for line in content:
        line = line.strip().split()
        class_id = int(line[0]) + 1; x_center = float(line[1]); y_center = float(line[2]); bbox_width = float(line[3]); bbox_height = float(line[4]);points = line[5:]
        points = list(map(float, points))
        for index, point in enumerate(points):
            points[index] = point*width if index%2==0 else point*height

        bbox = [(x_center-bbox_width/2)*width, (y_center-bbox_height/2)*height, bbox_width*width, bbox_height*height]

        image_id = name_to_image_id[os.path.basename(label_path).split('.')[0]]
        annotations.append({"id": annotation_id,"iscrowd": 0, "image_id": image_id, 
                            "category_id": class_id, 
                            "segmentation": [points],
                            "bbox": bbox,
                            "area": bbox_width*bbox_height*width*height,
                            })
        annotation_id += 1
                                
    return annotations


def get_annotations(label_directory, image_directory, name_to_image_id):
    annotations = []
    annotation_id = 0
    paths = [os.path.join(label_directory, file_name) for file_name in os.listdir(label_directory) if file_name.endswith(".txt") and "classes" not in  file_name]
    for label_path in tqdm(paths, "生成标签中"):
        image_path = os.path.basename(label_path).split('.')[0]
        for image in os.listdir(image_directory):
            if image_path in image:
                suffix = image.split('.')[-1]
        width, height = get_size(label_path.replace("labels", "images").replace("txt", suffix))
        annotations.extend(get_annotation(label_path, name_to_image_id, annotation_id, width, height))
        annotation_id += len(annotations)
    return annotations


def main():
    coco = {}
    global CLASS_PATH
    CLASS_PATH = os.path.join(YOLO_LABELS_DIRECTORY, "classes.txt") if CLASS_PATH is None else CLASS_PATH
    coco['categories'] = get_classes(CLASS_PATH)
    coco['images'], name_to_image_id = get_images(YOLO_IMAGES_DIRECTORY)
    coco['annotations'] = get_annotations(YOLO_LABELS_DIRECTORY, YOLO_IMAGES_DIRECTORY, name_to_image_id)
    with open(COCO_PATH, 'w') as f:
        json.dump(coco, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()