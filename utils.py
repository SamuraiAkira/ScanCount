import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_project_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def save_result_to_file(result_text):
    output_path = os.path.join(get_project_path(), "output.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result_text)
    return output_path