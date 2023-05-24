from pycocotools import coco
import json


COCO_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/符/官方符/merged/dataset_red_副本.json"


def clean_ip(coco_file:coco.COCO):
    for image in coco_file.imgs.copy().values():
        if len(coco_file.getAnnIds(imgIds=image['id'])) == 0:
            coco_file.dataset['images'].remove(image)
            coco_file.imgs.pop(image['id'])
    
    for category in coco_file.cats.copy().values():
        if len(coco_file.getImgIds(catIds=category['id'])) == 0:
            coco_file.dataset['categories'].remove(category)
            coco_file.cats.pop(category['id'])
    return coco_file


def clean(coco_path = COCO_PATH):
    coco_file = coco.COCO(coco_path)
    
    for image in coco_file.imgs.copy().values():
        if len(coco_file.getAnnIds(imgIds=image['id'])) == 0:
            coco_file.dataset['images'].remove(image)
            coco_file.imgs.pop(image['id'])
    
    for category in coco_file.cats.copy().values():
        if len(coco_file.getImgIds(catIds=category['id'])) == 0:
            coco_file.dataset['categories'].remove(category)
            coco_file.cats.pop(category['id'])

    with open(coco_path, 'w') as f:
        json.dump(coco_file.dataset, f, indent=4, ensure_ascii=False)


if __name__  == "__main__":
    a = clean_ip(coco.COCO("/Users/liyanxiao/Desktop/西安交大/RoboMaster/符/temp2/dataset.json"))
    print(len(a.imgs))