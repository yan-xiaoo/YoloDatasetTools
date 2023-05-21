from pycocotools import coco
import random
import json
import logging


ANNOTATION_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/armor/merge.json"
OUTPUT_TRAIN_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/armor/train_coco.json"
OUTPUT_VAL_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/armor/val_coco.json"
RATE_OF_TRAIN = 0.9
RATE_OF_VAL = 0.1
LOG_FILE_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/数据集管理脚本/split_data.log"


logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.FileHandler(LOG_FILE_PATH)
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)


def copy_basic_info(src, dst):
    if src.dataset.get('info', 0) != 0:
        dst.dataset["info"] = src.dataset["info"]
    if src.dataset.get('categories', 0) != 0:
        dst.dataset["categories"] = src.dataset["categories"]
    dst.createIndex()


def basic_split(annotation_file=ANNOTATION_PATH, output_train_file=OUTPUT_TRAIN_PATH, output_val_file=OUTPUT_VAL_PATH, rate_of_train=RATE_OF_TRAIN):
    annotation_file = coco.COCO(annotation_file)
    images_id_to_choose = [i for i in range(1, len(annotation_file.imgs)+1)]
    images_id_train = []
    for i in range(int(len(images_id_to_choose) * rate_of_train)):
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
        
    with open(output_train_file, "w") as f:
        json.dump(train_file.dataset, f, indent=4, ensure_ascii=False)

    with open(output_val_file, "w") as f:
        json.dump(val_file.dataset, f, indent=4, ensure_ascii=False)


def category_split(annotation_file=ANNOTATION_PATH, output_train_file=OUTPUT_TRAIN_PATH, output_val_file=OUTPUT_VAL_PATH, output_test_file=None, rate_of_train=RATE_OF_TRAIN, rate_of_val=RATE_OF_VAL, rate_of_test=1-RATE_OF_TRAIN-RATE_OF_VAL):
    annotation = coco.COCO(annotation_file)
    train_file = coco.COCO()
    val_file = coco.COCO()
    test_file = coco.COCO()

    copy_basic_info(annotation, train_file)
    copy_basic_info(annotation, val_file)
    copy_basic_info(annotation, test_file)

    for category_id in annotation.getCatIds():
        category_images =  annotation.getImgIds(catIds=category_id)
        num_of_train = int(len(category_images) * rate_of_train)
        num_of_val = int(len(category_images) * rate_of_val)
        num_of_test = int(len(category_images) * rate_of_test)

        # 为了防止没有验证集和测试集，将训练集的数量减少
        if num_of_val == 0 and num_of_train > 1 and rate_of_val != 0:
            num_of_val = 1
            num_of_train -= 1
        if num_of_test == 0 and num_of_train > 1 and rate_of_test != 0:
            num_of_test = 1
            num_of_train -= 1

        logger.info("category_id: %d, num_of_train: %d, num_of_val: %d, num_of_test: %d" % (category_id, num_of_train, num_of_val, num_of_test))
        for _ in range(num_of_train):
            image_id = random.choice(category_images)
            category_images.remove(image_id)
            img = annotation.loadImgs(image_id)[0]
            train_file.imgs[image_id] = img
            anns = annotation.loadAnns(annotation.getAnnIds(imgIds=image_id))[0]
            train_file.anns[image_id] = anns
        

        for _ in range(num_of_val):
            image_id = random.choice(category_images)
            category_images.remove(image_id)
            img = annotation.loadImgs(image_id)[0]
            val_file.imgs[image_id] = img
            anns = annotation.loadAnns(annotation.getAnnIds(imgIds=image_id))[0]
            val_file.anns[image_id] = anns
        
        if num_of_test != 0:
            for _ in range(num_of_test):
                image_id = random.choice(category_images)
                category_images.remove(image_id)
                img = annotation.loadImgs(image_id)[0]
                test_file.imgs[image_id] = img
                anns = annotation.loadAnns(annotation.getAnnIds(imgIds=image_id))[0]
                test_file.anns[image_id] = anns

    train_file.dataset["images"] = list(train_file.imgs.values())
    train_file.dataset["annotations"] = list(train_file.anns.values())

    val_file.dataset["images"] = list(val_file.imgs.values())
    val_file.dataset["annotations"] = list(val_file.anns.values())

    if output_test_file is not None:
        test_file.dataset["images"] = list(test_file.imgs.values())
        test_file.dataset["annotations"] = list(test_file.anns.values())
    
    with open(output_train_file, "w") as f:
        json.dump(train_file.dataset, f, indent=4, ensure_ascii=False)
    with open(output_val_file, 'w') as f:
        json.dump(val_file.dataset, f, indent=4, ensure_ascii=False)
    if output_test_file is not None:
        with open(output_test_file, 'w') as f:
            json.dump(test_file.dataset, f, indent=4, ensure_ascii=False)
    

if __name__ == '__main__':
    category_split(ANNOTATION_PATH, OUTPUT_TRAIN_PATH, OUTPUT_VAL_PATH, None, RATE_OF_TRAIN, RATE_OF_VAL, 0)