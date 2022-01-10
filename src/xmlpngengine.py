import xml.etree.ElementTree as ET
from PIL import Image, ImageChops
from os import path, linesep

from spriteframe import SpriteFrame
from utils import imghashes, g_settings, spritesheet_split_cache

# Packing Algorithm based on https://github.com/jakesgordon/bin-packing/blob/master/js/packer.growing.js
# converted to python
# By (Jake Gordon)[https://github.com/jakesgordon]
class GrowingPacker:
    def __init__(self):
        self.root = None

    def fit(self, blocks):
        num_blocks = len(blocks)
        w = blocks[0].get("w", 0) if num_blocks > 0 else 0
        h = blocks[0].get("h", 0) if num_blocks > 0 else 0
        self.root = { "x":0, "y":0, "w":w, "h":h }
        for block in blocks:
            node = self.find_node(self.root, block.get("w", 0), block.get("h", 0))
            if node:
                block["fit"] = self.split_node(node, block.get("w", 0), block.get("h", 0))
            else:
                block["fit"] = self.grow_node(block.get("w", 0), block.get("h", 0))
    
    def find_node(self, root, w, h):
        if root.get("used"):
            return self.find_node(root.get("right"), w, h) or self.find_node(root.get("down"), w, h)
        elif w <= root.get("w", 0) and h <= root.get("h", 0):
            return root
        else:
            return None
    
    def split_node(self, node, w, h):
        node["used"] = True
        node['down'] = { "x": node.get("x"), "y": node.get("y") + h, "w": node.get("w"), "h":node.get("h") - h }
        node['right'] = { "x": node.get("x") + w, "y": node.get("y"), "w": node.get("w") - w, "h": h }
        return node
    
    def grow_node(self, w, h):
        canGrowDown = (w <= self.root.get("w"))
        canGrowRight = (h <= self.root.get("h"))

        shouldGrowRight = canGrowRight and (self.root.get("h") >= (self.root.get("w") + w))
        shouldGrowDown = canGrowDown and (self.root.get("w") >= (self.root.get("h") + h))

        if shouldGrowRight:
            return self.grow_right(w, h)
        elif shouldGrowDown:
            return self.grow_down(w, h)
        elif canGrowRight:
            return self.grow_right(w, h)
        elif canGrowDown:
            return self.grow_down(w, h)
        else:
            return None
    
    def grow_right(self, w, h):
        self.root = {
            "used": True, 
            "x":0, 
            "y":0, 
            "w":self.root.get("w")+w,
            "h":self.root.get("h"),
            "down":self.root,
            "right": { "x": self.root.get("w"), "y":0, "w":w, "h":self.root.get("h") }
        }
        node = self.find_node(self.root, w, h)
        if node:
            return self.split_node(node, w, h)
        else:
            return None

    def grow_down(self, w, h):
        self.root = {
            "used": True, 
            "x":0, 
            "y":0, 
            "w":self.root.get("w"),
            "h":self.root.get("h") + h,
            "down": { "x": 0, "y": self.root.get("h"), "w": self.root.get("w"), "h": h },
            "right": self.root
        }
        node = self.find_node(self.root, w, h)
        if node:
            return self.split_node(node, w, h)
        else:
            return None

DEFAULT_PADDING = 1

def fast_image_cmp(im1, im2): # im1 == im2 ?
    if im1.size != im2.size:
        return False
    if im1.tobytes() != im2.tobytes():
        return False
    
    return ImageChops.difference(im1, im2).getbbox() is None

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

def pad_img(img, clip=False, top=DEFAULT_PADDING, right=DEFAULT_PADDING, bottom=DEFAULT_PADDING, left=DEFAULT_PADDING):
    if clip:
        img = img.crop(img.getbbox())
    
    width, height = img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
    result.paste(img, (left, top))
    return result

def add_pose_numbers(frame_arr):
    pose_arr = [ frame.data.pose_name for frame in frame_arr ]
    unique_poses = list(set(pose_arr))
    pose_counts = dict([ (ele, 0) for ele in unique_poses ])
    new_pose_arr = list(pose_arr)
    for i in range(len(new_pose_arr)):
        pose_counts[new_pose_arr[i]] += 1
        new_pose_arr[i] = new_pose_arr[i] + str(pose_counts[new_pose_arr[i]] - 1).zfill(4)
    return new_pose_arr

def make_png_xml(frames, save_dir, character_name="Result", progressupdatefn=None, settings=None):
    if settings is None:
        settings = g_settings
    prefix_type = settings.get('prefix_type', 'charname') # use character name or use a custom prefix instead
    custom_prefix = settings.get('custom_prefix', '') # the custom prefix to use
    must_use_prefix = settings.get('must_use_prefix', 0) != 0 # use the custom prefix even if frame is from existing spritesheet
    # print(len(imghashes))
    # print(len(frames))

    try:
        # init XML
        root = ET.Element("TextureAtlas")
        root.tail = linesep
        root.attrib['imagePath'] = f"{character_name}.png"
        
        new_pose_names = add_pose_numbers(frames)
        for f, pose in zip(frames, new_pose_names):
            final_pose_name = pose
            if f.data.from_single_png or (not f.data.from_single_png and f.modified):
                if prefix_type == 'charname':
                    final_pose_name = f"{character_name} {final_pose_name}"
                else:
                    final_pose_name = f"{custom_prefix} {final_pose_name}"
            else:
                if must_use_prefix and prefix_type == 'custom':
                    final_pose_name = f"{custom_prefix} {final_pose_name}"
            
            f.data.xml_pose_name = final_pose_name
        
        frame_dict_arr = []
        current_img_hashes = set([x.data.img_hash for x in frames])
        for imhash, img in imghashes.items():
            if imhash in current_img_hashes:
                frame_dict_arr.append({
                    "id": imhash,
                    "w": img.width,
                    "h": img.height
                })
        frame_dict_arr.sort(key= lambda rect: rect.get("h", -100), reverse=True)
        
        gp = GrowingPacker()
        gp.fit(frame_dict_arr)
        
        final_img = Image.new("RGBA", (gp.root['w'], gp.root['h']), (0, 0, 0, 0))
        # frame_dict_arr.sort(key=lambda x: x['id'].img_xml_data.xml_posename)
        prgs = 0
        for r in frame_dict_arr:
            fit = r.get("fit")
            final_img.paste( imghashes.get(r['id']), (fit["x"], fit["y"]) )
            prgs += 1
            progressupdatefn(prgs, "Adding images to spritesheet...")

        # convert frame_dict_arr into a dict[image_hash -> position in spritesheet]:
        imghash_dict = { rect['id']: (rect['fit']['x'], rect['fit']['y']) for rect in frame_dict_arr }
        for frame in frames:
            subtexture_element = ET.Element("SubTexture")
            subtexture_element.tail = linesep
            w, h = imghashes.get(frame.data.img_hash).size
            subtexture_element.attrib = {
                "name" : frame.data.xml_pose_name,
                "x": str(imghash_dict[frame.data.img_hash][0]),
                "y": str(imghash_dict[frame.data.img_hash][1]),
                "width": str(w),
                "height": str(h),
                "frameX": str(frame.data.framex),
                "frameY": str(frame.data.framey),
                "frameWidth": str(frame.data.framew),
                "frameHeight": str(frame.data.frameh),
            }
            root.append(subtexture_element)
            prgs += 1
            progressupdatefn(prgs, f"Saving {frame.data.xml_pose_name} to XML...")
            # im.close()
        print("Saving XML...")
        xmltree = ET.ElementTree(root)
        with open(path.join(save_dir, character_name) + ".xml", 'wb') as f:
            xmltree.write(f, xml_declaration=True, encoding='utf-8')
        
        print("Saving Image...")
        final_img = final_img.crop(final_img.getbbox())
        final_img.save(path.join(save_dir, character_name) + ".png")
        final_img.close()
        
        print("Done!")
    except Exception as e:
        return -1, str(e)
    
    return 0, None

def clean_up(*args):
    for img in args:
        img.close()

def appendIconToIconGrid(icongrid_path, iconpaths, iconsize=150): # savedir,
    ''' 
        Adds the selected Icon into the icon grid. Returns a value based on if it was successful or not, as follows:
        0 : Successful addition!
        1 : Icon grid (possibly) too full
        2 : Icon is too big to fit neatly into the icon grid
        3 : An Error occured in finding the right row to insert (It is possible that the icon grid wasn't transparent)
        4 : Icon image was too small for the icon space (This is a warning not an error, as the app will center the image if this happens)
    '''
    print("Icongrid from: {} \nIcons: {}".format(icongrid_path, len(iconpaths)))
    retval = 0
    problem_img = None
    indices = []
    exception_msg = None
    for iconpath in iconpaths:
        icongrid = Image.open(icongrid_path).convert('RGBA')
        grid_w, grid_h = icongrid.size
        max_col = grid_w // iconsize
        max_row = grid_h // iconsize
        iconimg = Image.open(iconpath)
        new_index = None

        # Icongrid manipulation code
        lastrow_y = icongrid.getbbox()[-1] # lower bound of the bbox is on the last row
        if lastrow_y >= icongrid.height:
            clean_up(icongrid, iconimg)
            return 1, new_index, None, exception_msg # 1, None, None, None
        row_index = lastrow_y // iconsize

        last_row_img = icongrid.crop((0, row_index*iconsize, icongrid.width, row_index*iconsize + iconsize))
        box = last_row_img.getbbox()
        last_row_img.close()

        if box:
            lastrow_x = box[2]
            col_index = lastrow_x // iconsize

            if row_index >= max_row - 1 and col_index >= max_col - 1:
                return 1, new_index, None, exception_msg

            new_index = row_index*10 + col_index + 1

            newrow_index = new_index // 10
            newcol_index = new_index % 10
            print("New pic to put at index={}: row={}, col={}".format(new_index, newrow_index, newcol_index))
            imgy, imgx = newrow_index*iconsize, newcol_index*iconsize
            print("Coords to put new pic: row={} col={}".format(imgy, imgx))
            
            print("Pasting new img.....")
            # icongrid = icongrid.copy()
            # last ditch try catch block
            try:
                # icon size check
                w, h = iconimg.size
                if w > iconsize or h > iconsize:
                    clean_up(icongrid, iconimg)
                    problem_img = iconpath
                    return 2, new_index, problem_img, exception_msg # 2, None, iconpath
                if w != iconsize and h != iconsize:
                    print("Bad icon size....")
                    # we will try to center the smaller image into the grid space
                    dx = (iconsize//2) - (w//2)
                    dy = (iconsize//2) - (h//2)
                    imgx += dx
                    imgy += dy
                    iconimg = iconimg.convert('RGBA')
                    icongrid.paste(iconimg, (imgx, imgy, imgx+w, imgy+h))
                    # icongrid.save(os.path.join(savedir, "Result-icongrid.png"))
                    icongrid.save(icongrid_path)
                    clean_up(icongrid, iconimg)
                    retval = 4
                    problem_img = iconpath
                    indices.append(new_index)
                    # return 4, new_index, problem_img
                else:
                    iconimg = iconimg.convert('RGBA')
                    icongrid.paste(iconimg, (imgx, imgy, imgx+iconsize, imgy+iconsize))
                    indices.append(new_index)
                    # new_icongrid.save(os.path.join(savedir, "Result-icongrid.png"))
                    icongrid.save(icongrid_path)
                print("Done!")
            except Exception as e:
                print("Problem at try except block!")
                problem_img = iconpath
                exception_msg = str(e)
                return 1, indices, problem_img, exception_msg # 1, [...], iconpath

        else:
            print("Something's sus!")
            problem_img = iconpath
            return 3, indices, problem_img, exception_msg

        iconimg.close()
        icongrid.close()
    return retval, indices, problem_img, exception_msg

def save_img_sequence(frames, savedir, updatefn):
    # Saves each frame as a png
    newposes = add_pose_numbers(frames)
    for i, (frame, pose) in enumerate(zip(frames, newposes)):
        try:
            im = imghashes.get(frame.data.img_hash)
            im = get_true_frame(im, frame.data.framex, frame.data.framey, frame.data.framew, frame.data.frameh)

            im.save(path.join(savedir, f"{pose}.png"))
            im.close()
            updatefn(i+1, f"Saving: {pose}.png")
        except Exception as e:
            return str(e)
    return None

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
        

if __name__ == '__main__':
    print("This program is just the engine! To run the actual application, Please type: \npython xmlpngUI.py\nor \npython3 xmlpngUI.py \ndepending on what works")