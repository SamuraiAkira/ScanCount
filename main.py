import os
import sys
import eel
import tkinter as tk
from processor import ProductProcessor
from utils import get_project_path

processor = ProductProcessor()

eel.init('web')

@eel.expose
def process_data(data):
    result_text, logs = processor.process_data(data)
    return {'result': result_text, 'logs': logs}

def get_screen_center(width, height):
    root = tk.Tk()
    root.withdraw()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    return x, y

def start_app():
    width = 800
    height = 850
    x, y = get_screen_center(width, height)
    
    try:
        if getattr(sys, 'frozen', False):
            eel.start('interface.html', size=(width, height), position=(x, y), port=0)
        else:
            eel.start('interface.html', size=(width, height), position=(x, y), port=0, mode='chrome')
    except Exception:
        eel.start('interface.html', size=(width, height), position=(x, y), port=0, mode='default')

if __name__ == '__main__':
    start_app()