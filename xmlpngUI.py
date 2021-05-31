import sys
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QGridLayout, QInputDialog, QLineEdit, QMessageBox, QPushButton, QWidget, QLabel, QFileDialog
from PyQt5 import uic
import os
import ntpath
import xmlpngengine

class SpriteFrame(QWidget):
    def __init__(self, imgpath, parent):
        super().__init__()
        self.imgpath = imgpath
        self.image_pixmap = QPixmap(imgpath)
        self.pose_name = "idle"

        self.img_label = QLabel(self)
        self.img_label.setToolTip(ntpath.basename(imgpath))
        self.img_label.setPixmap(self.image_pixmap.scaled(130, 130))

        self.setFixedSize(QSize(130, 130))

        self.remove_btn = QPushButton(self)
        self.remove_btn.move(90, 90)
        self.remove_btn.setIcon(QIcon('./image-assets/remove_img_new.png'))
        self.remove_btn.setIconSize(QSize(40, 40))
        self.remove_btn.setFixedSize(40, 40)
        self.remove_btn.setToolTip("Delete Frame")
        self.remove_btn.clicked.connect(lambda: self.remove_self(parent))

        self.info_btn = QPushButton(self)
        self.info_btn.move(0, 90)
        self.info_btn.setIcon(QIcon('./image-assets/info_icon.svg'))
        self.info_btn.setIconSize(QSize(35, 35))
        self.info_btn.setFixedSize(40, 40)
        self.info_btn.setToolTip("Frame Info")
        self.info_btn.clicked.connect(self.display_frame_info)
    
    def remove_self(self, parent):
        parent.labels.remove(self)
        parent.num_labels -= 1

        parent.layout.removeWidget(self)
        self.deleteLater()

        parent.re_render_grid()
        print("Deleting image, count: ", parent.num_labels, "Len of labels", len(parent.labels))
    
    def display_frame_info(self):
        print(self.imgpath)
        text, okPressed = QInputDialog.getText(None, "Change Pose Prefix Name", "Current Pose prefix:"+(" "*50), QLineEdit.Normal, self.pose_name) # very hack-y soln but it works!
        if okPressed and text != '':
            print("new pose prefix = ", text)
            self.pose_name = text
        else:
            print("Cancel pressed!")


class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        uic.loadUi('XmlPngUIFile.ui', self)
        self.setFixedSize(834, 520)
        self.xml_generate_button.clicked.connect(self.generate_xml)
        self.setWindowTitle("XML Generator")
        self.sprite_frames.setWidgetResizable(True)
        self.sprite_frame_content = QWidget()
        self.layout = QGridLayout(self.sprite_frame_content)
        self.sprite_frames.setWidget(self.sprite_frame_content)

        self.num_labels = 0
        self.labels = []

        self.add_img_button = QPushButton()
        self.add_img_button.setIcon(QIcon("./image-assets/AddImg.png"))
        self.add_img_button.setGeometry(0, 0, 130, 130)
        self.add_img_button.setFixedSize(QSize(130, 130))
        self.add_img_button.setIconSize(QSize(130, 130))
        self.add_img_button.clicked.connect(self.open_file_dialog)

        self.layout.addWidget(self.add_img_button, 0, 0, Qt.AlignmentFlag(0x1|0x20))
        self.myTabs.setCurrentIndex(0)

        self.setWindowIcon(QIcon("./image-assets/appicon.png"))
    
    def open_file_dialog(self):
        imgpaths = QFileDialog.getOpenFileNames(
            caption="Select sprite frames", 
            filter="PNG Images (*.png)",
            directory=os.getcwd()
        )[0]
        for pth in imgpaths:
            self.add_img(pth)
    
    def add_img(self, imgpath):
        print("Adding image, prevcount: ", self.num_labels)
        self.labels.append(SpriteFrame(imgpath, self))
        self.layout.removeWidget(self.add_img_button)
        self.layout.addWidget(self.labels[-1], self.num_labels // 4, self.num_labels % 4, Qt.AlignmentFlag(0x1|0x20))
        self.num_labels += 1
        self.layout.addWidget(self.add_img_button, self.num_labels // 4, self.num_labels % 4, Qt.AlignmentFlag(0x1|0x20))
    
    def re_render_grid(self):
        for i, sp in enumerate(self.labels):
            self.layout.addWidget(sp, i//4, i%4, Qt.AlignmentFlag(0x1|0x20))
        self.layout.removeWidget(self.add_img_button)
        self.layout.addWidget(self.add_img_button, self.num_labels // 4, self.num_labels % 4, Qt.AlignmentFlag(0x1|0x20))
    
    def generate_xml(self):
        charname:str = self.character_name_textbox.text()
        charname = charname.strip()
        clip = self.border_clip_checkbox.checkState()
        if self.num_labels > 0 and charname != '':
            savedir = QFileDialog.getExistingDirectory(caption="Save files to...")
            print("Stuff saved to: ", savedir)
            if savedir != '':
                xmlpngengine.make_png_xml([lab.imgpath for lab in self.labels], [lab.pose_name for lab in self.labels], savedir, charname, False if clip == 0 else True)
                self.successbox = QMessageBox(self)
                self.successbox.setWindowTitle("Done!")
                self.successbox.setText("Your files have been generated!\nCheck the folder you had selected")
                self.successbox.setIcon(QMessageBox.Information)
                x = self.successbox.exec_()
                print("[DEBUG] Exit status of error box: "+str(x))
        else:
            self.errbox = QMessageBox(self)
            self.errbox.setWindowTitle("Error!")
            errtxt = "Please enter some frames" if self.num_labels <= 0 else "Please enter the name of your character"
            self.errbox.setText(errtxt)
            self.errbox.setIcon(QMessageBox.Critical)
            x = self.errbox.exec_()
            print("[DEBUG] Exit status of error box: "+str(x))



if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    myapp = MyApp()
    myapp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Closing...")