import os
import xml.etree.ElementTree as ET
from PIL import Image

def pad_img(img, clip=False, top=2, right=2, bottom=2, left=2):
    if clip:
        img = img.crop(img.getbbox())
    
    width, height = img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(img.mode, (new_width, new_height), (0, 0, 0, 0))
    result.paste(img, (left, top))
    return result

def add_pose_numbers(pose_arr:list[str]):
    unique_poses = list(set(pose_arr))
    pose_counts = dict([ (ele, 0) for ele in unique_poses ])
    new_pose_arr = list(pose_arr)
    for i in range(len(new_pose_arr)):
        pose_counts[new_pose_arr[i]] += 1
        new_pose_arr[i] = new_pose_arr[i] + str(pose_counts[new_pose_arr[i]] - 1).zfill(4)
    return new_pose_arr

def make_png_xml(imgpaths:list[str], pose_names:list[str], save_dir:str, character_name:str="Result", clip=False):
    # PNG stuff
    widths = []
    heights = []
    for impath in imgpaths:
        im = Image.open(impath)
        if not clip:
            widths.append(im.width + 4) # 2 pixels padding on each side
            heights.append(im.height + 4)
        else:
            box = im.getbbox()
            widths.append(box[2] - box[0] + 4)
            heights.append(box[3] - box[1] + 4)
        im.close()
    row_width_sums = []
    for i in range(0, len(widths), 4):
        row_width_sums.append(sum(widths[i:i+4]))
    final_img_width = max(row_width_sums)

    max_heights = []
    for i in range(0, len(heights), 4):
        max_heights.append(max(heights[i:i+3]))
    final_img_height = sum(max_heights)

    # XML Stuff
    root = ET.Element("TextureAtlas")
    root.tail = os.linesep
    root.attrib['imagePath'] = character_name + ".png"

    final_img = Image.new('RGBA', (final_img_width, final_img_height), color=(0, 0, 0, 0))
    print("Final image size: ({}, {})".format(final_img_width, final_img_height))
    num_cols = 4
    csx = csy = 0
    newPoseNames = add_pose_numbers(pose_names)
    for i, imgpath in enumerate(imgpaths):
        print("Adding {} to final_image...".format(imgpath))
        old_img = Image.open(imgpath)
        new_img = pad_img(old_img, clip)

        row = i // num_cols
        col = i % num_cols

        if col == 0:
            csx = 0
        csy = sum(max_heights[:row])
        
        subtexture_element = ET.Element("SubTexture")
        subtexture_element.tail = os.linesep
        subtexture_element.attrib = {
            "name" : newPoseNames[i],
            "x": f'{csx}',
            "y": f'{csy}',
            "width": f'{new_img.width}',
            "height": f'{new_img.height}',
            "frameX": '0',
            "frameY": '0',
            "frameWidth": f'{new_img.width}',
            "frameHeight": f'{new_img.height}',
        }
        root.append(subtexture_element)

        final_img.paste(new_img, (csx, csy))
        
        csx += new_img.width
        
        old_img.close()
        new_img.close()

    # Saving png
    print(f"Saving final image....")
    final_img.save(os.path.join(save_dir, character_name) + ".png")
    final_img.close()

    # Saving XML
    print("Saving XML")
    xmltree = ET.ElementTree(root)
    with open(os.path.join(save_dir, character_name) + ".xml", 'wb') as f:
        xmltree.write(f, xml_declaration=True, encoding='utf-8')
    print("Done!")


if __name__ == '__main__':
    # Just a test script ignore this...
    print(add_pose_numbers([
        "Dad Sing Note DOWN", "Dad Sing Note DOWN", "Dad Sing Note DOWN", "Dad Sing Note DOWN", 
        "Dad Sing Note LEFT", 
        "Dad Sing Note RIGHT", "Dad Sing Note RIGHT", "Dad Sing Note RIGHT", 
        "Dad Sing Note UP", "Dad Sing Note UP", "Dad Sing Note UP", "Dad Sing Note UP",
        "Dad Sing Note DOWN", "Dad Sing Note DOWN",
        "Dad Sing Note RIGHT", "Dad Sing Note RIGHT"
    ]))