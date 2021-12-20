from PyQt5.QtWidgets import QMessageBox
from PIL import Image

SPRITEFRAME_SIZE = 128
imghashes:dict[int, Image.Image] = {} # dict[Int(hash) -> PIL.Image object]

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


# def get_true_frame(img , framex, framey, framew, frameh):
#     # if framex < 0, we pad, else we crop
#     final_frame = img
#     if framex < 0:
#         final_frame = pad_img(final_frame, False, 0, 0, 0, -framex)
#     else:
#         final_frame = final_frame.crop((framex, 0, final_frame.width, final_frame.height))
    
#     # same for framey
#     if framey < 0:
#         final_frame = pad_img(final_frame, False, -framey, 0, 0, 0)
#     else:
#         final_frame = final_frame.crop((0, framey, final_frame.width, final_frame.height))
    
#     # if framex + framew > img.width, we pad else we crop
#     if framex + framew > img.width:
#         final_frame = pad_img(final_frame, False, 0, framex+framew - img.width, 0, 0)
#     else:
#         final_frame = final_frame.crop((0, 0, framex+framew, final_frame.height))
    
#     # same for framey + frameh > img.height
#     if framey + frameh > img.height:
#         final_frame = pad_img(final_frame, False, 0, 0, framey + frameh - img.height, 0)
#     else:
#         final_frame = final_frame.crop((0, 0, final_frame.width, framey+frameh))
    
#     return final_frame

if __name__ == '__main__':
    print("To run the actual application, Please type: \npython xmlpngUI.py\nor \npython3 xmlpngUI.py \ndepending on what works")