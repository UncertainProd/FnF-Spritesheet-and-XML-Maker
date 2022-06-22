from PIL import Image
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QCheckBox, QFrame, QPushButton, QWidget, QLabel, QApplication
from framedata import FrameData
from utils import SPRITEFRAME_SIZE, imghashes
from os import path


class SpriteFrame(QWidget):
    def __init__(self, parent, imgpath, from_single_png = True, posename = "", **texinfo):
        super().__init__(parent)
        self._frameparent = parent

        # non-ui stuff
        fromsinglepng = from_single_png
        # if from_single_png is None:
            # fromsinglepng = True
        
        # "calculate" the pose_name
        first_num_index = 0
        if not fromsinglepng:
            first_num_index = len(posename)
            for i in range(len(posename)-1, 0, -1):
                if posename[i].isnumeric():
                    first_num_index = i
                else:
                    break
        true_pname = "idle" if fromsinglepng else posename[:first_num_index]

        self.data = FrameData(imgpath, fromsinglepng, true_pname, **texinfo)
        self.modified = False

        # ui stuff
        self.image_pixmap = imghashes.get(self.data.img_hash).toqpixmap()
        self.myframe = QFrame(self)
        self.img_label = QLabel(self.myframe)

        self.img_label.setPixmap(self.image_pixmap.scaled(SPRITEFRAME_SIZE, SPRITEFRAME_SIZE))

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
    
    @property
    def frameparent(self):
        return self._frameparent
    
    @frameparent.setter
    def frameparent(self, newparent):
        self._frameparent = newparent
        self.setParent(self._frameparent)

    # overriding the default mousePressEvent
    def mousePressEvent(self, event):
        btnpressed = event.button()
        if btnpressed == 1: # left mouse button
            prevstate = self.select_checkbox.checkState()
            newstate = 0 if prevstate != 0 else 1
            self.select_checkbox.setChecked(newstate)
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                self.frameparent.ranged_selection_handler(self)
        else:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ShiftModifier:
                self.frameparent.ranged_deletion_handler(self)
    
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
        # parent.update_frame_dict(self.img_xml_data.pose_name, self, remove=True)
        self.deleteLater()

        parent.re_render_grid()
        # print("Deleting image, count: ", parent.num_labels, "Len of labels", len(parent.labels))
        if len(parent.labels) == 0:
            parent.ui.posename_btn.setDisabled(True)
            parent.ui.actionPreview_Animation.setEnabled(False)
            parent.ui.actionView_XML_structure.setEnabled(False)
            # parent.ui.actionChange_Frame_Ordering.setEnabled(False)
    
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
        inside_subtex_name = f"{charname} {self.data.pose_name}####" if self.data.from_single_png or self.modified else f"{self.data.pose_name}####"

        ttstring = f'''Image: {path.basename(self.data.imgpath)}
Current Pose: {self.data.pose_name}
Will appear in XML as:
\t<SubTexture name=\"{inside_subtex_name}\" (...) >
\t# = digit from 0-9'''

        return ttstring
    
    def flip_img(self, dxn):
        # flip the PIL img of self
        if dxn == 'X':
            img = imghashes.get(self.data.img_hash).transpose(Image.FLIP_LEFT_RIGHT)
        elif dxn == 'Y':
            img = imghashes.get(self.data.img_hash).transpose(Image.FLIP_TOP_BOTTOM)
        else:
            print("Something went wrong!")
        
        # change hash accordingly
        self.data.change_img(img)

        # do pixmap stuff
        # Note: the above fn could have closed the img so pass the hash instead
        self.change_ui_img(self.data.img_hash)

    def change_ui_img(self, newimghash):
        self.image_pixmap = imghashes.get(newimghash).toqpixmap()
        self.img_label.setPixmap(self.image_pixmap.scaled(SPRITEFRAME_SIZE, SPRITEFRAME_SIZE))


if __name__ == '__main__':
    print("To run the actual application, Please type: \npython xmlpngUI.py\nor \npython3 xmlpngUI.py \ndepending on what works")