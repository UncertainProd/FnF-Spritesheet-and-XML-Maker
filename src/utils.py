SPRITEFRAME_SIZE = 130
is_dark_mode = False

def get_stylesheet_from_file(filename):
    with open(filename, 'r') as f:
        style = f.read()
    return style

if __name__ == '__main__':
    print("To run the actual application, Please type: \npython xmlpngUI.py\nor \npython3 xmlpngUI.py \ndepending on what works")