from animpreviewwindow import Ui_animation_view
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer

class AnimationView(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_animation_view()
        self.ui.setupUi(self)

        # self.ui.pose_combobox.addItems([""])
        self.ui.play_anim_button.clicked.connect(self.play_animation)
        self.ui.animation_display_area.setText("")
        
        self.animframes = []
        self.anim_names = {}
        self.frameindex = 0
        self.animstarted = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.set_next_frame)
    
    def parse_and_load_frames(self, frames):
        for f in frames:
            if f.pose_name in self.anim_names:
                self.anim_names[f.pose_name].append(f)
            else:
                self.anim_names[f.pose_name] = [ f ]
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
        self.ui.animation_display_area.setPixmap(self.animframes[self.frameindex].image_pixmap)
        self.frameindex = (self.frameindex + 1) % len(self.animframes)
    
    def closeEvent(self, a0):
        self.timer.stop()
        self.animstarted = False
        self.ui.animation_display_area.clear()
        self.ui.pose_combobox.clear()
        return super().closeEvent(a0)
