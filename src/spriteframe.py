from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QCheckBox, QFrame, QPushButton, QWidget, QLabel
from framedata import FrameImgData, FrameXMLData
from utils import SPRITEFRAME_SIZE
from os import path


class SpriteFrame(QWidget):
    def __init__(self, parent, imgpath, impixmap = None, posename = None, **texinfo):
        super().__init__(parent)
        # ID: pose_name + order(index?)
        # self.ID = [None, -1]
        self.frameparent = parent
        # XML related info calculated for a spriteframe
        # name:str
        # x:int, y:int, w:int, h:int
        # frameX:null<int>, frameY:null<int>, frameWidth:null<int>, frameHeight:null<int>

        # Info from the input that I can get
        # imgpath:str, (w:int, h:int) --derived from--> img:Image
        # from_single_png:bool
        # if from_single_png:-
        # spritesheet_path:str, xml_path:str
        # src_info: xml related info (see above)

        # stores the PIL image of the frame, along with other data about the image
        self.img_data = FrameImgData(imgpath, not impixmap, **texinfo)

        # self.imgpath = imgpath
        # self.imdat = imdat
        # self.from_single_png = not imdat
        self.modified = False
        self.image_pixmap = QPixmap(imgpath) if self.img_data.from_single_png else impixmap
        # self.img_width = self.image_pixmap.width()
        # self.img_height = self.image_pixmap.height()

        first_num_index = len(posename)-1
        for i in range(len(posename)-1, 0, -1):
            if posename[i].isnumeric():
                first_num_index = i
            else:
                break
        true_pname = "idle" if self.img_data.from_single_png else posename[:first_num_index]
        # if not self.img_data.from_single_png and posename[first_num_index:].isnumeric():
            # self.ID[1] = int(posename[first_num_index:])
        # else:
            # self.ID[1] = -1

        self.myframe = QFrame(self)
        # self.framex = self.framey = self.framew = self.frameh = None
        # self.tex_x = texinfo.get("tx", None)
        # self.tex_y = texinfo.get("ty", None)
        # self.tex_w = texinfo.get("tw", None)
        # self.tex_h = texinfo.get("th", None)

        # store data about this frame that will be needed for the XML
        self.img_xml_data = FrameXMLData(
            true_pname, 
            None, None, 
            self.img_data.img_width, self.img_data.img_height, 
            texinfo.get("framex", 0), texinfo.get("framey", 0), 
            texinfo.get("framew", self.img_data.img_width), texinfo.get("frameh", self.img_data.img_height)
        )
        # self.ID[0] = self.img_xml_data.pose_name
        
        self.img_label = QLabel(self.myframe)

        if self.img_data.from_single_png:
            self.img_label.setToolTip(self.get_tooltip_string(self.frameparent))
        else:
            ttstring = f"Image:(part of) {path.basename(imgpath)}\n" + \
                f"Current Pose: {self.img_xml_data.pose_name}\n" + \
                f"Will appear in XML as:\n\t<SubTexture name=\"{posename}\" (...) >\n\t# = digit from 0-9"
            self.img_label.setToolTip(ttstring)


        self.img_label.setPixmap(self.image_pixmap.scaled(SPRITEFRAME_SIZE, SPRITEFRAME_SIZE))
        # self.is_flip_x = False
        # self.is_flip_y = False

        self.setFixedSize(QSize(SPRITEFRAME_SIZE, SPRITEFRAME_SIZE))

        self.remove_btn = QPushButton(self.myframe)
        self.remove_btn.move(90, 90)
        self.remove_btn.setIcon(QIcon('./assets/remove-frame-icon.svg'))
        self.remove_btn.setIconSize(QSize(40, 40))
        self.remove_btn.setFixedSize(40, 40)
        self.remove_btn.setToolTip("Delete Frame")
        self.remove_btn.clicked.connect(lambda: self.remove_self(self.frameparent))

        self.select_checkbox = QCheckBox(self.myframe)
        self.select_checkbox.move(5, 5)
        self.select_checkbox.stateChanged.connect(lambda : self.add_to_selected_arr(self.frameparent))

        self.current_border_color = "black"
        self.myframe.setStyleSheet("QFrame{border-style:solid; border-color:" + self.current_border_color + "; border-width:2px}")
    
    # overriding the default mousePressEvent
    def mousePressEvent(self, event):
        btnpressed = event.button()
        if btnpressed == 1: # left mouse button
            prevstate = self.select_checkbox.checkState()
            newstate = 0 if prevstate != 0 else 1
            self.select_checkbox.setChecked(newstate)
        else:
            print("Click with the left mouse button")
    
    # overriding the default enterEvent
    def enterEvent(self, event):
        self.myframe.setStyleSheet("QFrame{ border-style:solid; border-color:#FFC9DEF5; border-width:4px }")
    
    # overriding the default leaveEvent
    def leaveEvent(self, event):
        self.myframe.setStyleSheet("QFrame{border-style:solid; border-color:" + self.current_border_color + "; border-width:2px}")
    
    def remove_self(self, parent):
        parent.labels.remove(self)
        if self in parent.selected_labels:
            parent.selected_labels.remove(self)
        parent.num_labels -= 1

        parent.frames_layout.removeWidget(self)
        parent.add_or_update_frame_dict(self.img_xml_data.pose_name, self, remove=True)
        self.deleteLater()

        parent.re_render_grid()
        print("Deleting image, count: ", parent.num_labels, "Len of labels", len(parent.labels))
        if len(parent.labels) == 0:
            parent.ui.posename_btn.setDisabled(True)
            parent.ui.actionPreview_Animation.setEnabled(False)
            parent.ui.actionView_XML_structure.setEnabled(False)
    
    def add_to_selected_arr(self, parent):
        if self.select_checkbox.checkState() == 0:
            parent.selected_labels.remove(self)
            self.current_border_color = "black"
            self.myframe.setStyleSheet("QFrame{border-style:solid; border-color:" + self.current_border_color + "; border-width:2px}")
        else:
            parent.selected_labels.append(self)
            self.current_border_color = "green"
            self.myframe.setStyleSheet("QFrame{border-style:solid; border-color:" + self.current_border_color + "; border-width:2px}")
        
        parent.ui.actionEdit_Frame_Properties.setDisabled(len(parent.selected_labels) <= 0)
    
    def get_tooltip_string(self, parent):
        charname = parent.ui.charname_textbox.text()
        charname = charname.strip() if charname.strip() != "" else "[ENTER YOUR CHARACTER NAME]"
        inside_subtex_name = f"{charname} {self.img_xml_data.pose_name}####" if self.img_data.from_single_png or self.modified else f"{self.img_xml_data.pose_name}####"

        ttstring = f"Image:{path.basename(self.img_data.imgpath)}\n" + \
        f"Current Pose: {self.img_xml_data.pose_name}\n" + \
        f"Will appear in XML as:\n\t<SubTexture name=\"{inside_subtex_name}\" (...) >\n\t# = digit from 0-9"
        return ttstring
    
    def change_img_to(self, newimg):
        self.img_data.modify_image_to(newimg)
        # make changes in xml data too
        self.img_xml_data.w = newimg.width
        self.img_xml_data.h = newimg.height
    
    def __str__(self):
        # return "ID: " + str(self.ID) + "\n" + str(self.img_data) + "\n" + str(self.img_xml_data)
        return str(self.img_data) + "\n" + str(self.img_xml_data)

if __name__ == '__main__':
    print("To run the actual application, Please type: \npython xmlpngUI.py\nor \npython3 xmlpngUI.py \ndepending on what works")