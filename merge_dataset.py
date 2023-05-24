from pycocotools import coco
import rename
import os
from shutil import copyfile
from merge_coco_files import console_main, Config
from clean_coco import clean_ip


MAIN_COCO_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/符/temp2/dataset.json"
MAIN_IMAGE_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/符/temp2/images"
MERGE_COCO_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/符/wmRHQ2_西安交大/dataset_red.json"
MERGE_IMAGE_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/符/wmRHQ2_西安交大/wmRHQ2"
OUTPUT_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/符/temp3"


def merge_dataset(main_coco_path, main_image_path, merge_coco_path, merge_image_path, output_path):
    merge_coco = coco.COCO(merge_coco_path)
    clean_ip(merge_coco)
    rename.split_images(merge_coco, merge_image_path, os.path.join(output_path,'images'))

    rename.rename_from_number(merge_coco_path,  os.path.join(output_path,'images'), rename.get_max_number(main_image_path)+1,
                              rename.get_number_of_zero(main_image_path), os.path.join(output_path, os.path.basename(main_coco_path)))
    main_coco = coco.COCO(main_coco_path)
    clean_ip(main_coco)
    for image in main_coco.dataset['images']:
        copyfile(os.path.join(main_image_path, image['file_name']), os.path.join(output_path, 'images',image['file_name']))
    console_main(Config(None, [main_coco_path, os.path.join(output_path, os.path.basename(main_coco_path))], os.path.join(output_path, "dataset.json")))


if __name__ == '__main__':
    merge_dataset(MAIN_COCO_PATH, MAIN_IMAGE_PATH, MERGE_COCO_PATH, MERGE_IMAGE_PATH, OUTPUT_PATH)