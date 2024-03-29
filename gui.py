# 数据集管理脚本的图形化界面
# 源石虫和丘丘人都能学会

# 这个库比原生的tk好看1000000倍
from tkinter import Event, Frame, Misc
import customtkinter as ctk
from dataclasses import dataclass
import tkinter as tk
from tkinter.simpledialog import Dialog
import tkinter.filedialog
import tkinter.messagebox
import json
import os


@dataclass
class CocoFormat:
    # 图片所在的目录
    image_path:str
    # 标签文件路径
    coco_path:str


@dataclass
class YoloFormat:
    # 图片所在的目录
    image_path:str
    # 标签所在的目录
    yolo_path:str


class Configure:
    """
    配置类，用于存储数据集相关配置
    """
    def __init__(self, data_type:str, data):
        """
        data_type: 字符串，"coco"或"yolo"(不区分大小写，但最好小写)
        data: coco/yolo格式的数据储存类的一个对象
        """
        self.data_type = data_type
        if (not isinstance(data, CocoFormat)) and (not isinstance(data, YoloFormat)):
            raise ValueError(f"参数data必须是一个YoloFormat或CocoFormat对象，而不是{data}")
        self.data = data
    
    def save(self, config_name="main"):
        if self.data_type.lower() == 'coco':
            data = {"data_type": self.data_type, "image_path": self.data.image_path,
                    "coco_path": self.data.coco_path}
        else:
            data = {"data_type": self.data_type, "image_path": self.data.image_path,
                    "yolo_path": self.data.yolo_path}
        with open(f"gui_config/{config_name}.json", "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    @classmethod
    def load(cls, config_name="main"):
        with open(f"gui_config/{config_name}.json", "r") as f:
            data = json.load(f)
        if data["data_type"].lower() == 'coco':
            return cls(data["data_type"], CocoFormat(data["image_path"], data["coco_path"]))
        else:
            return cls(data["data_type"], YoloFormat(data["image_path"], data["yolo_path"]))
    
    def __repr__(self) -> str:
        if self.data_type == 'yolo':
            return f"{self.__class__.__name__}({self.data_type}, YoloFormat({self.data.image_path}, {self.data.yolo_path}))"
        else:
            return f"{self.__class__.__name__}({self.data_type}, CocoFormat({self.data.image_path}, {self.data.coco_path}))"
        

class DialogCTk(Dialog):
    """
    仅仅重写了buttonbox方法：
        用CTk.CTkbutton替换了Dialog.buttonbox中的按钮，并把按钮的文字汉化了
    """
    def buttonbox(self) -> None:
        box = tk.Frame(self)

        w = ctk.CTkButton(box, text="确认", width=10, command=self.ok)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ctk.CTkButton(box, text="取消", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()


class AddConfigure(DialogCTk):
    def body(self, master: Frame) -> Misc | None:
        self.title("添加新的配置")
        path_frame = ctk.CTkFrame(master)
        self.large_path = ctk.StringVar()

        self.dataset_type = ""
        self.images_path = ""
        self.labels_path = ""
        self.coco_path = ""

        ctk.CTkLabel(master, text="数据集上层文件夹的路径: ").pack()
        ctk.CTkEntry(path_frame, textvariable=self.large_path, width=200, state=tk.DISABLED).grid(row=0, column=0, columnspan=2)
        ctk.CTkButton(path_frame, text="浏览", command=self.browse_large_path).grid(row=0, column=2)
        self.error_label = ctk.CTkLabel(master, font=("微软雅黑", 15), text_color="red", text='')
        path_frame.pack()

        self.select_frame = ctk.CTkFrame(master)
        ctk.CTkLabel(self.select_frame, text='请在以下选项中选择数据集的coco文件').pack()
        self.coco_select_list = tk.Listbox(self.select_frame, selectmode=tk.SINGLE)
        self.coco_select_list.pack(side='left')
        scrollbar = ctk.CTkScrollbar(self.select_frame, command=self.coco_select_list.yview)
        self.coco_select_list.configure(yscrollcommand = scrollbar.set)
        scrollbar.pack(side='right')
        self.select_coco_name_label = ctk.CTkLabel(self.select_frame, text="")
        ctk.CTkButton(self.select_frame, text="确认选择", command=self.confirm_coco_path).pack(side=tk.BOTTOM)
        self.select_coco_name_label.pack(side=tk.BOTTOM)
        self.error_label.pack() 
    
    def browse_large_path(self):
        directory = tkinter.filedialog.askdirectory(mustexist=True, initialdir=self.large_path.get() if self.large_path.get() != "" else None)
        self.large_path.set(directory)
        self.coco_select_list.delete(0, tk.END)
        self.images_path = ''
        self.coco_path = ''
        self.labels_path = ''
        self.dataset_type = ''
        if directory != "" and len(self.find_coco_in_dir(directory)) < 2:
            self.select_frame.pack_forget()
        if self.validate_dir():
            self.update_dir_info()
    
    def update_dir_info(self):
        directory = self.large_path.get()
        if os.path.isdir(os.path.join(directory, "labels")) and self.is_coco_file(directory):
            choice = tkinter.messagebox.askyesno("两种数据集格式", "该目录下同时存在labels文件夹与coco格式文件。是否认为其是yolo格式？\n"
                                                 "是-认为其是yolo数据集  否-认为其是coco数据集")
            if choice:
                self.dataset_type = 'yolo'
                self.labels_path = os.path.join(directory, "labels")
            else:
                self.dataset_type = 'coco'
                coco_paths = self.find_coco_in_dir(directory)
                if len(coco_paths) == 1:
                    self.coco_path = coco_paths[0]
                else:
                    for one in coco_paths:
                        self.coco_select_list.insert(tk.END, one)
                    self.select_frame.pack(before=self.error_label)
        elif os.path.exists(os.path.join(directory, 'labels')):
            self.dataset_type = 'yolo'
            self.labels_path = os.path.join(directory, 'labels')
        elif self.is_coco_file(directory):
            self.dataset_type = 'coco'
            coco_paths = self.find_coco_in_dir(directory)
            if len(coco_paths) == 1:
                self.coco_path = coco_paths[0]
            else:
                for one in coco_paths:
                    self.coco_select_list.insert(tk.END, one)
                self.select_frame.pack(before=self.error_label)

        if os.path.isdir(os.path.join(directory, "images")):
            self.images_path = os.path.join(directory, 'images')

    def confirm_coco_path(self):
        coco_path = self.coco_select_list.get(tk.ACTIVE)
        self.select_coco_name_label.configure(text="目前选择"+coco_path)
        self.coco_path = os.path.join(self.large_path.get(), coco_path)

    def validate_dir(self) -> bool:
        if self.large_path.get() == "":
            self.error_label.configure(text="路径不能为空")
            return False
        if not os.path.exists(self.large_path.get()):
            self.error_label.configure(text="选择的路径不存在")
            return False
        if not (os.path.isdir(os.path.join(self.large_path.get(),'images')) or
                os.path.isdir(os.path.join(self.large_path.get(),'image')) or
                os.path.isdir(os.path.join(self.large_path.get(),'labels')) or
                os.path.isdir(os.path.join(self.large_path.get(),'label')) or
                self.is_coco_file(self.large_path.get())):
            self.error_label.configure(text="路径下没有images或labels文件夹，也不存在coco文件")
            return False
        self.error_label.configure(text='')
        return True

    def validate(self) -> bool:
        if not self.validate_dir():
            return False
        if len(self.coco_select_list.get(0)) and self.coco_path == '':
            self.error_label.configure(text="请在上方列表中指定coco数据集，并点击“确认选择”")
        if self.coco_path and self.images_path or self.labels_path and self.images_path:
            print("good")
            return True
        return False

    def apply(self):
        pass
    
    @staticmethod
    def is_coco_file(dir):
        paths = os.listdir(dir)
        is_coco = False
        for path in paths:
            if path.endswith(".json"):
                try:
                    with open(os.path.join(dir, path), "r") as f:
                        d:dict = json.load(f)
                except (json.JSONDecodeError, OSError):
                    pass
                else:
                    if isinstance(d, dict):
                        if d.get("categories", 0) and d.get("annotations", 0) and d.get("images", 0):
                            is_coco = True
        return is_coco
    
    @staticmethod
    def find_coco_in_dir(dir):
        paths = os.listdir(dir)
        coco_paths = []
        for path in paths:
            if path.endswith(".json"):
                try:
                    with open(os.path.join(dir, path), "r") as f:
                        d:dict = json.load(f)
                except (json.JSONDecodeError, OSError):
                    pass
                else:
                    if isinstance(d, dict):
                        if d.get("categories", 0) and d.get("annotations", 0) and d.get("images", 0):
                            coco_paths.append(path)
        return coco_paths


class MainApp(ctk.CTk):
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)
        self.title("数据集管理工具")


        ctk.CTkButton(self, text='添加配置', command=self.add_configure).pack()
        exist_config = False
        for one_file in os.listdir("gui_config"):
            if one_file.endswith(".json"):
                exist_config = True
                break
        if not exist_config:
            self.add_configure()
    
    def add_configure(self):
        add_configure = AddConfigure(self)
        if add_configure.coco_path and add_configure.images_path or add_configure.labels_path and add_configure.images_path:
            if add_configure.dataset_type == 'yolo':
                config = Configure('yolo', YoloFormat(add_configure.images_path,
                                                    add_configure.labels_path))
            else:
                config = Configure('coco', CocoFormat(add_configure.images_path,
                                                    add_configure.coco_path))
            print(config)


if __name__ == '__main__':
    app = MainApp()
    app.mainloop()