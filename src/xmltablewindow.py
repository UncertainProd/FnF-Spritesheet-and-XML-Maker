from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QMenu, QAction, QMessageBox, QLineEdit, QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from utils import temp_path_shortener, imghashes
import engine.spritesheetutils as spritesheetutils
from xmltablewindowUI import Ui_TableWidgetThing
from utils import display_msg_box

class XMLTableView(QWidget):
    def __init__(self, table_headings):
        super().__init__()
        self.ui = Ui_TableWidgetThing()
        self.ui.setupUi(self)

        self.table_headings = table_headings
        self.ui.xmltable.setColumnCount(len(table_headings))
        self.ui.xmltable.setHorizontalHeaderLabels(table_headings)
        self.ui.xmltable.contextMenuEvent = self.handle_context_menu_event

        # self.ui.xmltable.cellClicked.connect(self.handle_cell_click)
        # self.ui.xmltable.cellActivated.connect(self.handle_cell_click)
        # self.ui.xmltable.cellPressed.connect(self.handle_cell_click)
        self.ui.xmltable.currentCellChanged.connect(self.handle_curr_cell_change)
        self.ui.frame_preview_label.setStyleSheet("QFrame{ border: 1px solid black; }")
        # self.ui.xmltable.selectionModel().selectionChanged.connect(self.handle_cell_selection)

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

        self.selected_cells = []
    
    def handle_curr_cell_change(self, current_row, current_col, prev_row, prev_col):
        self.selected_row_index = current_row
        self.handle_display_stuff(self.selected_row_index)
    
    def handle_context_menu_event(self, event):
        self.menu = QMenu(self)
        renameAction = QAction('Set Value', self)
        renameAction.triggered.connect(lambda: self.set_value_handle())
        self.menu.addAction(renameAction)
        # add other required actions
        self.menu.popup(QCursor.pos())
    
    def set_value_handle(self):
        _cells = self.ui.xmltable.selectedItems()
        idx = -1
        for _cell in _cells:
            if not (_cell.flags() & Qt.ItemIsEditable):
                display_msg_box(self, "Bad cell selection", "There are un-editable cells in your selection!\nSelect cells from the same column, valid columns being\nFrameX, FrameY, FrameWidth or FrameHeight", QMessageBox.Critical)
                return
            else:
                if idx != -1 and _cell.column() != idx:
                    display_msg_box(self, "Multiple Columns Selected", "Your selection spans multiple columns. Make sure to select cells that belong to the same column, valid columns being\nFrameX, FrameY, FrameWidth or FrameHeight", QMessageBox.Critical)
                    return
                else:
                    idx = _cell.column()

        rows = [ x.row() for x in _cells ]
        text, okPressed = QInputDialog.getText(self, f"Change Value of {self.table_headings[idx - 4]}", "New value:"+(" "*50), QLineEdit.Normal)
        is_real_number = lambda s: s.isnumeric() or (s[0] == '-' and s[1:].isnumeric())
        if okPressed and text != '' and is_real_number(text):
            val = int(text)
            old_selected_row_index = self.selected_row_index
            old_selected_row = self.selected_row
            for row_num in rows:
                self.ui.xmltable.setItem(row_num, idx, QTableWidgetItem(str(val)))
                self.selected_row_index = row_num
                self.selected_row = self.tabledata[row_num]
                self.handle_cell_change(row_num, idx)
            
            # restoring things back to normal
            self.selected_row_index = old_selected_row_index
            self.selected_row = old_selected_row
            self.set_true_frame()
        else:
            print("Text invalid / cancel was pressed")


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
        truframe = spritesheetutils.get_true_frame(
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

    # def handle_cell_selection(self, selected, deselected):
    #     if selected.indexes():
    #         self.selected_cells.extend(selected.indexes())
    #         self.selected_row_index = selected.indexes()[-1].row()
    #         self.handle_display_stuff(self.selected_row_index)
    #     elif deselected.indexes():
    #         for _cell in deselected.indexes():
    #             print(f"Removing: {_cell.row()}, {_cell.column()}")
    #             self.selected_cells.remove(_cell)
    #         self.selected_row_index = deselected.indexes()[-1].row()
    #         self.handle_display_stuff(self.selected_row_index)
    #         print(f'{[ (c.row(), c.column()) for c in self.selected_cells ]}')
    #     else:
    #         print("Something's weird here")

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