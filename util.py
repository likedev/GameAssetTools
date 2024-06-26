import os
from PySide6.QtCore import Qt
import copy
from config import *
from PySide6.QtGui import QIcon, QPixmap
import subprocess


def open_file_or_dir_in_explorer(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            # 如果是目录，直接打开这个目录
            subprocess.run(['explorer', os.path.normpath(path)])
        else:
            # 如果是文件，打开文件所在目录并选中这个文件
            subprocess.run(['explorer', '/select,', os.path.normpath(path)])
        return True
    return False


def set_item_data(item, data):
    item.setData(Qt.ItemDataRole.UserRole, copy.deepcopy(data))


def get_item_data(item):
    return item.data(Qt.ItemDataRole.UserRole)


icon_cache = {}


def get_file_extension(filename):
    _, ext = os.path.splitext(filename)
    ext = ext.lower()  # 确保扩展名小写以匹配映射表
    return ext


def get_icon_by_fileinfo(file):
    file_path = file['path']

    svg_icon_set = ['txt', 'py', 'pdf', 'psd', 'folder', 'obj',
                    'fbx', 'blend', 'zpr', 'ztl', 'hip', 'zprg', 'zip', '7z', 'uproject']
    png_icon_set = ['abc']

    def get_ext_path(ext):
        ext = ext.lstrip('.')
        if not ext:
            return './assets/icon/folder.svg'
        if ext in svg_icon_set:
            return './assets/icon/' + ext + '.svg'
        if ext in png_icon_set:
            return './assets/icon/' + ext + '.png'
        return './assets/icon/default.svg'

    def get_folder_icon_path():
        for app_tag in ['pycharm', 'idea']:
            if app_tag in file['tags']:
                return LOCAL_APP[app_tag]['icon_path']
        return './assets/icon/folder.svg'

    path_name, ext = os.path.splitext(file_path)

    if file_path in icon_cache:
        return icon_cache[file_path]  # 如果已缓存，直接返回
    if os.path.isdir(file_path):
        icon_path = get_folder_icon_path()
    else:
        icon_path = get_ext_path(ext)
    icon = QIcon(icon_path)  # 创建 QIcon 对象
    icon_cache[file_path] = icon  # 缓存图标
    return icon


pic_types_ext = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tif', 'tiff', 'svg', 'webp']


def is_pic_by_ext(ext_p):
    for ext in pic_types_ext:
        if ext in ext_p.lower():
            return True
    return False
