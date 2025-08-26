import os
import shutil

def clean_temp_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
