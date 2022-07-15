from PIL import Image
from utils import g_settings, imghashes, spritesheet_split_cache

class FrameData:
    def __init__(self, impath, from_single_png, pose_name, **xmlinfo):
        # get imgpath
        # get img from imgpath and ?xmlinfo
        # set appropriate frame stuff: depending on from_single_png
        # hash img
        # other stuff...
        # needed in XML table window
        self.imgpath = impath
        self.tx = None
        self.ty = None

        # w, h needed to crop img
        self.tw = None
        self.th = None
        self.from_single_png = from_single_png

        img = Image.open(impath).convert('RGBA')
        self.framex = 0
        self.framey = 0
        self.framew = img.width
        self.frameh = img.height
        should_clip = g_settings['isclip'] != 0
        cached_hash = None
        if not self.from_single_png:
            self.tx = xmlinfo.get("tx", 0)
            self.ty = xmlinfo.get("ty", 0)
            self.tw = xmlinfo.get("tw", 0)
            self.th = xmlinfo.get("th", 0)
            # impath, tex_coords (, clip) -> img
            # if clip == True here, then skip clip step ("if should_clip:...")
            # check if this img is in cache
            cached_hash = spritesheet_split_cache[impath].get((self.tx, self.ty, self.tw, self.th, should_clip))
            if not cached_hash:
                # crop the image
                img = img.crop((self.tx, self.ty, self.tx + self.tw, self.ty + self.th))
            else:
                # print("[DEBUG] Img found in cache!")
                img = imghashes.get(cached_hash)
            # set frame properties from xml
            self.framex = xmlinfo.get("framex", 0)
            self.framey = xmlinfo.get("framey", 0)
            self.framew = xmlinfo.get("framew", 0)
            self.frameh = xmlinfo.get("frameh", 0)
        
        # clipping the image if i didn't already find it in the cache
        if not cached_hash and should_clip:
            imbbox = img.getbbox()
            if imbbox:
                # crop img
                img = img.crop(imbbox)
                # adjust frame properties such that image can be reconstructed from them
                x1, y1, _, _ = imbbox
                self.framex -= x1
                self.framey -= y1
                # Note: frame width and height stay the same
            else:
                print("Unable to crop image!")
        
        # storing some img properties here for efficiency(kinda)
        self.img_width = img.width
        self.img_height = img.height

        # get hash
        self.img_hash = cached_hash if cached_hash else hash(img.tobytes())
        # if hash isnt in imghashes then add it
        if self.img_hash not in imghashes:
            imghashes[self.img_hash] = img
            # cache image for re-use (only imgs from xmls are cached this way)
            if not self.from_single_png:
                spritesheet_split_cache[impath][(self.tx, self.ty, self.tw, self.th, should_clip)] = self.img_hash
        elif cached_hash:
            pass
        else:
            img.close()

        self.pose_name = pose_name
        self.xml_pose_name = ""
    
    def change_img(self, newimg):
        # this method will mostly only be called when flipping the images 
        # so frame data will be unaltered
        self.img_width = newimg.width
        self.img_height = newimg.height

        self.img_hash = hash(newimg.tobytes())
        if self.img_hash not in imghashes:
            imghashes[self.img_hash] = newimg
        else:
            newimg.close()

# not used as of now
class FrameImgData:
    def __init__(self, imgpath, from_single_png, **texinfo):
        self.imgpath = imgpath
        self.from_single_png = from_single_png
        if self.from_single_png:
            self.img = Image.open(imgpath)
            self.img_width = self.img.width
            self.img_height = self.img.height
        else:
            im = Image.open(imgpath)
            self.tx = int(texinfo.get("tx", 0))
            self.ty = int(texinfo.get("ty", 0))
            self.tw = int(texinfo.get("tw", 0))
            self.th = int(texinfo.get("th", 0))
            self.img_width = self.tw
            self.img_height = self.th
            self.img = im.crop((self.tx, self.ty, self.tx + self.tw, self.ty + self.th))
            im.close()
        
        self.img_hash = hash(self.img.tobytes())
        self.img.close()
        self.is_flip_x = False
        self.is_flip_y = False
    
    def __str__(self):
        return f"""Frame Image data:
            Image path: {repr(self.imgpath)}
            From single png: {repr(self.from_single_png)}
            Width: {repr(self.img_width)}
            Height: {repr(self.img_height)}
            Flip-X: {repr(self.is_flip_x)}
            Flip-Y: {repr(self.is_flip_y)}
        """
    
    def modify_image_to(self, im):
        # modifies PIL image object itself (does not change imgpath though)
        self.img = im
        self.img_width = im.width
        self.img_height = im.height

# not used as of now
# class FrameXMLData:
#     def __init__(self, pose_name, x, y, w, h, framex, framey, framew, frameh, flipx=False, flipy=False):
#         self.pose_name = pose_name
#         self.x = x
#         self.y = y
#         self.w = w
#         self.h = h
#         self.framex = framex
#         self.framey = framey
#         self.framew = framew
#         self.frameh = frameh
#         self.is_flip_x = flipx
#         self.is_flip_y = flipy
#         self.xml_posename = None
#         # not exactly relevant to the xml but still
#         self.from_single_png = False
    
#     def convert_to_dict(self):
#         attribs = {
#             "name": self.pose_name,
#             "x": self.x,
#             "y": self.y,
#             "width": self.w,
#             "height": self.h
#         }

#         if self.framex:
#             attribs.update({
#                 "frameX": self.framex,
#                 "frameY": self.framey,
#                 "frameWidth": self.framew,
#                 "frameHeight": self.frameh,
#             })
        
#         return attribs
    
#     def __str__(self):
#         return f"""Frame XML data:
#             FrameX: {repr(self.framex)}
#             FrameY: {repr(self.framey)}
#             FrameWidth: {repr(self.framew)}
#             FrameHeight: {repr(self.frameh)}
#         """