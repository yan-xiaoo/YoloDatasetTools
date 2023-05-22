# 合并多个coco文件
# 用法：参见第32行
# 需要安装pycocotools
# pip install pycocotools

from pycocotools import coco
import json
import os
import copy


"""
    Config class for merge_coco_files.py
    COCO_FILE_DIRECTORY: COCO文件所在的目录，将会合并该目录下的所有coco文件（不递归）
    COCO_FILE_PATH: COCO文件的路径列表，将会合并该列表中的所有coco文件
    注：如果这两个选项都不为空，则会把两者包含的所有coco文件全部合并
    OUTPUT_PATH: 合并后的coco文件的输出路径
"""
class Config:
    COCO_FILE_DIRECTORY = None
    COCO_FILE_PATH = []
    OUTPUT_PATH = None
    """
        coco_directory: COCO文件所在的目录，将会合并该目录下的所有coco文件（不递归）
        coco_file_path: COCO文件的路径列表，将会合并该列表中的所有coco文件
        注：如果这两个选项都不为空，则会把两者包含的所有coco文件全部合并
        output_path: 合并后的coco文件的输出路径
    """
    def __init__(self, coco_directory=None, coco_file_path = None, output_path = None):
        self.COCO_FILE_DIRECTORY = coco_directory
        self.COCO_FILE_PATH = coco_file_path if coco_file_path is not None else []
        self.OUTPUT_PATH = output_path
    
    def __repr__(self) -> str:
        return "Config(COCO_FILE_DIRECTORY={}, COCO_FILE_PATH={}, OUTPUT_PATH={})".format(self.COCO_FILE_DIRECTORY, self.COCO_FILE_PATH, self.OUTPUT_PATH)


# 直接使用时，请修改下面这行中用于初始化Config类的三个参数
# 例如：Config('C:/a', ['C:/b/coco_file_b.json', 'C:/a/coco_file_a.json'], 'C:/a/output.json')
# 会将 C:/a 下的所有coco文件和 C:/b/coco_file_b.json 中的所有coco文件合并
# 输出到 C:/a/output.json
DEFAULT_CONFIG = Config("/Users/liyanxiao/Desktop/西安交大/RoboMaster/new", None, "/Users/liyanxiao/Desktop/西安交大/RoboMaster/new/output.json")


class MergeError(Exception):
    pass

class CategoryError(MergeError):
    pass

class CategoryRepeatError(CategoryError):
    pass

class CategoryNotFoundError(CategoryError):
    pass


"""
    解析config，把其中COCO_FILE_DIRECTORY中的所有文件合并到COCO_FILE_PATH下
    返回一个新的Config类的对像
"""
def parse_config(config:Config) -> Config:
    coco_files_path = config.COCO_FILE_PATH
    if config.COCO_FILE_DIRECTORY is not None:
        # 如果Config.COCO_FILE_DIRECTORY不为空，则将该目录下的所有coco文件合并
        for one_file in os.listdir(config.COCO_FILE_DIRECTORY):
            # 如果一个文件以.json结尾，且不在COCO_FILE_PATH中，则将其加入COCO_FILE_PATH，一起处理
            if one_file.endswith('.json') and one_file not in config.COCO_FILE_PATH and os.path.join(config.COCO_FILE_DIRECTORY, one_file) not in config.COCO_FILE_PATH:
                coco_files_path.append(os.path.join(config.COCO_FILE_DIRECTORY, one_file))
    return Config(None, coco_files_path, config.OUTPUT_PATH)


def merge_coco_files(config:Config = DEFAULT_CONFIG):
    config = parse_config(config)
    coco_files_path = config.COCO_FILE_PATH
    if len(coco_files_path) == 0:
        return
    
    result = coco.COCO(coco_files_path[0])

    for index in range(1, len(coco_files_path)):
        result = merge_two_coco_file(result, coco_files_path[index])
        
    with open(config.OUTPUT_PATH, 'w') as f:
        json.dump(result.dataset, f, indent=4, ensure_ascii=False)

"""
    合并两个coco文件
    main_coco_file_path: 主coco数据集，既可以是文件也可以是个coco.COCO对象
    merge_coco_file_path: 要合并的coco数据集，既可以是文件也可以是个coco.COCO对象
    allow_repeat: 是否允许两个文件中存在对重复图片的标注, 默认为True
        True: 遇到对重复图片的标注时，采用main_coco_file_path那个文件中的标注
        False: 遇到对重复图片的标注时，抛出一个ValueError
    allow_category_merge: 是否允许将main_file中不存在，但在merge_file中存在的category加入到main_file中
        True: 会加入，且category的id为main_file中最大的id+1
        False: 不会加入，遇到这种情况会抛出一个CategoryNotFoundError
    返回这两个coco文件合并后的coco数据集
"""
def merge_two_coco_file(main_coco:str, merge_coco:str, allow_repeat:bool=True, allow_category_merge:bool=True) -> coco.COCO:
    if isinstance(main_coco, coco.COCO):
        main_file = main_coco
    else:
        main_file = coco.COCO(main_coco)
    if isinstance(merge_coco, coco.COCO):
        merge_file = merge_coco
    else:
        merge_file = coco.COCO(merge_coco)
    output = coco.COCO()

    # 合并categories
    category_errors = []
    category_dict = {}
    output.dataset["categories"] = main_file.dataset["categories"]
    for one_category in merge_file.dataset['categories']:
        if one_category['id'] in main_file.cats:
            # 看看main_file与merge_file中同一个id对应的类别名称是否相同
            if main_file.cats[one_category['id']]['name'] != one_category['name']:
                # 纳尼？不相同？
                # 那就看看main_file中有没有与merge_file中同名的类别
                for one_category_id in main_file.cats:
                    if main_file.cats[one_category_id]['name'] == one_category['name']:
                        # 有同名但不同id的类别，抛出异常让上层函数处理
                        # 上层函数应当询问用户这俩类别是否相同
                        # 如果是，则将merge_file中的类别id改为main_file中的类别id
                        # 如果不是，新建一个类别，将merge_file中的类别id改为新建的类别id
                        error = CategoryRepeatError(f"{main_coco} 与 {merge_coco} "
                                                  "中的类别名称重复。", main_file.cats[one_category_id], one_category)
                        error.add_note(f"第一个文件中的类别： {main_file.cats[one_category_id]}")
                        error.add_note(f"第二个文件中的类别： {one_category}")
                        category_errors.append(error)
                        break
                else:
                    # 没有任何一个同名的类别，说明这个类别仅在merge_file中出现
                    if allow_category_merge:
                        # 允许合并，那就合并吧
                        category_dict[one_category['id']] = len(output.dataset['categories']) + 1
                        one_category['id'] = len(output.dataset['categories']) + 1
                        output.dataset['categories'].append(one_category)
                    else:
                        # 虽然但是，找不到同名类别说不定是因为表述不同（比如‘蓝色未击打’和‘蓝未击打’代码上看肯定不一样，但事实上相同）
                        # 上层函数应当询问用户main_file中是否存在与one_category中同义的类别
                        # 如果是，则将merge_file中的类别id改为main_file中的类别id
                        # 如果不是，新建一个类别，将merge_file中的类别id改为新建的类别id
                        error = CategoryNotFoundError(f"{main_coco} 中没有找到 {merge_coco} "
                                                    f"中的类别 {one_category['name']}。", one_category, main_file.cats)
                        error.add_note(f"第一个文件中的所有类别： {main_file.cats}")
                        error.add_note(f"第二个文件中未能找到的类别： {one_category}")
                        category_errors.append(error)
            else:
                category_dict[one_category['id']] = one_category['id']
        else:
            # 考虑一种情况：main: category: {1:{'id':1, 'name': '蓝色已击打}}
            #            merge: category: {1: ... , 2:..., 3:{'id':3, 'name': '蓝色已击打}}
            # 由于main中没有id为3的类别，所以上面不会处理这种情况
            # 但这种情况下显然应该抛出一个CategoryRepeatError,所以在这里检查
            for one_category_id in main_file.cats:
                if main_file.cats[one_category_id]['name'] == one_category['name']:
                    # 有同名但不同id的类别，抛出异常让上层函数处理
                    # 上层函数应当询问用户这俩类别是否相同
                    # 如果是，则将merge_file中的类别id改为main_file中的类别id
                    # 如果不是，新建一个类别，将merge_file中的类别id改为新建的类别id
                    error = CategoryRepeatError(f"{main_coco} 与 {merge_coco} "
                                                  "中的类别名称重复。\n"
                                                  f"第一个文件中的类别： {main_file.cats[one_category_id]}\n"
                                                  f"第二个文件中的类别： {one_category}", main_file.cats[one_category_id], one_category)
                    error.add_note(f"第一个文件中的类别： {main_file.cats[one_category_id]}")
                    error.add_note(f"第二个文件中的类别： {one_category}")
                    category_errors.append(error)
                    break
            else:
                    # 没有任何一个同名的类别，说明这个类别仅在merge_file中出现
                    if allow_category_merge:
                        # 允许合并，那就合并吧
                        category_dict[one_category['id']] = len(output.dataset['categories']) + 1
                        one_category['id'] = len(output.dataset['categories']) + 1
                        output.dataset['categories'].append(one_category)
                    else:
                        # 虽然但是，找不到同名类别说不定是因为表述不同（比如‘蓝色未击打’和‘蓝未击打’代码上看肯定不一样，但事实上相同）
                        # 上层函数应当询问用户main_file中是否存在与one_category中同义的类别
                        # 如果是，则将merge_file中的类别id改为main_file中的类别id
                        # 如果不是，新建一个类别，将merge_file中的类别id改为新建的类别id
                        error = CategoryNotFoundError(f"{main_coco} 中没有找到 {merge_coco} "
                                                    f"中的类别 {one_category['name']}。", one_category, main_file.cats)
                        error.add_note(f"第一个文件中的所有类别： {main_file.cats}")
                        error.add_note(f"第二个文件中未能找到的类别： {one_category}")
                        category_errors.append(error)
    if len(category_errors) > 0:
        raise ExceptionGroup("尝试合并时发生以下错误", category_errors)

    # 合并images部分
    # image_id_table是merge_file中的image_id到main_file中的image_id的映射
    image_id_table = {}
    output.dataset['images'] = main_file.dataset['images']
    for image_data in merge_file.imgs.values():
        file_name = image_data['file_name']
        repeat = False
        for main_image_data in main_file.imgs.values():
            if main_image_data["file_name"] == file_name:
                    repeat = True
        if repeat:
            continue
        image_id = len(output.dataset["images"]) + 1
        image_id_table[image_data["id"]] = image_id
        image_data["id"] = image_id
        output.dataset["images"].append(image_data)

    # 合并annotations部分
    output.dataset['annotations'] = main_file.dataset['annotations']
    for annotation in merge_file.anns.values():
        annotation["id"] = len(output.dataset["annotations"]) + 1
        # 如果此处出现KeyError, 说明merge_file中image_id对应的图片和main_file中的重复了
        # 因此该图片没有被加入output中
        # 所以有关它的所有标注都应当舍弃
        try:
            annotation["image_id"] = image_id_table[annotation["image_id"]]
        except KeyError:
            # 其实直接continue就是舍弃了（）
            continue
        annotation['category_id'] = category_dict[annotation['category_id']]
        output.dataset["annotations"].append(annotation)

    output.createIndex()
    return output


def find_with_name(dataset:coco.COCO, name:str):
    """
    在dataset中查找名称为name的类别
    :param dataset: coco.COCO对象
    :param name: 要查找的类别名称
    :return: 如果找到，返回类别，否则返回None
    """
    for category in dataset.dataset['categories']:
        if category['name'] == name:
            return category
    return None


def change_category_id(dataset:coco.COCO, old_id:int, new_id:int, cache:coco.COCO=None):
    """
    将dataset中所有category_id为old_id更新为new_id
    :param dataset: coco.COCO对象
    :param old_id: 旧的category_id
    :param new_id: 新的category_id
    :return: None
    """
    for annotation in dataset.dataset['annotations']:
        if cache is not None:
            if cache.anns[annotation['id']]['category_id'] == old_id:
                annotation['category_id'] = new_id
        else:
            if annotation['category_id'] == old_id:
                annotation['category_id'] = new_id
    
    for category in dataset.dataset['categories']:
        if cache is not None:
            if find_with_name(cache, category['name'])['id'] == old_id:
                category['id'] = new_id
        else:
            if category['id'] == old_id:
                category['id'] = new_id
    dataset.createIndex()


def delete_category(dataset:coco.COCO, category_id):
    """
    从数据集dataset中删除category_id对应的标签
    """
    for one_category in dataset.dataset['categories'][:]:
        if one_category['id'] == category_id:
            dataset.dataset['categories'].remove(one_category)
    for one_annotation in dataset.dataset['annotations'][:]:
        if one_annotation['category_id'] == category_id:
            dataset.dataset['annotations'].remove(one_annotation)
    dataset.createIndex()


def delete_image(dataset:coco.COCO, image_name):
    """
    从数据集dataset中删除image_name对应的图片
    """
    for one_image in dataset.dataset['images'][:]:
        if one_image['file_name'] == image_name:
            image_id = one_image['id']
            dataset.dataset['images'].remove(one_image)
    for one_annotation in dataset.dataset['annotations'][:]:
        if one_annotation['image_id'] == image_id:
            dataset.dataset['annotations'].remove(one_annotation)
    dataset.createIndex()


def _ask_until_answers(answers, question: str, error_message:str = None):
    """
    询问用户问题，直到用户输入的答案传入function后返回的结果为True中
    :param answers: 一个函数，仅有一个参数，接受用户输入的答案，返回True或False
    :param question: 问题
    :param error_message: 错误提示
    :return: 用户输入的答案
    """
    while True:
        answer = input(question)
        if answers(answer):
            return answer
        else:
            if error_message is not None:
                print(error_message)


def console_main():
    if DEFAULT_CONFIG.COCO_FILE_DIRECTORY is None and DEFAULT_CONFIG.COCO_FILE_PATH == []:
        print("输入一个文件夹可以合并该文件夹下的所有coco文件，输入几个coco文件的路径可以合并这几个文件")
        choice = _ask_until_answers(lambda ans: ans in ['0','1','2'], "请选择输入文件夹还是文件(1/2): ")
        match choice:
            case '0':return
            case '1':
                path = _ask_until_answers(os.path.isdir, "请输入coco文件夹路径: ")
                config = Config(path, None, None)
            case '2':
                paths = []
                while True:
                    path = _ask_until_answers(lambda ans: os.path.isfile(ans) or ans == '0', "请输入coco文件路径(输入0结束): ", "输入的内容不是文件路径")
                    if path == '0':
                        break
                    else:
                        paths.append(path)
                config = Config(None, paths, None)
    if DEFAULT_CONFIG.OUTPUT_PATH is None:
        config.OUTPUT_PATH = _ask_until_answers(lambda ans: os.path.isdir(os.path.dirname(ans)), "请输入输出文件路径: ")
    else:
        config = DEFAULT_CONFIG
    
    config = parse_config(config)
    result = coco.COCO(config.COCO_FILE_PATH[0])
    for path in config.COCO_FILE_PATH[1:]:
        coco_file = coco.COCO(path)
        allow_category_merge = False

        try:
            result = merge_two_coco_file(result, coco_file, allow_category_merge=False, allow_repeat=True)
        except* MergeError:
            stay = True
            allow_category_merge = False
            while stay:
                try:
                    result = merge_two_coco_file(result, coco_file, allow_category_merge=allow_category_merge, allow_repeat=True)
                except* CategoryNotFoundError as e:
                    backup = coco.COCO()
                    backup.dataset = copy.deepcopy(coco_file.dataset)
                    backup.createIndex()
                    for error in e.exceptions:
                        print(f" {error.args[1]} 这个标签没有在之前的文件中出现过。")
                        print(f"之前文件中存在的标签如下：{error.args[2]}")
                        choice = _ask_until_answers(lambda ans: ans in ['0','1'],f"该标签是否与之前文件中的某个标签相同？(1/0): ")
                        if choice == '0':
                            choice2 = _ask_until_answers(lambda ans: ans in ['0','1'], f"是否将其作为新的标签添加至合并后的文件中(1/0): ")
                            if choice2 == '1':
                                allow_category_merge = True
                            else:
                                delete_category(coco_file, error.args[1]['id'])
                        else:
                            print("这个标签与以下哪个标签相同？")
                            for one_annotation in result.cats.values():
                                print(f"{one_annotation['id']}: {one_annotation['name']}")
                            choice3 = _ask_until_answers(lambda ans: ans in [str(one_annotation['id']) for one_annotation in result.cats.values()], "请输入标签id: ")
                            for one in coco_file.dataset['categories']:
                                if one['id'] == int(choice3):
                                    one['name'] = error.args[2][int(choice3)]['name']
                            change_category_id(coco_file, error.args[1]['id'], int(choice3), backup)
                except* CategoryRepeatError as e:
                    backup = coco.COCO()
                    backup.dataset = copy.deepcopy(coco_file.dataset)
                    backup.createIndex()
                    for error in e.exceptions:
                        print(f" {error.args[2]} 这个标签在之前的文件中出现过，但id不同")
                        print(f"之前文件中存在的标签如下：{error.args[1]}")
                        choice = _ask_until_answers(lambda ans: ans in ['0','1'],f"是否认为这两个标签是相同的？(1/0): ")
                        if choice == '1':
                            change_category_id(coco_file, error.args[2]['id'], error.args[1]['id'], backup)
                        else:
                            choice = input(f"请为该标签 {error.args[2]} 修改名称： ")
                            coco_file.dataset['categories'][error.args[2]['id']-1]['name'] = choice
                    allow_category_merge = True
                else:
                    stay = False
                print("完成一轮")
        finally:
            with open(config.OUTPUT_PATH, 'w') as f:
                json.dump(result.dataset, f, indent=4, ensure_ascii=False)
        


if __name__ == '__main__':
    console_main()