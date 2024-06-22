import os

import win32com
import win32gui
from PySide6.QtCore import Qt
import copy

from PySide6.QtGui import QIcon, QPixmap
import win32api
from win32con import LR_DEFAULTSIZE, LR_LOADFROMFILE
import win32ui


def set_item_data(item, data):
    item.setData(Qt.ItemDataRole.UserRole, copy.deepcopy(data))


def get_item_data(item):
    return item.data(Qt.ItemDataRole.UserRole)


icon_cache = {}


def get_file_extension(filename):
    _, ext = os.path.splitext(filename)
    ext = ext.lower()  # 确保扩展名小写以匹配映射表
    return ext


def get_icon_by_extension(file_path):
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

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()  # 确保扩展名小写以匹配映射表
    if ext in icon_cache:
        return icon_cache[ext]  # 如果已缓存，直接返回
    if os.path.isdir(file_path):
        icon_path = './assets/icon/folder.svg'
    else:
        icon_path = get_ext_path(ext)
    icon = QIcon(icon_path)  # 创建 QIcon 对象
    icon_cache[ext] = icon  # 缓存图标
    return icon
