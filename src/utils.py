SPRITEFRAME_SIZE = 128

def get_stylesheet_from_file(filename):
    with open(filename, 'r') as f:
        style = f.read()
    return style

def temp_path_shortener(pathstr):
    if '/' in pathstr:
        return "/".join(pathstr.split('/')[-2:])
    else:
        return "None"

if __name__ == '__main__':
    print("To run the actual application, Please type: \npython xmlpngUI.py\nor \npython3 xmlpngUI.py \ndepending on what works")