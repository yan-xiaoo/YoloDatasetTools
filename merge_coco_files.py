# 合并多个coco文件
# 用法：参见第32行
# 需要安装pycocotools
# pip install pycocotools

from pycocotools import coco
import json
import os


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
    
    def parse(self):
        """
        解析配置，将self.COCO_FILE_DIRECTORY中的所有json文件添加到COCO_FILE_PATH下，
        并清空self.COCO_FILE_DIRECTORY
        """
        coco_files = []
        if self.COCO_FILE_DIRECTORY is not None:
            for file in os.listdir(self.COCO_FILE_DIRECTORY):
                if file.endswith('json') and not file in self.COCO_FILE_PATH and not os.path.join(self.COCO_FILE_DIRECTORY, file) in self.COCO_FILE_PATH:
                    coco_files.append(os.path.join(self.COCO_FILE_DIRECTORY, file))
        if self.COCO_FILE_PATH is not None :
            coco_files.extend(self.COCO_FILE_PATH)
        
        return Config(None, coco_files, output_path=self.OUTPUT_PATH)


# 直接使用时，请修改下面这行中用于初始化Config类的三个参数
# 例如：Config('C:/a', ['C:/b/coco_file_b.json', 'C:/a/coco_file_a.json'], 'C:/a/output.json')
# 会将 C:/a 下的所有coco文件和 C:/b/coco_file_b.json 中的所有coco文件合并
# 输出到 C:/a/output.json
DEFAULT_CONFIG = Config("/Users/liyanxiao/Desktop/西安交大/RoboMaster/符/wmR_交大隔着铁丝网拍的", None, "/Users/liyanxiao/Desktop/西安交大/RoboMaster/符/wmR_交大隔着铁丝网拍的/dataset.json")


def merge_coco_files(config:Config = DEFAULT_CONFIG):
    config = config.parse()
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
    allow_category_merge: 是否允许将main_file中不存在，但在merge_file中存在的category加入到main_file中
        True: 会加入，且category的id为main_file中最大的id+1
        False: 不会加入，返回错误信息
    返回这两个coco文件合并后的coco数据集
    如果有错误：返回一个包含错误信息的列表

    错误信息格式：
    1. {'name':'CategoryNameRepeat', 'detail':'(一个category对像)与(另一个category对象)的名称冲突', 'object':[(第一个category对象), (第二个category对象)]}
    2. {'name':'CategoryNotFound', 'detail':'(category对象)未在被合并文件中找到', 'object':[(没找到的那个category对象), (另一个文件所有category对象)]}
    第二种错误仅在allow_category_merge=False时出现
    category对象:
    {'id':int, 'name': str}
"""
def merge_two_coco_file(main_coco:str, merge_coco:str, allow_category_merge:bool=True) -> coco.COCO:
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
                        # 有同名但不同id的类别，返回错误信息让上层函数处理
                        # 上层函数应当询问用户这俩类别是否相同
                        # 如果是，则将merge_file中的类别id改为main_file中的类别id
                        # 如果不是，新建一个类别，将merge_file中的类别id改为新建的类别id
                        category_errors.append({'name':'CategoryNameRepeat', 
                                                'detail': f'{one_category} 与 {main_file.cats[one_category_id]} 的名称重复',
                                                'object': [one_category, main_file.cats[one_category_id]]})
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
                        category_errors.append({'name':'CategoryNotFound', 
                                                'detail': f"{one_category} 未在被合并文件中找到",
                                                 'object': [one_category, main_file.dataset['categories']]})
            else:
                category_dict[one_category['id']] = one_category['id']
        else:
            # 考虑一种情况：main: category: {1:{'id':1, 'name': '蓝色已击打}}
            #            merge: category: {1: ... , 2:..., 3:{'id':3, 'name': '蓝色已击打}}
            # 由于main中没有id为3的类别，所以上面不会处理这种情况
            # 但这种情况下显然应该抛出一个CategoryRepeatError,所以在这里检查
            for one_category_id in main_file.cats:
                if main_file.cats[one_category_id]['name'] == one_category['name']:
                    # 有同名但不同id的类别，返回错误信息让上层函数处理
                    # 上层函数应当询问用户这俩类别是否相同
                    # 如果是，则将merge_file中的类别id改为main_file中的类别id
                    # 如果不是，新建一个类别，将merge_file中的类别id改为新建的类别id
                    category_errors.append({'name':'CategoryNameRepeat', 
                                                'detail': f'{one_category} 与 {main_file.cats[one_category_id]} 的名称重复',
                                                'object': [one_category, main_file.cats[one_category_id]]})
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
                        category_errors.append({'name':'CategoryNotFound', 
                                                'detail': f"{one_category} 未在被合并文件中找到",
                                                 'object': [one_category, main_file.dataset['categories']]})
    if len(category_errors) > 0:
        return category_errors

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
        image_ids = [image_data["id"] for image_data in output.dataset["images"]]
        image_id = max(image_ids) + 1
        image_id_table[image_data["id"]] = image_id
        image_data["id"] = image_id
        output.dataset["images"].append(image_data)

    # 合并annotations部分
    output.dataset['annotations'] = main_file.dataset['annotations']
    for annotation in merge_file.anns.values():
        annotations_ids = [annotation["id"] for annotation in output.dataset["annotations"]]
        annotation["id"] = max(annotations_ids) + 1
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


def console_main(config:Config=None):
    if DEFAULT_CONFIG.COCO_FILE_DIRECTORY is None and DEFAULT_CONFIG.COCO_FILE_PATH == [] and config is None:
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
    if DEFAULT_CONFIG.OUTPUT_PATH is None and config is None:
        config.OUTPUT_PATH = _ask_until_answers(lambda ans: os.path.isdir(os.path.dirname(ans)), "请输入输出文件路径: ")
    if config is None:
        config = DEFAULT_CONFIG
    
    config = config.parse()
    result = coco.COCO(config.COCO_FILE_PATH[0])
    for path in config.COCO_FILE_PATH[1:]:
        coco_file = coco.COCO(path)
        allow_category_merge = False

        while True:
            info = merge_two_coco_file(result, coco_file, allow_category_merge=allow_category_merge)
            if isinstance(info, list):
                for error_info in info:
                    if error_info['name'] == "CategoryNotFound":
                        print(f" {error_info['object'][0]} 这个标签没有在之前的文件中出现过。")
                        print(f"之前文件中存在的标签如下：{error_info['object'][1]}")
                        choice = _ask_until_answers(lambda ans: ans in ['0','1'],f"该标签是否与之前文件中的某个标签相同？(1/0): ")
                        if choice == '0':
                            choice2 = _ask_until_answers(lambda ans: ans in ['0','1'], f"是否将其作为新的标签添加至合并后的文件中(1/0): ")
                            if choice2 == '1':
                                allow_category_merge = True
                            else:
                                delete_category(coco_file, error_info['object'][0]['id'])
                        else:
                            print("这个标签与以下哪个标签相同？")
                            for one_annotation in result.cats.values():
                                print(f"{one_annotation['id']}: {one_annotation['name']}")
                            choice3 = _ask_until_answers(lambda ans: ans in [str(one_annotation['id']) for one_annotation in result.cats.values()], "请输入标签id: ")
                            for one in coco_file.dataset['categories']:
                                if one['id'] == int(choice3):
                                    one['name'] = error_info['object'][1][int(choice3)-1]['name']
                            change_category_id(coco_file, error_info['object'][0]['id'], int(choice3))
                    elif error_info['name'] == "CategoryNameRepeat":
                        print(f" {error_info['object'][0]} 这个标签在之前的文件中出现过，但id不同")
                        print(f"之前文件中存在的标签如下：{error_info['object'][1]}")
                        choice = _ask_until_answers(lambda ans: ans in ['0','1'],f"是否认为这两个标签是相同的？(1/0): ")
                        if choice == '1':
                            change_category_id(coco_file, error_info['object'][0]['id'], error_info['object'][1]['id'])
                        else:
                            choice = input(f"请为该标签 {error_info['object'][0]} 修改名称： ")
                            for cate in coco_file.dataset['categories']:
                                if cate['id'] == error_info['object'][0]['id']:
                                    cate['name'] = choice
                    allow_category_merge = True
            else:
                result = info
                break
        
        with open(config.OUTPUT_PATH, 'w') as f:
            json.dump(result.dataset, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    console_main()