from PIL.ImageQt import QImage
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QCheckBox, QFrame, QPushButton, QWidget, QLabel
import ntpath
from utils import SPRITEFRAME_SIZE


class SpriteFrame(QWidget):
    def __init__(self, imgpath, parent, imdat = None, posename = None):
        super().__init__()
        self.imgpath = imgpath
        self.imdat = imdat
        self.from_single_png = not imdat
        self.image_pixmap = QPixmap(imgpath) if self.from_single_png else QPixmap.fromImage(imdat)
        self.pose_name = "idle" if self.from_single_png else " ".join((posename[:-4]).split(' ')[1:]) # I'm assuming the character name is just the first word
        self.myframe = QFrame(self)
        self.framex = self.framey = self.framew = self.frameh = None

        self.img_label = QLabel(self.myframe)

        if self.from_single_png:
            self.img_label.setToolTip(self.get_tooltip_string(parent))
        else:
            ttstring = f"Image:(part of) {ntpath.basename(imgpath)}\n" + \
                f"Current Pose: {self.pose_name}\n" + \
                f"Will appear in XML as:\n\t<SubTexture name=\"{posename}\" (...) >\n\t# = digit from 0-9"
            self.img_label.setToolTip(ttstring)


        self.img_label.setPixmap(self.image_pixmap.scaled(128, 128))

        self.setFixedSize(QSize(SPRITEFRAME_SIZE, SPRITEFRAME_SIZE))

        self.remove_btn = QPushButton(self.myframe)
        self.remove_btn.move(90, 90)
        self.remove_btn.setIcon(QIcon('./image-assets/remove-frame-icon.svg'))
        self.remove_btn.setIconSize(QSize(40, 40))
        self.remove_btn.setFixedSize(40, 40)
        self.remove_btn.setToolTip("Delete Frame")
        self.remove_btn.clicked.connect(lambda: self.remove_self(parent))

        self.select_checkbox = QCheckBox(self.myframe)
        self.select_checkbox.move(5, 5)
        self.select_checkbox.stateChanged.connect(lambda : self.add_to_selected_arr(parent))

        self.myframe.setStyleSheet("QFrame{border-style:solid; border-color:black; border-width:2px}")
    
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
        self.myframe.setStyleSheet("QFrame{border-style:solid; border-color:black; border-width:2px}")
    
    def remove_self(self, parent):
        parent.labels.remove(self)
        if self in parent.selected_labels:
            parent.selected_labels.remove(self)
        parent.num_labels -= 1

        parent.frames_layout.removeWidget(self)
        self.deleteLater()

        parent.re_render_grid()
        print("Deleting image, count: ", parent.num_labels, "Len of labels", len(parent.labels))
        if len(parent.labels) == 0:
            parent.ui.posename_btn.setDisabled(True)
    
    def add_to_selected_arr(self, parent):
        if self.select_checkbox.checkState() == 0:
            parent.selected_labels.remove(self)
        else:
            parent.selected_labels.append(self)
        
        parent.ui.actionEdit_Frame_Properties.setDisabled(len(parent.selected_labels) <= 0)
    
    def get_tooltip_string(self, parent):
        charname = parent.ui.charname_textbox.text()
        charname = charname.strip() if charname.strip() != "" else "[ENTER YOUR CHARACTER NAME]"
        inside_subtex_name = f"{charname} {self.pose_name}####"

        ttstring = f"Image:{ntpath.basename(self.imgpath)}\n" + \
        f"Current Pose: {self.pose_name}\n" + \
        f"Will appear in XML as:\n\t<SubTexture name=\"{inside_subtex_name}\" (...) >\n\t# = digit from 0-9"
        return ttstring