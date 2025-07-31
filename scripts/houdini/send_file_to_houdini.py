
import os
import argparse

houdini_path = r"C:/Program Files/Side Effects Software/Houdini 20.5.370"
parser = argparse.ArgumentParser(description='Create a file node in Houdini')
parser.add_argument('--name', help='Name of the node to create')
parser.add_argument('--file', help='Path to the file')
args = parser.parse_args()


def enableHouModule():
    import sys, os
    if hasattr(sys, "setdlopenflags"):
        old_dlopen_flags = sys.getdlopenflags()
        sys.setdlopenflags(old_dlopen_flags | os.RTLD_GLOBAL)
    if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
        os.add_dll_directory(f"{houdini_path}/bin")

    try:
        import hou
    except ImportError:
        sys.path.append(f'{houdini_path}/houdini/python3.11libs')
        import hou
    finally:
        if hasattr(sys, "setdlopenflags"):
            sys.setdlopenflags(old_dlopen_flags)


os.environ['HOUDINI_SCRIPT_LICENSE'] = 'hescape'
enableHouModule()
import hrpyc
connection, hou = hrpyc.import_remote_module()

geo_node = hou.node('/obj/geo1')

existing_node = geo_node.node(args.name)
if existing_node:
    existing_node.destroy()

file_node = geo_node.createNode('file', args.name)
file_node.parm("file").set(args.file)
