from animpreviewwindow import Ui_animation_view
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer
from xmlpngengine import get_true_frame
from utils import imghashes

class AnimationView(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_animation_view()
        self.ui.setupUi(self)
        # self.setStyleSheet(get_stylesheet_from_file("app-styles.qss"))

        # self.ui.pose_combobox.addItems([""])
        self.ui.play_anim_button.clicked.connect(self.play_animation)
        self.ui.animation_display_area.setText("Click 'Play Animation' to start the animation preview")
        self.ui.animation_display_area.setStyleSheet("background-color:#696969;")
        
        self.animframes = []
        self.anim_names = {}
        self.frameindex = 0
        self.animstarted = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.set_next_frame)
    
    def parse_and_load_frames(self, frames):
        for f in frames:
            if f.img_xml_data.pose_name in self.anim_names:
                self.anim_names[f.img_xml_data.pose_name].append(f)
            else:
                self.anim_names[f.img_xml_data.pose_name] = [ f ]
        self.ui.pose_combobox.addItems(list(self.anim_names.keys()))
    
    def play_animation(self):
        if self.animstarted:
            self.timer.stop()
            self.animstarted = False
            self.ui.play_anim_button.setText("Play Animation")
        else:
            self.animstarted = True
            framerate = self.ui.framerate_adjust.value()
            animname = self.ui.pose_combobox.currentText()
            self.animframes = self.anim_names[animname]
            self.frameindex = 0
            print(f"Playing {animname} at {framerate}fps with nframes:{len(self.animframes)}")
            self.ui.play_anim_button.setText("Stop Animation")
            self.timer.start(1000/framerate)
    
    def set_next_frame(self):
        curframe = self.animframes[self.frameindex]
        truframe_pixmap = get_true_frame(
            imghashes.get(curframe.img_data.img_hash),
            curframe.img_xml_data.framex if curframe.img_xml_data.framex is not None else 0,
            curframe.img_xml_data.framey if curframe.img_xml_data.framey is not None else 0,
            curframe.img_xml_data.framew if curframe.img_xml_data.framew is not None else imghashes.get(curframe.img_data.img_hash).width,
            curframe.img_xml_data.frameh if curframe.img_xml_data.frameh is not None else imghashes.get(curframe.img_data.img_hash).height,
            curframe.img_xml_data.is_flip_x,
            curframe.img_xml_data.is_flip_y
        ).toqpixmap()
        self.ui.animation_display_area.setPixmap(truframe_pixmap)
        self.frameindex = (self.frameindex + 1) % len(self.animframes)
    
    def closeEvent(self, a0):
        self.timer.stop()
        self.animstarted = False
        self.ui.animation_display_area.clear()
        self.ui.pose_combobox.clear()
        self.animframes.clear()
        self.anim_names.clear()
        self.frameindex = 0
        return super().closeEvent(a0)
