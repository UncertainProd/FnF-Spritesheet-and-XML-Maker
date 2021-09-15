import xml.etree.ElementTree as ET
from PIL import Image, ImageChops
from PIL.ImageQt import ImageQt
from math import sqrt
from os import path, linesep

def fast_image_cmp(im1, im2): # im1 == im2 ?
    if im1.size != im2.size:
        return False
    if im1.tobytes() != im2.tobytes():
        return False
    
    return ImageChops.difference(im1, im2).getbbox() is None

def pad_img(img, clip=False, top=2, right=2, bottom=2, left=2):
    if clip:
        img = img.crop(img.getbbox())
    
    width, height = img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
    result.paste(img, (left, top))
    return result

def add_pose_numbers(frame_arr):
    pose_arr = [ frame.pose_name for frame in frame_arr ]
    unique_poses = list(set(pose_arr))
    pose_counts = dict([ (ele, 0) for ele in unique_poses ])
    new_pose_arr = list(pose_arr)
    for i in range(len(new_pose_arr)):
        pose_counts[new_pose_arr[i]] += 1
        new_pose_arr[i] = new_pose_arr[i] + str(pose_counts[new_pose_arr[i]] - 1).zfill(4)
    return new_pose_arr

def group_imgs(frames, newposes):
    num_imgs = 0
    existing_spsh_frames = [ (sframe, newpose) for sframe, newpose in zip(frames, newposes) if not sframe.from_single_png ]
    imdict = {} # { "existingspsh.png": { (x, y, w, h):[(pose, frameinfo, modified), ...], ... }, ... }
    for f, npose in existing_spsh_frames:
        if imdict.get(f.imgpath):
            coord_dict = imdict[f.imgpath]
            crds = (f.tex_x, f.tex_y, f.tex_w, f.tex_h)
            if coord_dict.get(crds):
                imdict[f.imgpath][crds].append((npose, (f.framex, f.framey, f.framew, f.frameh), f.modified))
            else:
                imdict[f.imgpath][crds] = [(npose, (f.framex, f.framey, f.framew, f.frameh), f.modified)]
                num_imgs += 1
        else:
            crds = (f.tex_x, f.tex_y, f.tex_w, f.tex_h)
            imdict[f.imgpath] = { crds:[ (npose, (f.framex, f.framey, f.framew, f.frameh), f.modified) ] }
            num_imgs += 1
    # print(imdict)
    single_img_frames = [ (fr, np) for fr, np in zip(frames, newposes) if fr.from_single_png ]
    return imdict, single_img_frames

def get_tot_imgs_from_imdict(imdict, reuse):
    tot = 0
    if reuse >= 1:
        for coord_dict in imdict.values():
            tot += len(coord_dict.keys())
    else:
        for coord_dict in imdict.values():
            for poselist in coord_dict.values():
                tot += len(poselist)
    return tot

def calculate_final_size(imdict, imlist, num_cols, clip, reuse):
    # PNG stuff
    widths = []
    heights = []
    exceptionmsg = None
    for frame, _ in imlist:
        try:
            im = Image.open(frame.imgpath)
        except Exception as e:
            exceptionmsg = str(e)
            print("Error: ", exceptionmsg)
            return 1, exceptionmsg
        else:
            if not clip:
                widths.append(im.width + 4) # 2 pixels padding on each side
                heights.append(im.height + 4)
            else:
                box = im.getbbox()
                widths.append(box[2] - box[0] + 4)
                heights.append(box[3] - box[1] + 4)
            im.close()
    
    for impath, coords_dict in imdict.items():
        spsh = Image.open(impath)
        for (x, y, w, h), poselist in coords_dict.items():
            if reuse >= 1:
                if not clip:
                    widths.append(w + 4)
                    heights.append(h + 4)
                else:
                    box = spsh.crop((x, y, x+w, y+h)).getbbox()
                    widths.append(box[2] - box[0] + 4)
                    heights.append(box[3] - box[1] + 4)
            else:
                for _ in poselist:
                    if not clip:
                        widths.append(w + 4)
                        heights.append(h + 4)
                    else:
                        box = spsh.crop((x, y, x+w, y+h)).getbbox()
                        widths.append(box[2] - box[0] + 4)
                        heights.append(box[3] - box[1] + 4)
        spsh.close()
    print(f"Len of widths and heights: {len(widths)}")
    row_width_sums = []
    for i in range(0, len(widths), num_cols):
        row_width_sums.append(sum(widths[i:i+num_cols]))
    final_img_width = max(row_width_sums)

    max_heights = []
    for i in range(0, len(heights), num_cols):
        max_heights.append(max(heights[i:i+num_cols]))
    final_img_height = sum(max_heights)

    return final_img_width, final_img_height, max_heights

def superoptimize(single_png_list, pre_exist_dict):
    new_single_png_list = list(single_png_list) # [(frame:Spriteframe, newPose:str), ...]
    new_pre_exist_dict = dict(pre_exist_dict) # { impth:str: {(coord):[pose, ...], ...}, ... }
    imgplaced = False

    # merge between single and existing imgs
    for single_png_frame, single_png_pose in single_png_list:
        im = Image.open(single_png_frame.imgpath)
        imgplaced = False
        for impth, coords_dict in pre_exist_dict.items():
            spsh = Image.open(impth)
            for coord in coords_dict:
                x, y, w, h = coord
                im2 = spsh.crop((x, y, x+w, y+h)).convert('RGBA')
                if fast_image_cmp(im, im2):
                    new_pre_exist_dict[impth][coord].append((single_png_pose, (single_png_frame.framex, single_png_frame.framey, single_png_frame.framew, single_png_frame.frameh), True))
                    new_single_png_list.remove((single_png_frame, single_png_pose))
                    imgplaced = True
                    break
            if imgplaced:
                break
        im.close()

    return new_pre_exist_dict, new_single_png_list

def make_png_xml(frames, save_dir, character_name="Result", progressupdatefn=None, settings=None):
    clip = settings.get('clip', False)
    reuse_sprites_level = settings.get('reuse_sprites_level', 1)
    prefix_type = settings.get('prefix_type', 'charname')
    custom_prefix = settings.get('custom_prefix', '')
    insist_prefix = settings.get('insist_prefix', False)
    # filter for (not from_single_png)
    # group by imgpath => into a dict { grp: (x, y, w, h)... }
    # for each imgpath: group by (x, y, w, h) in such a way that
    # each (x, y, w, h): [pose1, pose2, ...]
    newPoseNames = add_pose_numbers(frames)
    existing_img_dict, imlist = group_imgs(frames, newPoseNames)
    if reuse_sprites_level == 2:
        existing_img_dict, imlist = superoptimize(imlist, existing_img_dict)

    num_imgs = len(imlist) + get_tot_imgs_from_imdict(existing_img_dict, reuse_sprites_level)
    num_cols = int(sqrt(num_imgs))
    final_img_width, final_img_height, max_heights = calculate_final_size(existing_img_dict, imlist, num_cols, clip, reuse_sprites_level)

    # XML Stuff
    root = ET.Element("TextureAtlas")
    root.tail = linesep
    root.attrib['imagePath'] = character_name + ".png"

    final_img = Image.new('RGBA', (final_img_width, final_img_height), color=(0, 0, 0, 0))
    print("Final image size: ({}, {})".format(final_img_width, final_img_height))
    
    # Constructing the img
    csx = csy = 0
    i = 0
    for i, (frame, posename) in enumerate(imlist):
        # print("Adding {} to final_image...".format(frame.imgpath))
        try:
            old_img = Image.open(frame.imgpath).convert('RGBA')
        except Exception as e:
            exceptionmsg = str(e)
            return 1, exceptionmsg
        else:
            new_img = pad_img(old_img, clip)
            row = i // num_cols
            col = i % num_cols
            if col == 0:
                csx = 0
            csy = sum(max_heights[:row])
            
            subtexture_element = ET.Element("SubTexture")
            subtexture_element.tail = linesep
            subtexture_element.attrib = {
                "name" : ((character_name if prefix_type == 'charname' else custom_prefix) + " " if frame.from_single_png or frame.modified else "") + posename,
                "x": f'{csx}',
                "y": f'{csy}',
                "width": f'{new_img.width}',
                "height": f'{new_img.height}',
                "frameX": str(frame.framex) if frame.framex and not clip else '0', # checking clip checkbox will override any spriteframe settings
                "frameY": str(frame.framey) if frame.framey and not clip else '0',
                "frameWidth": str(frame.framew) if frame.framew and frame.framew != 'default' and str(frame.framew).isnumeric() and not clip else f'{new_img.width}',
                "frameHeight": str(frame.frameh) if frame.frameh and frame.frameh != 'default' and str(frame.frameh).isnumeric() and not clip else f'{new_img.height}',
            }
            root.append(subtexture_element)
            new_img = new_img.convert('RGBA')
            final_img.paste(new_img, (csx, csy))
            
            csx += new_img.width
            
            old_img.close()
            new_img.close()
            progressupdatefn(i+1, frame.imgpath)
    
    # FOR EXISTING SPRITESHEET FRAMES
    i += 1
    for impth, coorddict in existing_img_dict.items(): # {"xyz.png": { (x, y, w, h):[(pose, frameinfo, modified)...] ... }, ... }
        # print("Adding {} to final_image...".format(impth))
        spsh = Image.open(impth)
        for coord, poselist in coorddict.items(): # { (x, y, w, h):[(pose, frameinfo, modified)...], ... }
            try:
                x, y, w, h = coord
                old_img = spsh.crop((x, y, x+w, y+h)).convert('RGBA')
            except Exception as e:
                exceptionmsg = str(e)
                return 1, exceptionmsg
            else:
                new_img = pad_img(old_img, clip)
            
            if reuse_sprites_level >= 1:
                row = i // num_cols
                col = i % num_cols
                if col == 0:
                    csx = 0
                csy = sum(max_heights[:row])
                new_img = new_img.convert('RGBA')
                final_img.paste(new_img, (csx, csy))
                csx += new_img.width
                i += 1
            
            # Adding each pose to poselist
            for pose, frameinfo, modified in poselist:   
                if reuse_sprites_level == 0:
                    row = i // num_cols
                    col = i % num_cols

                    if col == 0:
                        csx = 0
                    csy = sum(max_heights[:row])

                    new_img = new_img.convert('RGBA')
                    print(f"DEBUGINFO: pasting from existing at {csx, csy}")
                    final_img.paste(new_img, (csx, csy))
                    csx += new_img.width
                    i += 1
                subtexture_element = ET.Element("SubTexture")
                subtexture_element.tail = linesep
                if insist_prefix:
                    stname = (character_name if prefix_type == 'charname' else custom_prefix) + " " + pose
                else:
                    stname = (character_name + " " if modified else "") + pose
                subtexture_element.attrib = {
                    "name" : stname,
                    "x": f'{csx}',
                    "y": f'{csy}',
                    "width": f'{new_img.width}',
                    "height": f'{new_img.height}',
                    "frameX": f'{frameinfo[0]}' if frameinfo[0] and not clip else '0', # checking clip checkbox will override any spriteframe settings
                    "frameY": f'{frameinfo[1]}' if frameinfo[1] and not clip else '0',
                    "frameWidth": f'{frameinfo[2]}' if frameinfo[2] and frameinfo[2] != 'default' and str(frameinfo[2]).isnumeric() and not clip else f'{new_img.width}',
                    "frameHeight": f'{frameinfo[3]}' if frameinfo[3] and frameinfo[3] != 'default' and str(frameinfo[3]).isnumeric() and not clip else f'{new_img.height}',
                }
                root.append(subtexture_element)
            
            old_img.close()
            new_img.close() 
            progressupdatefn(i+1, pose)

    # Saving png
    print(f"Saving final image....")
    try:
        final_img.save(path.join(save_dir, character_name) + ".png")
        # final_img.save(save_dir + '\\' + character_name + ".png")
    except Exception as e:
        exceptionmsg = str(e)
        return 1, exceptionmsg
    else:
        final_img.close()
    
    # Saving XML
    print("Saving XML")
    xmltree = ET.ElementTree(root)
    try:
        with open(path.join(save_dir, character_name) + ".xml", 'wb') as f:
        # with open(save_dir + '\\' + character_name + ".xml", 'wb') as f:
            xmltree.write(f, xml_declaration=True, encoding='utf-8')
        print("Done!")
    except Exception as e:
        exceptionmsg = str(e)
        return 1, exceptionmsg
    
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

def save_img_sequence(frames, savedir, updatefn, clip):
    newposes = add_pose_numbers(frames)
    for i, (frame, pose) in enumerate(zip(frames, newposes)):
        try:
            if frame.from_single_png:
                im = Image.open(frame.imgpath).convert('RGBA')
            else:
                im = Image.open(frame.imgpath).convert('RGBA').crop((frame.tex_x, frame.tex_y, frame.tex_x + frame.tex_w, frame.tex_y + frame.tex_h))
            
            if clip:
                im = im.crop(im.getbbox())
            im.save(path.join(savedir, f"{pose}.png"))
            im.close()
            updatefn(i+1, f"{pose}.png")
        except Exception as e:
            return str(e)
    return None

def split_spsh(pngpath, xmlpath, udpdatefn):
    spritesheet = Image.open(pngpath)
    try:
        cleaned_xml = ""
        quotepairity = 0
        with open(xmlpath, 'r') as f:
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
    for i, subtex in enumerate(subtextures):
        tex_x = int(subtex.attrib['x'])
        tex_y = int(subtex.attrib['y'])
        tex_width = int(subtex.attrib['width'])
        tex_height = int(subtex.attrib['height'])
        pose_name = subtex.attrib['name']
        sprite_img = spritesheet.crop((tex_x, tex_y, tex_x+tex_width, tex_y+tex_height)).convert('RGBA')
        sprite_img = sprite_img.convert('RGBA')
        qim = ImageQt(sprite_img)
        sprites.append((qim, pose_name, tex_x, tex_y, tex_width, tex_height))
        udpdatefn((i+1)*50//len(subtextures), pose_name)
    
    return sprites
        

if __name__ == '__main__':
    print("This program is just the engine! To run the actual application, Please type: \npython xmlpngUI.py\nor \npython3 xmlpngUI.py \ndepending on what works")