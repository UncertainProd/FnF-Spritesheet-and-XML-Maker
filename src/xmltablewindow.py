from PyQt5.QtWidgets import QTableWidgetItem, QWidget
from spriteframe import SpriteFrame
from utils import temp_path_shortener
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
        self.ui.xmltable.selectionModel().selectionChanged.connect(self.handle_cell_selection)

        # list[SpriteFrame]
        self.tabledata:list[SpriteFrame] = []
    
    def fill_data(self, data):
        table = self.ui.xmltable
        self.tabledata = data
        table.setRowCount(len(data))
        for rownum, label in enumerate(data):
            tabledat = [label.imgpath, label.pose_name, label.img_width, label.img_height, label.framex, label.framey, label.framew, label.frameh]
            for colnum, col in enumerate(tabledat):
                table_cell = QTableWidgetItem(str(col))
                # tablewidgetitem.setFlags(tablewidgetitem.flags() ^ Qt.ItemIsEditable)
                table.setItem(rownum, colnum, table_cell)
    
    def handle_cell_selection(self, selected, deselected):
        if selected.indexes():
            row = selected.indexes()[-1].row()
            self.handle_display_stuff(row)
        elif deselected.indexes():
            row = deselected.indexes()[-1].row()
            self.handle_display_stuff(row)
        else:
            print("Something's weird here")

    def handle_display_stuff(self, row):
        selected_row = self.tabledata[row]
        short_path = temp_path_shortener(selected_row.imgpath)

        self.ui.frame_preview_label.clear()
        self.ui.frame_preview_label.setPixmap(selected_row.image_pixmap)
        
        if selected_row.from_single_png:
            self.ui.frame_info_label.setText(f"Image path: {short_path}\tFrom existing spritesheet: No")
        else:
            self.ui.frame_info_label.setText(f"Image path: {short_path}\tFrom existing spritesheet: Yes\tCo-ords in source spritesheet: x={selected_row.tex_x} y={selected_row.tex_y} w={selected_row.tex_w} h={selected_row.tex_h}")
        
        frame_info = [selected_row.framex, selected_row.framey, selected_row.framew, selected_row.frameh]
        frame_spinboxes = [self.ui.framex_spinbox, self.ui.framey_spinbox, self.ui.framewidth_spinbox, self.ui.frameheight_spinbox]
        for spinbox, info in zip(frame_spinboxes, frame_info):
            spinbox.setValue(int(info) if info is not None and str(info).lower() != "default" else 0)

