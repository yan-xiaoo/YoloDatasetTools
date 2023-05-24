from pycocotools import coco
import random
import json
import logging


ANNOTATION_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/armor/merge.json"
OUTPUT_TRAIN_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/armor/train_coco.json"
OUTPUT_VAL_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/armor/val_coco.json"
RATE_OF_TRAIN = 0.9
RATE_OF_VAL = 0.1
LOG_FILE_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/dataset_scripts/split_data.log"


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


def split_to_number(annotation_path, output_path, number):
    '''
    按类别平均减少来缩小一个数据集，直到它包含的图片数量等于number
    '''
    annotation = coco.COCO(annotation_path)
    output_file = coco.COCO()

    copy_basic_info(annotation, output_file)

    length = len(annotation.imgs)
    number_left = number
    for category_id in annotation.getCatIds():
        category_images =  annotation.getImgIds(catIds=category_id)
        len_of_category = len(category_images)
        print(len_of_category, length)
        for _ in range(int(len_of_category / length * number)):
            try:
                image_id = random.choice(category_images)
            except IndexError:
                break
            else:
                number_left -= 1
            category_images.remove(image_id)
            img = annotation.loadImgs(image_id)[0]
            output_file.imgs[image_id] = img
            anns = annotation.loadAnns(annotation.getAnnIds(imgIds=image_id))[0]
            output_file.anns[image_id] = anns
    if number_left > 0:
        print(number_left)
        images = annotation.dataset['images'][:]
        for _ in range(number_left):
            image = random.choice(images)
            images.remove(image)
            print(image)
            img = annotation.loadImgs(image['id'])[0]
            output_file.imgs[image['id']] = img
            anns = annotation.loadAnns(annotation.getAnnIds(imgIds=image['id']))[0]
            output_file.anns[image['id']] = anns


    output_file.dataset["images"] = list(output_file.imgs.values())
    output_file.dataset["annotations"] = list(output_file.anns.values())

    with open(output_path, "w") as f:
        json.dump(output_file.dataset, f, indent=4, ensure_ascii=False)


def split_to_category(annotation_path:str, categories:list, output_path:str):
    """
    从一个数据集中留下指定的类别，其他都删除
    categories: 要保留的类别的id，是一个列表
    """
    from merge_coco_files import delete_category
    annotation = coco.COCO(annotation_path)
    output = coco.COCO(annotation_path)
    for category in annotation.dataset['categories']:
        if category['id'] not in categories:
            delete_category(output, category['id'])
    with open(output_path, "w") as f:
        json.dump(output.dataset, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    category_split("/Users/liyanxiao/Desktop/西安交大/RoboMaster/符/temp3/dataset.json", 
                   "/Users/liyanxiao/Desktop/西安交大/RoboMaster/符/temp3/dataset_train.json",
                   "/Users/liyanxiao/Desktop/西安交大/RoboMaster/符/temp3/dataset_val.json",
                   None, 0.9,0.1,0)
    