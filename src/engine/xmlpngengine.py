import xml.etree.ElementTree as ET
from PIL import Image, ImageChops
from os import path, linesep

from utils import imghashes, g_settings, clean_filename

from engine.packingalgorithms import GrowingPacker, OrderedPacker
from engine.spritesheetutils import get_true_frame, add_pose_numbers
from engine.imgutils import pad_img


def fast_image_cmp(im1, im2): # im1 == im2 ?
    if im1.size != im2.size:
        return False
    if im1.tobytes() != im2.tobytes():
        return False
    
    return ImageChops.difference(im1, im2).getbbox() is None

def make_png_xml(frames, save_dir, character_name="Result", progressupdatefn=None, settings=None):
    if settings is None:
        settings = g_settings
    prefix_type = settings.get('prefix_type', 'charname') # use character name or use a custom prefix instead
    custom_prefix = settings.get('custom_prefix', '') # the custom prefix to use
    must_use_prefix = settings.get('must_use_prefix', 0) != 0 # use the custom prefix even if frame is from existing spritesheet
    padding_pixels = settings.get('frame_padding', 0)
    packing_algorithm = settings.get('packing_algo', 0) # 0 = Growing Packer, 1 = Ordered Packer
    # no_merge = settings.get('no_merge', 0) != 0 # no merging lookalike frames

    # print(len(imghashes))
    # print(len(frames))

    try:
        # init XML
        root = ET.Element("TextureAtlas")
        root.text = "\n"
        root.tail = linesep
        root.attrib['imagePath'] = f"{character_name}.png"
        
        new_pose_names = add_pose_numbers(frames)
        for f, pose in zip(frames, new_pose_names):
            final_pose_name = pose
            if f.data.from_single_png or (not f.data.from_single_png and f.modified):
                if prefix_type == 'charname':
                    final_pose_name = f"{character_name} {final_pose_name}"
                elif prefix_type == 'custom':
                    final_pose_name = f"{custom_prefix} {final_pose_name}"
            else:
                if must_use_prefix and prefix_type == 'custom':
                    final_pose_name = f"{custom_prefix} {final_pose_name}"
            
            f.data.xml_pose_name = final_pose_name
        
        frame_dict_arr = []
        current_img_hashes = set([x.data.img_hash for x in frames])

        # Doesn't quite work yet, still a WIP
        # if no_merge:
        #     for f in frames:
        #         frame_dict_arr.append({
        #             "id": f.data.img_hash,
        #             "w": imghashes.get(f.data.img_hash).width + 2*padding_pixels,
        #             "h": imghashes.get(f.data.img_hash).height + 2*padding_pixels,
        #             "frame": f # this comes in handy later on
        #         })
        # else:
        #     pass
        # add the padding to width and height, then actually padding the images (kind of a hack but it works TODO: work out a better way to do this)
        for imhash, img in imghashes.items():
            if imhash in current_img_hashes:
                frame_dict_arr.append({
                    "id": imhash,
                    "w": img.width + 2*padding_pixels,
                    "h": img.height + 2*padding_pixels
                })
        
        if packing_algorithm == 1:
            packer = OrderedPacker()
        else:
            packer = GrowingPacker()
            frame_dict_arr.sort(key= lambda rect: rect.get("h", -100), reverse=True)
        
        packer.fit(frame_dict_arr)

        final_img = Image.new("RGBA", (packer.root['w'], packer.root['h']), (0, 0, 0, 0))
        # frame_dict_arr.sort(key=lambda x: x['id'].img_xml_data.xml_posename)
        prgs = 0
        for r in frame_dict_arr:
            fit = r.get("fit")

            # accounting for user-defined padding
            imhash_img = imghashes.get(r['id'])
            imhash_img = pad_img(imhash_img, False, padding_pixels, padding_pixels, padding_pixels, padding_pixels)
            
            final_img.paste( imhash_img, (fit["x"], fit["y"]) )
            prgs += 1
            progressupdatefn(prgs, "Adding images to spritesheet...")

        # Doesn't quite work yet, still a WIP
        # if no_merge:
        #     for framedict in frame_dict_arr:
        #         frame = framedict['frame']
        #         subtexture_element = ET.Element("SubTexture")
        #         subtexture_element.tail = linesep
        #         w, h = imghashes.get(frame.data.img_hash).size
        #         subtexture_element.attrib = {
        #             "name" : frame.data.xml_pose_name,
        #             "x": str(framedict['fit']['x']),
        #             "y": str(framedict['fit']['y']),
        #             "width": str(w + 2*padding_pixels),
        #             "height": str(h + 2*padding_pixels),
        #             "frameX": str(frame.data.framex),
        #             "frameY": str(frame.data.framey),
        #             "frameWidth": str(frame.data.framew),
        #             "frameHeight": str(frame.data.frameh),
        #         }
        #         root.append(subtexture_element)
        #         prgs += 1
        #         progressupdatefn(prgs, f"Saving {frame.data.xml_pose_name} to XML...")
        # else:
        #     pass
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
                "width": str(w + 2*padding_pixels),
                "height": str(h + 2*padding_pixels),
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
        cleanpath = path.join(save_dir, clean_filename(character_name))
        with open(cleanpath + ".xml", 'wb') as f:
            xmltree.write(f, xml_declaration=True, encoding='utf-8')
        
        print("Saving Image...")
        final_img = final_img.crop(final_img.getbbox())
        final_img.save(cleanpath + ".png")
        final_img.close()
        
        print("Done!")
    except Exception as e:
        return -1, str(e)
    
    return 0, None

def save_img_sequence(frames, savedir, updatefn):
    # Saves each frame as a png
    newposes = add_pose_numbers(frames)
    for i, (frame, pose) in enumerate(zip(frames, newposes)):
        try:
            im = imghashes.get(frame.data.img_hash)
            im = get_true_frame(im, frame.data.framex, frame.data.framey, frame.data.framew, frame.data.frameh)

            cleanpath = path.join(savedir, clean_filename(f"{pose}.png"))
            im.save(cleanpath)
            im.close()
            updatefn(i+1, f"Saving: {pose}.png")
        except Exception as e:
            return str(e)
    return None
        

if __name__ == '__main__':
    print("This program is just the engine! To run the actual application, Please type: \npython xmlpngUI.py\nor \npython3 xmlpngUI.py \ndepending on what works")