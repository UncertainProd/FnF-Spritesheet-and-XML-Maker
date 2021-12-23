from PyQt5.QtWidgets import QTableWidgetItem, QWidget
from PyQt5.QtCore import Qt
from utils import temp_path_shortener, imghashes
from xmlpngengine import get_true_frame
from xmltablewindowUI import Ui_TableWidgetThing

class XMLTableView(QWidget):
    def __init__(self, table_headings):
        super().__init__()
        self.ui = Ui_TableWidgetThing()
        self.ui.setupUi(self)

        self.ui.xmltable.setColumnCount(len(table_headings))
        self.ui.xmltable.setHorizontalHeaderLabels(table_headings)

        # self.ui.xmltable.cellClicked.connect(self.handle_cell_click)
        # self.ui.xmltable.cellActivated.connect(self.handle_cell_click)
        # self.ui.xmltable.cellPressed.connect(self.handle_cell_click)
        self.ui.frame_preview_label.setStyleSheet("QFrame{ border: 1px solid black; }")
        self.ui.xmltable.selectionModel().selectionChanged.connect(self.handle_cell_selection)

        # list[SpriteFrame]
        self.tabledata = []
        self.canchange = True
        self.frame_info = [None, None, None, None]
        self.frame_spinboxes = [self.ui.framex_spinbox, self.ui.framey_spinbox, self.ui.framewidth_spinbox, self.ui.frameheight_spinbox]
        
        self.ui.framex_spinbox.valueChanged.connect(self.handle_framex_change)
        self.ui.framey_spinbox.valueChanged.connect(self.handle_framey_change)
        self.ui.framewidth_spinbox.valueChanged.connect(self.handle_framew_change)
        self.ui.frameheight_spinbox.valueChanged.connect(self.handle_frameh_change)
        
        self.selected_row = None
        self.selected_row_index = None

        self.was_opened = False

    def handle_framex_change(self, newval):
        if self.canchange:
            if self.selected_row:
                self.selected_row.data.framex = newval
                self.ui.xmltable.setItem(self.selected_row_index, 4, QTableWidgetItem(str(newval)))
                self.set_true_frame()

    def handle_framey_change(self, newval):
        if self.canchange:
            if self.selected_row:
                self.selected_row.data.framey = newval
                self.ui.xmltable.setItem(self.selected_row_index, 5, QTableWidgetItem(str(newval)))
                self.set_true_frame()

    def handle_framew_change(self, newval):
        if self.canchange:
            if self.selected_row:
                self.selected_row.data.framew = newval
                self.ui.xmltable.setItem(self.selected_row_index, 6, QTableWidgetItem(str(newval)))
                self.set_true_frame()

    def handle_frameh_change(self, newval):
        if self.canchange:
            if self.selected_row:
                self.selected_row.data.frameh = newval
                self.ui.xmltable.setItem(self.selected_row_index, 7, QTableWidgetItem(str(newval)))
                self.set_true_frame()

    def set_true_frame(self):
        # set the frame pixmap
        curimg = imghashes.get(self.selected_row.data.img_hash)
        truframe = get_true_frame(
            curimg, 
            self.selected_row.data.framex if self.selected_row.data.framex is not None else 0,
            self.selected_row.data.framey if self.selected_row.data.framey is not None else 0,
            self.selected_row.data.framew if self.selected_row.data.framew is not None else curimg.width,
            self.selected_row.data.frameh if self.selected_row.data.frameh is not None else curimg.height,
        ).toqpixmap()
        self.ui.frame_preview_label.setPixmap(truframe)
        self.ui.frame_preview_label.setFixedSize(truframe.width(), truframe.height())

    def fill_data(self, data):
        # data: list[Spriteframe]
        table = self.ui.xmltable
        if self.was_opened:
            table.cellChanged.disconnect(self.handle_cell_change)
        self.tabledata = data
        table.setRowCount(len(data))
        for rownum, label in enumerate(data):
            tabledat = [label.data.imgpath, label.data.pose_name, label.data.img_width, label.data.img_height, label.data.framex, label.data.framey, label.data.framew, label.data.frameh]
            for colnum, col in enumerate(tabledat):
                table_cell = QTableWidgetItem(str(col))
                if colnum < 4:
                    table_cell.setFlags(table_cell.flags() ^ Qt.ItemIsEditable)
                table.setItem(rownum, colnum, table_cell)
        
        table.cellChanged.connect(self.handle_cell_change)
        self.was_opened = True
    
    def handle_cell_change(self, row, col):
        idx = col - 4

        if idx >= 0:
            self.canchange = False
            newval = self.ui.xmltable.item(row, col).text()
            if newval.lower() == 'default':
                # default framex = framey = 0, framew = img.width, frameh = img.height
                if idx <= 1:
                    newval = 0
                elif idx == 2:
                    newval = self.selected_row.data.img_width
                elif idx == 3:
                    newval = self.selected_row.data.img_height
                else:
                    print("Something's wrong")
                self.ui.xmltable.setItem(row, col, QTableWidgetItem(str(newval)))
            else:
                try:
                    newval = int(newval)
                    assert (idx >= 2 and newval > 0) or (idx < 2)
                except Exception as e:
                    print("Exception:\n", e)
                    if idx == 0:
                        newval = self.selected_row.data.framex
                    elif idx == 1:
                        newval = self.selected_row.data.framey
                    elif idx == 2:
                        newval = self.selected_row.data.framew
                    elif idx == 3:
                        newval = self.selected_row.data.frameh
                    else:
                        print("Something's wrong")
                    self.ui.xmltable.setItem(row, col, QTableWidgetItem(str(newval)))
            
            self.frame_spinboxes[idx].setValue(newval if newval else 0)
            self.canchange = True
            
            # idx: 0 = framex, 1 = framey, 2 = framew, 3 = frameh
            if idx == 0:
                self.selected_row.data.framex = newval
            elif idx == 1:
                self.selected_row.data.framey = newval
            elif idx == 2:
                self.selected_row.data.framew = newval
            elif idx == 3:
                self.selected_row.data.frameh = newval
            else:
                print("[ERROR] Some error occured!")
            
            self.set_true_frame()

    def handle_cell_selection(self, selected, deselected):
        if selected.indexes():
            self.selected_row_index = selected.indexes()[-1].row()
            self.handle_display_stuff(self.selected_row_index)
        elif deselected.indexes():
            self.selected_row_index = deselected.indexes()[-1].row()
            self.handle_display_stuff(self.selected_row_index)
        else:
            print("Something's weird here")

    def handle_display_stuff(self, row):
        self.selected_row = self.tabledata[row]
        short_path = temp_path_shortener(self.selected_row.data.imgpath)

        self.ui.frame_preview_label.clear()
        self.set_true_frame()
        
        if self.selected_row.data.from_single_png:
            self.ui.frame_info_label.setText(f"Image path: {short_path}\tFrom existing spritesheet: No")
        else:
            self.ui.frame_info_label.setText(f"Image path: {short_path}\tFrom existing spritesheet: Yes\tCo-ords in source spritesheet: x={self.selected_row.data.tx} y={self.selected_row.data.ty} w={self.selected_row.data.tw} h={self.selected_row.data.th}")
        
        self.frame_info = [self.selected_row.data.framex, self.selected_row.data.framey, self.selected_row.data.framew, self.selected_row.data.frameh]
        for spinbox, info in zip(self.frame_spinboxes, self.frame_info):
            self.canchange = False
            spinbox.setValue(int(info) if info is not None and str(info).lower() != "default" else 0)
            self.canchange = True