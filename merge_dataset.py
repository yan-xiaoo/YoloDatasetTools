from pycocotools import coco
import rename
import os
from shutil import copyfile
from merge_coco_files import console_main, Config


MAIN_COCO_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/armor/train_coco.json"
MAIN_IMAGE_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/armor/装甲板_yolo_train/images"
MERGE_COCO_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/sb_2/train.json"
MERGE_IMAGE_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/sb_2"
OUTPUT_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/armor/train_merge"


def merge_dataset(main_coco_path, main_image_path, merge_coco_path, merge_image_path, output_path):
    rename.split_images(coco.COCO(merge_coco_path), merge_image_path, output_path)
    rename.rename_from_number(merge_coco_path, output_path, rename.get_max_number(main_image_path)+1,
                              rename.get_number_of_zero(main_image_path), os.path.join(output_path, os.path.basename(main_coco_path)))
    for image in coco.COCO(main_coco_path).imgs.values():
        copyfile(os.path.join(main_image_path, image['file_name']), os.path.join(output_path, image['file_name']))
    console_main(Config(None, [main_coco_path, os.path.join(output_path, os.path.basename(main_coco_path))], os.path.join(output_path, "dataset.json")))


if __name__ == '__main__':
    merge_dataset(MAIN_COCO_PATH, MAIN_IMAGE_PATH, MERGE_COCO_PATH, MERGE_IMAGE_PATH, OUTPUT_PATH)