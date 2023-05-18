from pycocotools import coco
import random
import json


ANNOTATION_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/labels_my-project-name_2023-05-14-01-09-56.json"
OUTPUT_TRAIN_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/train_coco.json"
OUTPUT_VAL_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/val_coco.json"
RATE_OF_TRAIN = 0.9


def copy_basic_info(src, dst):
    dst.dataset["categories"] = src.dataset["categories"]
    dst.dataset["info"] = src.dataset["info"]
    dst.createIndex()

annotation_file = coco.COCO(ANNOTATION_PATH)

images_id_to_choose = [i for i in range(1, len(annotation_file.imgs)+1)]
images_id_train = []
for i in range(int(len(images_id_to_choose) * RATE_OF_TRAIN)):
    images_id_train.append(random.choice(images_id_to_choose))
    images_id_to_choose.remove(images_id_train[-1])

train_file = coco.COCO()
val_file = coco.COCO()

copy_basic_info(annotation_file, train_file)
copy_basic_info(annotation_file, val_file)

for image_id in images_id_train:
    img = annotation_file.loadImgs(image_id)[0]
    train_file.imgs[image_id] = img
    anns = annotation_file.loadAnns(annotation_file.getAnnIds(imgIds=image_id))[0]
    train_file.anns[image_id] = anns

train_file.dataset["images"] = list(train_file.imgs.values())
train_file.dataset["annotations"] = list(train_file.anns.values())

for image_id in images_id_to_choose:
    img = annotation_file.loadImgs(image_id)[0]
    val_file.imgs[image_id] = img
    anns = annotation_file.loadAnns(annotation_file.getAnnIds(imgIds=image_id))[0]
    val_file.anns[image_id] = anns

val_file.dataset["images"] = list(val_file.imgs.values())
val_file.dataset["annotations"] = list(val_file.anns.values())
    
with open(OUTPUT_TRAIN_PATH, "w") as f:
    json.dump(train_file.dataset, f, indent=4, ensure_ascii=False)

with open(OUTPUT_VAL_PATH, "w") as f:
    json.dump(val_file.dataset, f, indent=4, ensure_ascii=False)

temp1 = coco.COCO(OUTPUT_TRAIN_PATH)
temp2 = coco.COCO(OUTPUT_VAL_PATH)
assert len(temp1.dataset["images"]) + len(temp2.dataset["images"]) == len(annotation_file.dataset["images"])