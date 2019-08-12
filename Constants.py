import os, sys
windowWidth = 400
windowHeight = 700


# Keycodes
left = 37
right = 39
up = 38
down = 40
space = 32

def resourcePath(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)