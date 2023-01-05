from PyQt5.QtWidgets import QMessageBox

SPRITEFRAME_SIZE = 128
imghashes = {} # dict[Int(hash) -> PIL.Image object]
spritesheet_split_cache = {} # dict[str(spritesheet_path) -> dict[ (x,y,w,h, clipped)-> int(hash) ] ]
g_settings = {
    "isclip": 1,
    "prefix_type": "charname",
    "custom_prefix": "",
    "must_use_prefix": 0
} # dict containing all settings (check settingswindow.py)

def get_stylesheet_from_file(filename):
    with open(filename, 'r') as f:
        style = f.read()
    return style

def temp_path_shortener(pathstr):
    if '/' in pathstr:
        return "/".join(pathstr.split('/')[-2:])
    else:
        return pathstr

def display_msg_box(parent, window_title="MessageBox", text="Text Here", icon=None):
    msgbox = QMessageBox(parent)
    msgbox.setWindowTitle(window_title)
    msgbox.setText(text)
    if not icon:
        msgbox.setIcon(QMessageBox.Information)
    else:
        msgbox.setIcon(icon)
    x = msgbox.exec_()
    print("[DEBUG] Exit status of msgbox: "+str(x))

def parse_value(val, exceptions=None, fallback=0, dtype=int):
    if exceptions is None:
        exceptions = dict()
    
    if val in exceptions.keys():
        return exceptions.get(val)
    else:
        try:
            return dtype(val)
        except Exception as e:
            print("Could not convert into required type")
            print(e)
            return fallback

def clean_filename(filename):
    replacers = {
        '\\': '_backslash_',
        '/': '_fwdslash_',
        ':': '_colon_',
        '*': '_asterisk_',
        '?': '_questionmark_',
        '"': '_quot_',
        '<': '_lt_',
        '>': '_gt_',
        '|': '_pipe_'
    }
    for ch, replch in replacers.items():
        filename = filename.replace(ch, replch)
    return filename

if __name__ == '__main__':
    print("To run the actual application, Please type: \npython xmlpngUI.py\nor \npython3 xmlpngUI.py \ndepending on what works")