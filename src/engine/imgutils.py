from PIL import Image

DEFAULT_PADDING = 1

def pad_img(img, clip=False, top=DEFAULT_PADDING, right=DEFAULT_PADDING, bottom=DEFAULT_PADDING, left=DEFAULT_PADDING):
    if clip:
        img = img.crop(img.getbbox())
    
    width, height = img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
    result.paste(img, (left, top))
    return result

def clean_up(*args):
    for img in args:
        img.close()