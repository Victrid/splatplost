import glob
import os


def get_ui_files():
    data = []
    for ui in glob.glob(os.path.join(os.path.dirname(__file__), "..", "gui", "*.ui")):
        data.append((ui, "splatplost"))
    return data


def get_language_files():
    data = []
    for lang in glob.glob(os.path.join(os.path.dirname(__file__), "..", "gui", "i18n", "*.qm")):
        data.append((lang, "splatplost"))
    return data


datas = get_ui_files()
datas += get_language_files()
