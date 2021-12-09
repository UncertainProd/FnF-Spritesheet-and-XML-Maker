from PIL import Image

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
        
        self.is_flip_x = False
        self.is_flip_y = False

class FrameXMLData:
    def __init__(self, pose_name, x, y, w, h, framex, framey, framew, frameh):
        self.pose_name = pose_name
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.framex = framex
        self.framey = framey
        self.framew = framew
        self.frameh = frameh
    
    def convert_to_dict(self):
        attribs = {
            "name": self.pose_name,
            "x": self.x,
            "y": self.y,
            "width": self.w,
            "height": self.h
        }

        if self.framex:
            attribs.update({
                "frameX": self.framex,
                "frameY": self.framey,
                "frameWidth": self.framew,
                "frameHeight": self.frameh,
            })
        
        return attribs