import os
import ctypes
import sys


def list_files_recursive(directory):
    files_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            files_list.append(os.path.join(root, file))
    return files_list


# 如果是管理员权限，执行文件扫描操

USER_PROFILE_PATH = os.environ["userprofile"]
print(USER_PROFILE_PATH)
start_menu_path = os.path.join(USER_PROFILE_PATH, "AppData/Roaming/Microsoft/Windows/Start Menu/Programs")
path_2 = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs"
all_files = list_files_recursive(path_2)
for p2 in all_files:
    print(p2)

if __name__ == "__main__":
    pass
