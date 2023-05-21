import os
import logging
import json


DST_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/images-face-master/test"
SRC_PATH = "/Users/liyanxiao/Desktop/西安交大/RoboMaster/images-face-master/train"

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.FileHandler("move_label.log")
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)


actions = []
def move(src:str, dst:str):
    if os.path.exists(dst):
        raise FileExistsError(f"{dst} 已存在")
    else:
        os.rename(src, dst)
        actions.append([src, dst])
        print(f"{src} -> {dst}")
        logger.log(logging.INFO, f"{src} -> {dst}")


def undo(times:int):
    for i in range(times):
        try:
            action = actions.pop()
        except IndexError:
            print("没有可以撤销的操作")
            break
        os.rename(action[1], action[0])
        print(f"撤销操作： {action[1]} -> {action[0]}")
        logger.log(logging.INFO, f"撤销操作： {action[1]} -> {action[0]}")
    

def _find_empty_id(directory:str, suffix='txt'):
    max_id = 0
    acquire_0 = False
    for (root, dirs, files) in os.walk(directory):
        for file in files:
            if isinstance(suffix, list):
                for one in suffix:
                    if file.endswith(f'.{one}'):
                        file_id = int(file.split('.')[0])
                        max_id = max(max_id, file_id)
                        if file.split('.')[0].startswith('0'):
                            acquire_0 = True
            else:
                if file.endswith(f'.{suffix}'):
                    file_id = int(file.split('.')[0])
                    max_id = max(max_id, file_id)
                    if file.split('.')[0].startswith('0'):
                        acquire_0 = True
    
    available_list = []
    for i in range(1, max_id+1):
        if isinstance(suffix, list):
            for one in suffix:
                if not (os.path.exists(os.path.join(directory, f"{i}.{one}"))
                or os.path.exists(os.path.join(directory, "{:0>4d}.{}".format(i, one)))):
                    available_list.append(i)
        else:
            if not (os.path.exists(os.path.join(directory, f"{i}.{suffix}"))
                or os.path.exists(os.path.join(directory, "{:0>4d}.{}".format(i, suffix)))):
                available_list.append(i)
    available_list.append(max_id+1)
    return available_list, acquire_0

"""
将一个标签文件移动到另一个目录
src: 原标签文件的路径
dst_dir: 目标目录，该目录应当包含一个名为"images"的存放图片的子目录与名为"labels"的存放标签的子目录
移动标签文件时，会寻找目标目录空缺的编号并重命名为该编号。如果没有空缺，将原标签文件的编号设置为目标目录中最大编号+1
"""
def move_label(src:str, dst_dir:str):
    if "classes.txt" in src:
        return
    available_label_list, acquire_0 = _find_empty_id(os.path.join(dst_dir, 'labels'),'txt')
    available_image_list, acquire_0 = _find_empty_id(os.path.join(dst_dir, 'images'),['jpg','png'])

    for available_label in available_label_list:
        if available_label in available_image_list:
            if acquire_0:
                dst_txt = os.path.join(dst_dir, 'labels', "{:0>4d}.txt".format(available_label))
                dst_img = os.path.join(dst_dir, 'images', "{:0>4d}.png".format(available_label))
            else:
                dst_txt = os.path.join(dst_dir, 'labels', "{}.txt".format(available_label))
                dst_img = os.path.join(dst_dir, 'images', "{}.png".format(available_label))
            break
    
    if src.endswith('txt'):
        move(src, dst_txt)
        image_dir = os.path.join(os.path.dirname(os.path.dirname(src)), 'images', os.path.basename(src).split('.')[0]+'.png')
        move(image_dir, dst_img)
    elif src.endswith('png'):
        move(src, dst_img)
        label_dir = os.path.join(os.path.dirname(os.path.dirname(src)), 'labels', os.path.basename(src).split('.')[0]+'.txt')
        move(label_dir, dst_txt)


"""
为了和统计标签数量的脚本配合使用留的后门"""
def __backdoor():
    return json.load(open('file_list.json', 'r'))


def main():
    while True:
        choice = input("请输入待移动的文件的文件名（不含路径）：")
        if choice == '-1':
            break
        if choice == 'z':
            undo(2)
            continue
        if choice == 'b':
            try:
                files = __backdoor()
            except FileNotFoundError:
                print("未找到file_list.json")
                continue
            else:
                for file in files:
                    src = os.path.join(SRC_PATH, 'labels', file)
                    try:
                        move_label(src, DST_PATH)
                    except FileNotFoundError as e:
                        print(e.args)
                    except FileExistsError as e:
                        print(e.args)
                continue
        src = os.path.join(SRC_PATH, 'labels', choice+'.txt')
        try:
            move_label(src, DST_PATH)
        except FileNotFoundError as e:
            print(e.args)
            continue
        except FileExistsError as e:
            print(e.args)
            continue


def move_labels(src_dir, dst_dir):
    for (root, dirs, files) in os.walk(src_dir):
        for file in files:
            if file.endswith('txt'):
                src = os.path.join(root, file)
                move_label(src, dst_dir)


if __name__ == '__main__':
    move_labels("/Users/liyanxiao/Desktop/西安交大/RoboMaster/dataset/labels", "/Users/liyanxiao/Desktop/西安交大/RoboMaster/images-face-master/train")