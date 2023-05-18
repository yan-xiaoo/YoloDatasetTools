import json


MAIN_FILE_NAME = r"C:\Users\liyan\Downloads\QQ_Receive\final.json"
MERGE_FILE_NAME = r"C:\Users\liyan\Downloads\QQ_Receive\train400_end(1).json"
OUTPUT_FILE_NAME = r"C:\Users\liyan\Downloads\QQ_Receive\merged_new.json"


def load(file_name:str):
    with open(file_name, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    main_json = load(MAIN_FILE_NAME)
    merge_json = load(MERGE_FILE_NAME)

    total_id = 0;
    exist_images = []
    image_id_table = {}
    main_imageid_to_filename = {}
    merge_imageid_to_filename = {}

    for one_image in main_json['images']:
        exist_images.append(one_image['file_name'])
        main_imageid_to_filename[one_image['id']] = one_image['file_name']
        total_id+=1

    for one_image in merge_json['images']:
        merge_imageid_to_filename[one_image['id']] = one_image['file_name']
        if one_image['file_name'] not in exist_images:
            total_id+=1
            image_id_table[one_image['id']] = total_id
            one_image['id'] = total_id
            main_json['images'].append(one_image)

    annotation_id = len(main_json['annotations'])
    append_annotations = []
    for one in merge_json['annotations']:
        # 防止重复
        # 因为main_json与merge_json中可能包含对同一张图片`的标注，所以要防止标签被添加两次
        flag = True
        for one_annotation in main_json['annotations']:
            if one_annotation['image_id'] == one['image_id'] and one_annotation['segmentation'] == one['segmentation']:
                flag = False
                break
            # 如果one和one_annotation标注的是同一张图片
            # 那就只留下one_annotation，因为one_annotation是main_json中的标注
            try:
                merge_annotation_filename = merge_imageid_to_filename[one['image_id']]
            except KeyError:
                merge_annotation_filename = merge_imageid_to_filename[image_id_table[one['image_id']]]


            if main_imageid_to_filename[one_annotation['image_id']] == merge_annotation_filename:
                flag = False
                break
        if flag:
            annotation_id+=1
            one['id'] = annotation_id
            # 更改标签对应的image_id，否则会出现标签和图片不匹配的问题
            one['image_id'] = image_id_table[one['image_id']]
            append_annotations.append(one)
    
    main_json['annotations'].extend(append_annotations)
    
    with open(OUTPUT_FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(main_json, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()