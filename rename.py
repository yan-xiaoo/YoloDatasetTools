from pycocotools import coco
import os
import json
from shutil import copyfile


COCO_FILE_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/sb_2/train.json"
COCO_OUTPUT_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/sb_2/train_renamed/train.json"
IMAGE_MERGE_DIRECTORY = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/sb_2"
IMAGE_OUTPUT_DIRECTORY = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/sb_2/train_renamed"
IMAGE_MAIN_DIRECTORY = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/armor/装甲板_yolo_train/images"


def rename(src, dst):
    if os.path.exists(dst):
        raise FileExistsError("File already exists: {}".format(dst))
    os.rename(src, dst)


def get_max_number(directory):
    paths = os.listdir(directory)
    max_number = 0
    for path in paths:
        if (path.endswith('.jpg') or path.endswith('.png')) and int(path.split('.')[0]) > max_number :
            max_number = int(path.split('.')[0])
    return max_number


def get_number_of_zero(directory):
    paths = os.listdir(directory)
    max_number = 0
    max_path = None
    for path in paths:
        if (path.endswith('.jpg') or path.endswith('.png')) and int(os.path.basename(path).split('.')[0]) > max_number:
            max_number = int(os.path.basename(path).split('.')[0])
            max_path = path
    
    number = 0
    for char in os.path.basename(max_path).split('.')[0]:
        if char == '0':
            number += 1
        else:
            break
    return number + len(str(max_number))


def rename_from_number(coco_file, directory, number, number_of_zeros, output_path=None):
    coco_data = coco.COCO(coco_file)
    images = os.listdir(directory)
    max_number_now = max(get_max_number(directory), number)
    image_old_to_new = {}
    image_path_old_to_new = {}
    suffix = images[0].split('.')[-1]
    template = "{:0>"+str(number_of_zeros)+"d}"
    for image in images:
        image_path_old_to_new[os.path.join(directory, image)] = os.path.join(directory, template.format(max_number_now+1)+"."+suffix)
        rename(os.path.join(directory, image), os.path.join(directory, template.format(max_number_now+1)+"."+suffix))
        max_number_now += 1
    for image in images:
        rename(image_path_old_to_new[os.path.join(directory, image)], os.path.join(directory, template.format(number)+"."+suffix))
        image_old_to_new[image] = template.format(number)+"."+suffix
        number += 1
    for one_image in coco_data.dataset['images']:
        one_image['file_name'] = image_old_to_new[one_image['file_name']]
    if output_path is None:
        output_path = coco_file
    with open(output_path, 'w') as f:
        json.dump(coco_data.dataset, f, indent=4, ensure_ascii=False)


def split_images(coco_file:coco.COCO, directory, output_dir):
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    for one_image in coco_file.dataset['images']:
        copyfile(os.path.join(directory, one_image['file_name']), os.path.join(output_dir, one_image['file_name']))


def main():
    global COCO_FILE_PATH
    global COCO_OUTPUT_PATH
    global IMAGE_MERGE_DIRECTORY
    global IMAGE_MAIN_DIRECTORY
    global IMAGE_OUTPUT_DIRECTORY
    split_images(coco.COCO(COCO_FILE_PATH), IMAGE_MERGE_DIRECTORY, IMAGE_OUTPUT_DIRECTORY)
    rename_from_number(COCO_FILE_PATH, IMAGE_OUTPUT_DIRECTORY, get_max_number(IMAGE_MAIN_DIRECTORY)+1, get_number_of_zero(IMAGE_MAIN_DIRECTORY), COCO_OUTPUT_PATH)


if __name__ == '__main__':
    main()