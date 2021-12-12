from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel, QSpacerItem, QWidget

from frameorderwindowUI import Ui_FrameOrderScreen
from utils import SPRITEFRAME_SIZE

class DisplayFrame(QWidget):
    def __init__(self, parent, dapixmap):
        super().__init__(parent=parent)
        # needs: pixmap, frame
        self.display_frame = QFrame(self)
        self.imglabel = QLabel(self.display_frame)
        self.imglabel.setPixmap(dapixmap.scaled(SPRITEFRAME_SIZE, SPRITEFRAME_SIZE))
        self.setFixedSize(QSize(SPRITEFRAME_SIZE, SPRITEFRAME_SIZE))
        self.display_frame.setFixedSize(QSize(SPRITEFRAME_SIZE, SPRITEFRAME_SIZE))
        self.current_border_color = "black"
        self.display_frame.setStyleSheet("QFrame{border-style:solid; border-color:" + self.current_border_color + "; border-width:2px}")


class FrameOrderScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_FrameOrderScreen()
        self.ui.setupUi(self)
        self.ui.pose_name_combo_box.currentIndexChanged.connect(self.handle_index_change)
        
        self.num_cols = 6
        self.num_rows = 1
        self.grid_layout = QGridLayout(self.ui.frame_addition_widget)
        self.ui.scrollArea.setWidget(self.ui.frame_addition_widget)
        
        # for i in range(self.num_cols):
            # self.grid_layout.setColumnMinimumWidth(i, 0)
            # self.grid_layout.setColumnStretch(i, 0)
        # for i in range(self.num_rows):
            # self.grid_layout.setRowMinimumHeight(i, 0)
            # self.grid_layout.setRowStretch(i, 0)
        
        # vspcr = QSpacerItem(1, 1)
        # self.grid_layout.addItem(vspcr, self.num_rows, 0, 1, 4)

        # hspcr = QSpacerItem(1, 1)
        # self.grid_layout.addItem(hspcr, 0, self.num_cols, self.num_rows, 1)

        self.frame_dict = None
        self.cur_frames = None
        self.cur_display_frames = []
    
    def clear_grid(self):
        labs = list(self.cur_display_frames)
        for lab in labs:
            self.grid_layout.removeWidget(lab)

    def re_render_grid(self):
        self.clear_grid()
        self.num_rows = 1 + len(self.cur_display_frames)//self.num_cols
        for i in range(self.num_cols):
            self.grid_layout.setColumnMinimumWidth(i, 0)
            self.grid_layout.setColumnStretch(i, 0)
        for i in range(self.num_rows):
            self.grid_layout.setRowMinimumHeight(i, 0)
            self.grid_layout.setRowStretch(i, 0)

        vspcr = QSpacerItem(1, 1)
        self.grid_layout.addItem(vspcr, self.num_rows, 0, 1, 4)

        hspcr = QSpacerItem(1, 1)
        self.grid_layout.addItem(hspcr, 0, self.num_cols, self.num_rows, 1)
        

        for i, f in enumerate(self.cur_display_frames):
            self.grid_layout.addWidget(f, i // self.num_cols, i % self.num_cols, Qt.AlignmentFlag(0x1|0x20))

    def resizeEvent(self, a0):
        w = self.width()
        # print("Current width", w)
        if w < 1228:
            self.num_cols = 6
        elif 1228 <= w <= 1652:
            self.num_cols = 8
        else:
            self.num_cols = 12
        self.re_render_grid()
        return super().resizeEvent(a0)

    def set_frame_dict(self, frame_dict):
        self.frame_dict = frame_dict
        self.ui.pose_name_combo_box.clear()
        self.ui.pose_name_combo_box.addItems(frame_dict.keys())
        self.ui.pose_name_combo_box.setCurrentIndex(0)
    
    def handle_index_change(self, newind):
        posename = self.ui.pose_name_combo_box.currentText()
        if posename:
            self.cur_frames = self.frame_dict[posename]
            self.clear_grid()
            self.add_frames()
    
    def add_frames(self):
        self.cur_display_frames = []
        self.num_rows = 1 + len(self.cur_frames) // self.num_cols
        
        self.grid_layout.setRowMinimumHeight(self.num_rows - 1, 0)
        self.grid_layout.setRowStretch(self.num_rows - 1, 0)
        
        vspcr = QSpacerItem(1, 1)
        self.grid_layout.addItem(vspcr, self.num_rows, 0, 1, 4)

        hspcr = QSpacerItem(1, 1)
        self.grid_layout.addItem(hspcr, 0, self.num_cols, self.num_rows, 1)
        
        for i, frame in enumerate(self.cur_frames):
            self.cur_display_frames.append(DisplayFrame(self, frame.image_pixmap))
            self.grid_layout.addWidget(self.cur_display_frames[-1], i // self.num_cols, i % self.num_cols, Qt.AlignmentFlag(0x1|0x20))