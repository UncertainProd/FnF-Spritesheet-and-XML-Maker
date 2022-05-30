import xml.etree.ElementTree as ET
from engine.imgutils import pad_img
from utils import spritesheet_split_cache
from spriteframe import SpriteFrame
from PIL import Image

def get_true_frame(img , framex, framey, framew, frameh, flipx=False, flipy=False):
    # if framex < 0, we pad, else we crop
    final_frame = img
    if framex < 0:
        final_frame = pad_img(final_frame, False, 0, 0, 0, -framex)
    else:
        final_frame = final_frame.crop((framex, 0, final_frame.width, final_frame.height))
    
    # same for framey
    if framey < 0:
        final_frame = pad_img(final_frame, False, -framey, 0, 0, 0)
    else:
        final_frame = final_frame.crop((0, framey, final_frame.width, final_frame.height))
    
    # if framex + framew > img.width, we pad else we crop
    if framex + framew > img.width:
        final_frame = pad_img(final_frame, False, 0, framex+framew - img.width, 0, 0)
    else:
        final_frame = final_frame.crop((0, 0, framew, final_frame.height))
    
    # same for framey + frameh > img.height
    if framey + frameh > img.height:
        final_frame = pad_img(final_frame, False, 0, 0, framey + frameh - img.height, 0)
    else:
        final_frame = final_frame.crop((0, 0, final_frame.width, frameh))

    return final_frame

def add_pose_numbers(frame_arr):
    pose_arr = [ frame.data.pose_name for frame in frame_arr ]
    unique_poses = list(set(pose_arr))
    pose_counts = dict([ (ele, 0) for ele in unique_poses ])
    new_pose_arr = list(pose_arr)
    for i in range(len(new_pose_arr)):
        pose_counts[new_pose_arr[i]] += 1
        new_pose_arr[i] = new_pose_arr[i] + str(pose_counts[new_pose_arr[i]] - 1).zfill(4)
    return new_pose_arr


def split_spsh(pngpath, xmlpath, udpdatefn):
    # spritesheet = Image.open(pngpath)
    try:
        cleaned_xml = ""
        quotepairity = 0
        with open(xmlpath, 'r', encoding='utf-8') as f:
            ch = f.read(1)
            while ch and ch != '<':
                ch = f.read(1)
            cleaned_xml += ch
            while True:
                ch = f.read(1)
                if ch == '"':
                    quotepairity = 1 - quotepairity
                elif (ch == '<' or ch == '>') and quotepairity == 1:
                    ch = '&lt;' if ch == '<' else '&gt;'
                else:
                    if not ch:
                        break
                cleaned_xml += ch

        xmltree = ET.fromstring(cleaned_xml) # ET.parse(xmlpath)
        print("XML cleaned")
    except ET.ParseError as e:
        print("Error!", str(e))
        return []
    sprites = []

    root = xmltree # .getroot()
    subtextures = root.findall("SubTexture")
    # get_true_val = lambda val: int(val) if val else None

    # initialize cache for this spritesheet
    if not spritesheet_split_cache.get(pngpath):
        spritesheet_split_cache[pngpath] = {}
    
    # debug: current cache
    print("Current cache:\n", spritesheet_split_cache)

    for i, subtex in enumerate(subtextures):
        tex_x = int(subtex.attrib['x'])
        tex_y = int(subtex.attrib['y'])
        tex_width = int(subtex.attrib['width'])
        tex_height = int(subtex.attrib['height'])
        pose_name = subtex.attrib['name']
        fx = int(subtex.attrib.get("frameX", 0))
        fy = int(subtex.attrib.get("frameY", 0))
        fw = int(subtex.attrib.get("frameWidth", tex_width))
        fh = int(subtex.attrib.get("frameHeight", tex_height))
        # sprite_img = spritesheet.crop((tex_x, tex_y, tex_x+tex_width, tex_y+tex_height)).convert('RGBA')
        # sprite_img = sprite_img.convert('RGBA')
        # qim = ImageQt(sprite_img)
        # sprites.append((sprite_img.toqpixmap(), pose_name, tex_x, tex_y, tex_width, tex_height))
        sprites.append(
            SpriteFrame(
                None, pngpath, False, pose_name, 
                tx=tex_x, ty=tex_y, tw=tex_width, th=tex_height,
                framex=fx, framey=fy, framew=fw, frameh=fh
            )
        )
        udpdatefn((i+1)*50//len(subtextures), pose_name)
    
    return sprites

def get_gif_frames(gifpath, updatefn=None):
    sprites = []
    with Image.open(gifpath) as gif:
        for i in range(gif.n_frames):
            gif.seek(i)
            gif.save("_tmp.png")
            sprites.append(SpriteFrame(None, "_tmp.png", True))
            if updatefn is not None:
                updatefn((i+1)*50//gif.n_frames, f"Adding Frame-{i+1}")
    
    return sprites
            