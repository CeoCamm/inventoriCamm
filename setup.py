from cx_Freeze import *
import os

files = [
    'static',
    'templates',
    'app.py',
    'EditProductWindow.py',
    'style.css',
    'conexion.py',
]

def get_files_in_paths(file_list, base_path='.'):
    paths = []
    for file in file_list:
        full_path = os.path.join(base_path, file)
        if os.path.isdir(full_path):
            paths.append((full_path, file))
        else:
            paths.append((full_path, os.path.basename(full_path)))
    return paths

setup(
    name="CAMM",
    version="1.0",
    description="ORGANIADOR DE STOKC RAPIDO Y SENSILLO",
    executables=[Executable("app_desktop.py", base=None)],
    options={
        'build_exe': {
            'include_files': get_files_in_paths(files),
        },
    }
)

