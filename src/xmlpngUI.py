import sys
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QActionGroup, QApplication, QGridLayout, QInputDialog, QLineEdit, QMainWindow, QMessageBox, QProgressDialog, QPushButton, QSpacerItem, QLabel, QFileDialog
from os import path
from animationwindow import AnimationView
import engine.icongridutils as icongridutils
import engine.spritesheetutils as spritesheetutils
# from frameorderscreen import FrameOrderScreen
from xmltablewindow import XMLTableView
import json

import engine.xmlpngengine as xmlpngengine
from mainUI import Ui_MainWindow
from spriteframe import SpriteFrame
from utils import SPRITEFRAME_SIZE, get_stylesheet_from_file
from settingswindow import SettingsWindow


def display_progress_bar(parent, title="Sample text", startlim=0, endlim=100):
    def update_prog_bar(progress, progresstext):
        progbar.setValue(progress)
        progbar.setLabel(QLabel(progresstext))
    progbar = QProgressDialog(title, None, startlim, endlim, parent)
    progbar.setWindowModality(Qt.WindowModal)
    progbar.show()

    return update_prog_bar, progbar

def set_preferences(prefdict):
    try:
        with open('preferences.json', 'w') as f:
            json.dump(prefdict, f)
    except Exception as e:
        with open("error.log", 'a') as errlog:
            errlog.write(str(e))

class MyApp(QMainWindow):
    def __init__(self, prefs):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("XML Generator")

        self.ui.generatexml_btn.clicked.connect(self.generate_xml)
        self.ui.actionExport_as_Spritesheet_and_XML.triggered.connect(self.generate_xml)
        self.ui.actionExport_induvidual_images.triggered.connect(self.export_bunch_of_imgs)
        self.ui.frames_area.setWidgetResizable(True)
        self.frames_layout = QGridLayout(self.ui.sprite_frame_content)
        self.ui.frames_area.setWidget(self.ui.sprite_frame_content)

        self.num_labels = 0
        self.labels = []
        self.selected_labels = []
        # self.frame_dict = {} # dict< pose_name: str -> frames: list[SpriteFrame] >

        self.add_img_button = QPushButton()
        self.add_img_button.setIcon(QIcon("./assets/AddImg.png"))
        self.add_img_button.setGeometry(0, 0, SPRITEFRAME_SIZE, SPRITEFRAME_SIZE)
        self.add_img_button.setFixedSize(QSize(SPRITEFRAME_SIZE, SPRITEFRAME_SIZE))
        self.add_img_button.setIconSize(QSize(SPRITEFRAME_SIZE, SPRITEFRAME_SIZE))
        self.add_img_button.clicked.connect(self.open_frame_imgs)

        self.frames_layout.addWidget(self.add_img_button, 0, 0, Qt.AlignmentFlag(0x1|0x20))
        self.ui.myTabs.setCurrentIndex(0)

        self.setWindowIcon(QIcon("./assets/appicon.png"))
        self.icongrid_zoom = 1
        self.ui.uploadicongrid_btn.clicked.connect(self.uploadIconGrid)
        self.ui.actionImport_IconGrid.triggered.connect(self.uploadIconGrid)
        self.ui.generateicongrid_btn.clicked.connect(self.getNewIconGrid)
        self.ui.uploadicons_btn.clicked.connect(self.appendIcon)
        self.ui.actionImport_Icons.triggered.connect(self.appendIcon)
        self.ui.actionClear_IconGrid.triggered.connect(self.clearIconGrid)
        self.ui.actionClear_Icon_selection.triggered.connect(self.clearSelectedIcons)

        self.action_zoom_in = QAction(self.ui.icongrid_holder_label)
        self.ui.icongrid_holder_label.addAction(self.action_zoom_in)
        self.action_zoom_in.triggered.connect(self.zoomInPixmap)
        self.action_zoom_in.setShortcut("Ctrl+i")

        self.action_zoom_out = QAction(self.ui.icongrid_holder_label)
        self.ui.icongrid_holder_label.addAction(self.action_zoom_out)
        self.action_zoom_out.triggered.connect(self.zoomOutPixmap)
        self.action_zoom_out.setShortcut("Ctrl+o")

        self.ui.zoom_label.setText("Zoom: 100%")

        self.iconpaths = []
        self.icongrid_path = ""

        self.ui.posename_btn.clicked.connect(self.setAnimationNames)
        self.ui.posename_btn.setDisabled(True)
        self.ui.charname_textbox.textChanged.connect(self.onCharacterNameChange)

        self.num_cols = 6
        self.num_rows = 1

        self.ui.actionImport_Images.triggered.connect(self.open_frame_imgs)
        self.ui.action_import_existing.triggered.connect(self.open_existing_spsh_xml)
        self.ui.actionImport_from_GIF.triggered.connect(self.open_gif)

        self.num_rows = 1 + self.num_labels//self.num_cols
        
        for i in range(self.num_cols):
            self.frames_layout.setColumnMinimumWidth(i, 0)
            self.frames_layout.setColumnStretch(i, 0)
        for i in range(self.num_rows):
            self.frames_layout.setRowMinimumHeight(i, 0)
            self.frames_layout.setRowStretch(i, 0)
        
        vspcr = QSpacerItem(1, 1)
        self.frames_layout.addItem(vspcr, self.num_rows, 0, 1, 4)

        hspcr = QSpacerItem(1, 1)
        self.frames_layout.addItem(hspcr, 0, self.num_cols, self.num_rows, 1)

        self.ui.actionClear_Spritesheet_Grid.triggered.connect(self.clear_spriteframe_grid)
        self.ui.myTabs.currentChanged.connect(self.handle_tab_change)
        self.ui.spsh_settings_btn.clicked.connect(self.show_settings)

        self.settings_widget = SettingsWindow()

        self.anim_view_window = AnimationView()
        self.ui.actionPreview_Animation.triggered.connect(self.show_anim_preview)
        self.ui.actionPreview_Animation.setEnabled(len(self.labels) > 0)
        # adding a QActionGroup at runtime :/
        darkmode_action_group = QActionGroup(self.ui.menuDefault_Dark_mode)
        theme_opts = ["Default", "Dark Mode"]
        checked_action = "Default" if prefs.get("theme", 'default') != 'dark' else "Dark Mode"
        for opt in theme_opts:
            action = QAction(opt, self.ui.menuDefault_Dark_mode, checkable=True, checked=(opt == checked_action))
            self.ui.menuDefault_Dark_mode.addAction(action)
            darkmode_action_group.addAction(action)
        darkmode_action_group.setExclusive(True)
        darkmode_action_group.triggered.connect(self.set_dark_mode)
        
        self.xml_table = XMLTableView(['Image Path', 'Name', 'Width', 'Height', 'FrameX', 'FrameY', 'FrameWidth', 'FrameHeight'])
        self.ui.actionView_XML_structure.triggered.connect(self.show_table_view)
        self.ui.actionView_XML_structure.setEnabled(len(self.labels) > 0)
        self.ui.actionFlipX.triggered.connect(lambda: self.flip_labels('X'))
        self.ui.actionFlipY.triggered.connect(lambda: self.flip_labels('Y'))

        self.ui.use_psychengine_checkbox.clicked.connect(self.handle_psychengine_checkbox)

        # self.frame_order_screen = FrameOrderScreen()
        # self.ui.actionChange_Frame_Ordering.triggered.connect(self.show_frame_order_screen)
        # self.ui.actionChange_Frame_Ordering.setEnabled(len(self.labels) > 0)
        
        # Note: Add any extra windows before this if your want the themes to apply to them
        if prefs.get("theme", 'default') == 'dark':
            self.set_theme(get_stylesheet_from_file("assets/app-styles.qss"))
        
    
    def ranged_selection_handler(self, selected_spriteframe):
        first_selected_spriteframe = None
        for sprf in self.labels:
            if sprf == selected_spriteframe:
                break

            if sprf.select_checkbox.checkState() != 0 and sprf != selected_spriteframe:
                first_selected_spriteframe = sprf
                break
        
        if first_selected_spriteframe is not None:
            start_selecting = False
            for sprf in self.labels:
                if sprf == first_selected_spriteframe:
                    start_selecting = True
                
                if start_selecting:
                    # checks the box and adds it to the selected list
                    sprf.select_checkbox.setChecked(1)
                
                if sprf == selected_spriteframe:
                    break
    
    def ranged_deletion_handler(self, selected_spriteframe):
        first_selected_spriteframe = None
        for sprf in self.labels:
            if sprf == selected_spriteframe:
                break

            if sprf.select_checkbox.checkState() != 0 and sprf != selected_spriteframe:
                first_selected_spriteframe = sprf
                break
        
        if first_selected_spriteframe is not None:
            start_selecting = False
            for sprf in self.labels:
                if sprf == first_selected_spriteframe:
                    start_selecting = True
                
                if start_selecting:
                    # unchecks the box and removes it from the selected list
                    sprf.select_checkbox.setChecked(0)
                
                if sprf == selected_spriteframe:
                    break
    

    def open_gif(self):
        gifpath = self.get_asset_path("Select the GIF file", "GIF images (*.gif)")
        if gifpath != '':
            update_prog_bar, progbar = display_progress_bar(self, "Extracting sprite frames....")
            QApplication.processEvents()
            
            sprites = spritesheetutils.get_gif_frames(gifpath, update_prog_bar)
            for i, spfr in enumerate(sprites):
                spfr.frameparent = self
                self.add_spriteframe(spfr)
                update_prog_bar(50 + ((i+1)*50//len(sprites)), f"Adding frames from: {gifpath}")
            progbar.close()
            
            self.ui.posename_btn.setDisabled(self.num_labels <= 0)

    def handle_psychengine_checkbox(self, checked):
        self.ui.uploadicongrid_btn.setEnabled(not checked)
    
    # def show_frame_order_screen(self):
        # self.frame_order_screen.set_frame_dict(self.frame_dict)
        # self.frame_order_screen.show()
    
    def flip_labels(self, dxn='X'):
        for lab in self.selected_labels:
            lab.flip_img(dxn)
        
        for lab in list(self.selected_labels):
            # this automatically removes it from self.selected_labels
            lab.select_checkbox.setChecked(False)

    def show_table_view(self):
        print("Showing table view...")
        self.xml_table.fill_data(self.labels)
        self.xml_table.show()

    def set_dark_mode(self, event):
        if event.text() == "Dark Mode":
            styles = get_stylesheet_from_file("./assets/app-styles.qss")
            self.set_theme(styles)
        else:
            self.set_theme("")
    
    def set_theme(self, stylestr):
        self.setStyleSheet(stylestr)
        self.settings_widget.setStyleSheet(stylestr)
        self.anim_view_window.setStyleSheet(stylestr)
        self.xml_table.setStyleSheet(stylestr)
        # self.frame_order_screen.setStyleSheet(stylestr)
        if stylestr == "":
            set_preferences({ "theme":"default" })
        else:
            set_preferences({ "theme":"dark" })

    def show_anim_preview(self):
        self.anim_view_window.parse_and_load_frames(self.labels)
        self.anim_view_window.show()
    
    def show_settings(self):
        self.settings_widget.show()

    def handle_tab_change(self, newtabind):
        self.ui.actionClear_Spritesheet_Grid.setDisabled(newtabind != 0)
        self.ui.action_import_existing.setDisabled(newtabind != 0)
        self.ui.actionImport_from_GIF.setDisabled(newtabind != 0)
        self.ui.actionImport_Images.setDisabled(newtabind != 0)
        self.ui.actionEdit_Frame_Properties.setDisabled(newtabind != 0 or len(self.selected_labels) <= 0)
        self.ui.menuExport.setDisabled(newtabind != 0)
        self.ui.menuEdit_Selected_Images.setDisabled(newtabind != 0)

        self.ui.actionImport_IconGrid.setDisabled(newtabind != 1)
        self.ui.actionImport_Icons.setDisabled(newtabind != 1)
        self.ui.actionClear_IconGrid.setDisabled(newtabind != 1)
        self.ui.actionClear_Icon_selection.setDisabled(newtabind != 1)
    
    def onCharacterNameChange(self):
        for label in self.labels:
            label.img_label.setToolTip(label.get_tooltip_string(self))
    
    def clear_spriteframe_grid(self):
        labs = list(self.labels)
        for lab in labs:
            lab.remove_self(self)
        self.ui.actionEdit_Frame_Properties.setDisabled(len(self.selected_labels) <= 0)
    
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
    
    def open_existing_spsh_xml(self):
        imgpath = self.get_asset_path("Select Spritesheet File", "PNG Images (*.png)")

        if imgpath != '':
            xmlpath = self.get_asset_path("Select XML File", "XML Files (*.xml)")
            if xmlpath != '':
                trubasenamefn = lambda fpath: path.basename(fpath).split('.')[0]
                charname = trubasenamefn(xmlpath)
                if trubasenamefn(imgpath) != trubasenamefn(xmlpath):
                    self.msgbox = QMessageBox(self)
                    self.msgbox.setWindowTitle("Conflicting file names")
                    self.msgbox.setText("The Spritesheet and the XML file have different file names.\nThe character name will not be auto-filled")
                    self.msgbox.setIcon(QMessageBox.Warning)
                    self.msgbox.addButton("OK", QMessageBox.YesRole)
                    cancel_import = self.msgbox.addButton("Cancel import", QMessageBox.NoRole)
                    x = self.msgbox.exec_()
                    clickedbtn = self.msgbox.clickedButton()
                    if clickedbtn == cancel_import:
                        return
                    charname = self.ui.charname_textbox.text() # trubasenamefn(imgpath) if clickedbtn == usespsh else trubasenamefn(xmlpath)
                    print("[DEBUG] Exit status of msgbox: "+str(x))


                update_prog_bar, progbar = display_progress_bar(self, "Extracting sprite frames....")
                QApplication.processEvents()

                sprites = spritesheetutils.split_spsh(imgpath, xmlpath, update_prog_bar)
                for i, spfr in enumerate(sprites):
                    spfr.frameparent = self
                    self.add_spriteframe(spfr)
                    update_prog_bar(50 + ((i+1)*50//len(sprites)), f"Adding: {imgpath}")
                progbar.close()
                
                self.ui.posename_btn.setDisabled(self.num_labels <= 0)
                
                self.ui.charname_textbox.setText(charname)

        
    
    def open_frame_imgs(self):
        imgpaths = self.get_asset_path("Select sprite frames", "PNG Images (*.png)", True)

        if imgpaths:
            update_prog_bar, progbar = display_progress_bar(self, "Importing sprite frames....", 0, len(imgpaths))
            QApplication.processEvents()

            for i, pth in enumerate(imgpaths):
                # self.add_img(pth)
                self.add_spriteframe(SpriteFrame(self, pth))
                update_prog_bar(i+1, f"Adding: {pth}")
            progbar.close()
        
        if len(self.labels) > 0:
            self.ui.posename_btn.setDisabled(False)
    
    def add_spriteframe(self, sp):
        self.num_rows = 1 + self.num_labels//self.num_cols
        
        self.frames_layout.setRowMinimumHeight(self.num_rows - 1, 0)
        self.frames_layout.setRowStretch(self.num_rows - 1, 0)
        
        vspcr = QSpacerItem(1, 1)
        self.frames_layout.addItem(vspcr, self.num_rows, 0, 1, 4)

        hspcr = QSpacerItem(1, 1)
        self.frames_layout.addItem(hspcr, 0, self.num_cols, self.num_rows, 1)
        
        self.labels.append(sp)
        self.frames_layout.removeWidget(self.add_img_button)
        self.frames_layout.addWidget(self.labels[-1], self.num_labels // self.num_cols, self.num_labels % self.num_cols, Qt.AlignmentFlag(0x1|0x20))
        self.num_labels += 1
        self.frames_layout.addWidget(self.add_img_button, self.num_labels // self.num_cols, self.num_labels % self.num_cols, Qt.AlignmentFlag(0x1|0x20))
        self.ui.actionPreview_Animation.setEnabled(len(self.labels) > 0)
        self.ui.actionView_XML_structure.setEnabled(len(self.labels) > 0)
        # self.ui.actionChange_Frame_Ordering.setEnabled(len(self.labels) > 0)
        
        # self.update_frame_dict(sp.img_xml_data.pose_name, sp)
    
    def update_frame_dict(self, key, val, remove=False):
        # TODO
        return
    
    def re_render_grid(self):
        self.num_rows = 1 + self.num_labels//self.num_cols
        for i in range(self.num_cols):
            self.frames_layout.setColumnMinimumWidth(i, 0)
            self.frames_layout.setColumnStretch(i, 0)
        for i in range(self.num_rows):
            self.frames_layout.setRowMinimumHeight(i, 0)
            self.frames_layout.setRowStretch(i, 0)

        vspcr = QSpacerItem(1, 1)
        self.frames_layout.addItem(vspcr, self.num_rows, 0, 1, 4)

        hspcr = QSpacerItem(1, 1)
        self.frames_layout.addItem(hspcr, 0, self.num_cols, self.num_rows, 1)
        
        for i, sp in enumerate(self.labels):
            self.frames_layout.addWidget(sp, i//self.num_cols, i%self.num_cols, Qt.AlignmentFlag(0x1|0x20))
        self.frames_layout.removeWidget(self.add_img_button)
        self.frames_layout.addWidget(self.add_img_button, self.num_labels // self.num_cols, self.num_labels % self.num_cols, Qt.AlignmentFlag(0x1|0x20))
    
    def export_bunch_of_imgs(self):
        savedir = QFileDialog.getExistingDirectory(caption="Save image sequence to...")
        updatefn, progbar = display_progress_bar(self, "Exporting Image Sequence", startlim=0, endlim=len(self.labels))
        QApplication.processEvents()
        
        errmsg = xmlpngengine.save_img_sequence(self.labels, savedir, updatefn)
        progbar.close()
        if errmsg:
            self.display_msg_box("Error!", text=f"An error occured: {errmsg}", icon=QMessageBox.Critical)
        else:
            self.display_msg_box("Success!", text="Image sequence saved successfully!", icon=QMessageBox.Information)
    
    def generate_xml(self):
        charname = self.ui.charname_textbox.text()
        charname = charname.strip()
        if self.num_labels > 0 and charname != '':
            savedir = QFileDialog.getExistingDirectory(caption="Save files to...")
            print("Stuff saved to: ", savedir)
            if savedir != '':
                update_prog_bar, progbar = display_progress_bar(self, "Generating....", 0, len(self.labels))
                QApplication.processEvents()
                
                statuscode, errmsg = xmlpngengine.make_png_xml(
                    self.labels, 
                    savedir, 
                    charname, 
                    update_prog_bar
                )
                progbar.close()
                if errmsg is None:
                    self.display_msg_box(
                        window_title="Done!", 
                        text="Your files have been generated!\nCheck the folder you had selected",
                        icon=QMessageBox.Information
                    )
                else:
                    self.display_msg_box(
                        window_title="Error!",
                        text=("Some error occured! Error message: " + errmsg),
                        icon=QMessageBox.Critical
                    )
        else:
            errtxt = "Please enter some frames" if self.num_labels <= 0 else "Please enter the name of your character"
            self.display_msg_box(
                window_title="Error!", 
                text=errtxt,
                icon=QMessageBox.Critical
            )
    
    def zoomInPixmap(self):
        if self.icongrid_path and self.icongrid_zoom <= 5:
            self.icongrid_zoom *= 1.1
            icongrid_pixmap = QPixmap(self.icongrid_path)
            w = icongrid_pixmap.width()
            h = icongrid_pixmap.height()
            icongrid_pixmap = icongrid_pixmap.scaled(int(w*self.icongrid_zoom), int(h*self.icongrid_zoom), 1)
            self.ui.icongrid_holder_label.setFixedSize(icongrid_pixmap.width(), icongrid_pixmap.height())
            self.ui.scrollAreaWidgetContents_2.setFixedSize(icongrid_pixmap.width(), icongrid_pixmap.height())
            self.ui.icongrid_holder_label.setPixmap(icongrid_pixmap)
            self.ui.zoom_label.setText("Zoom: %.2f %%" % (self.icongrid_zoom*100))


    def zoomOutPixmap(self):
        if self.icongrid_path and self.icongrid_zoom >= 0.125:
            self.icongrid_zoom /= 1.1
            icongrid_pixmap = QPixmap(self.icongrid_path)
            w = icongrid_pixmap.width()
            h = icongrid_pixmap.height()
            icongrid_pixmap = icongrid_pixmap.scaled(int(w*self.icongrid_zoom), int(h*self.icongrid_zoom), 1)
            self.ui.icongrid_holder_label.setFixedSize(icongrid_pixmap.width(), icongrid_pixmap.height())
            self.ui.scrollAreaWidgetContents_2.setFixedSize(icongrid_pixmap.width(), icongrid_pixmap.height())
            self.ui.icongrid_holder_label.setPixmap(icongrid_pixmap)
            self.ui.zoom_label.setText("Zoom: %.2f %%" % (self.icongrid_zoom*100))
    
    def uploadIconGrid(self):
        print("Uploading icongrid...")
        self.icongrid_path = self.get_asset_path("Select the Icon-grid", "PNG Images (*.png)")
        icongrid_pixmap = QPixmap(self.icongrid_path)
        self.ui.icongrid_holder_label.setFixedSize(icongrid_pixmap.width(), icongrid_pixmap.height())
        self.ui.scrollAreaWidgetContents_2.setFixedSize(icongrid_pixmap.width(), icongrid_pixmap.height())
        self.ui.icongrid_holder_label.setPixmap(icongrid_pixmap)
    
    def clearIconGrid(self):
        self.icongrid_path = ""
        self.ui.icongrid_holder_label.clear()
    
    def getNewIconGrid(self):
        if self.ui.use_psychengine_checkbox.isChecked():
            if len(self.iconpaths) > 0:
                print("Using psych engine style icon grid generation....")
                savepath, _ = QFileDialog.getSaveFileName(self, "Save as filename", filter="PNG files (*.png)")

                stat, problemimg, exception_msg = icongridutils.makePsychEngineIconGrid(self.iconpaths, savepath)

                if exception_msg is not None:
                    self.display_msg_box(
                        window_title="Error!", 
                        text=f"An error occured: {exception_msg}",
                        icon=QMessageBox.Critical
                    )
                else:
                    if stat == 0:
                        self.display_msg_box(
                            window_title="Done!", 
                            text="Your icon-grid has been generated!",
                            icon=QMessageBox.Information
                        )
                        # display final image onto the icon display area 
                        icongrid_pixmap = QPixmap(savepath)
                        self.ui.icongrid_holder_label.setFixedSize(icongrid_pixmap.width(), icongrid_pixmap.height())
                        self.ui.scrollAreaWidgetContents_2.setFixedSize(icongrid_pixmap.width(), icongrid_pixmap.height())
                        self.ui.icongrid_holder_label.setPixmap(icongrid_pixmap)
                    elif stat == 1:
                        self.display_msg_box(
                            window_title="Icon image error",
                            text=f"The icon {problemimg} is bigger than 150x150 and couldn't be added to the final grid\nThe final grid was generated without it",
                            icon=QMessageBox.Warning
                        )
            else:
                self.display_msg_box(
                    window_title="Error!", 
                    text="Please select some icons",
                    icon=QMessageBox.Critical
                )
            
            # no need to continue past this if in psych-engine mode
            return
        
        if self.icongrid_path != '' and len(self.iconpaths) > 0:
            print("Valid!")
            # savedir = QFileDialog.getExistingDirectory(caption="Save New Icongrid to...")
            # if savedir != '':
            stat, newinds, problemimg, exception_msg = icongridutils.appendIconToGrid(self.icongrid_path, self.iconpaths) #, savedir)
            print("[DEBUG] Function finished with status: ", stat)
            errmsgs = [
                'Icon grid was too full to insert a new icon', 
                'Your character icon: {} is too big! Max size: 150 x 150',
                'Unable to find suitable location to insert your icon'
            ]

            if exception_msg is not None:
                self.display_msg_box(
                    window_title="An Error occured", 
                    text=("An Exception (Error) occurred somewhere\nError message:\n"+exception_msg),
                    icon=QMessageBox.Critical
                )
            else:
                if stat == 0:
                    self.display_msg_box(
                        window_title="Done!", 
                        text="Your icon-grid has been generated!\nYour icon's indices are {}".format(newinds),
                        icon=QMessageBox.Information
                    )
                elif stat == 4:
                    self.display_msg_box(
                        window_title="Warning!", 
                        text="One of your icons was smaller than the 150 x 150 icon size!\nHowever, your icon-grid is generated but the icon has been re-adjusted. \nYour icon's indices: {}".format(newinds),
                        icon=QMessageBox.Warning
                    )
                else:
                    self.display_msg_box(
                        window_title="Error!", 
                        text=errmsgs[stat - 1].format(problemimg),
                        icon=QMessageBox.Critical
                )
            icongrid_pixmap = QPixmap(self.icongrid_path)
            self.ui.icongrid_holder_label.setFixedSize(icongrid_pixmap.width(), icongrid_pixmap.height())
            self.ui.scrollAreaWidgetContents_2.setFixedSize(icongrid_pixmap.width(), icongrid_pixmap.height())
            self.ui.icongrid_holder_label.setPixmap(icongrid_pixmap)
        else:
            errtxt = "Please add an icon-grid image" if self.icongrid_path == '' else "Please add an icon"
            self.display_msg_box(
                window_title="Error!", 
                text=errtxt,
                icon=QMessageBox.Critical
            )
    
    def appendIcon(self):
        print("Appending icon")
        self.iconpaths = self.get_asset_path("Select your character icons", "PNG Images (*.png)", True)
        print("Got icon: ", self.iconpaths)
        if len(self.iconpaths) > 0:
            print("Valid selected")
            self.ui.iconselected_label.setText("No. of\nicons selected:\n{}".format(len(self.iconpaths)))
        else:
            self.ui.iconselected_label.setText("No. of\nicons selected:\n0")
    
    def clearSelectedIcons(self):
        self.iconpaths = []
        self.ui.iconselected_label.setText("Number of\nicons selected:\n{}".format(len(self.iconpaths)))

    def setAnimationNames(self):
        if len(self.selected_labels) == 0:
            self.display_msg_box(window_title="Error", text="Please select some frames to rename by checking the checkboxes on them", icon=QMessageBox.Critical)
        else:
            text, okPressed = QInputDialog.getText(self, "Change Animation (Pose) Prefix Name", "Current Animation (Pose) prefix:"+(" "*50), QLineEdit.Normal) # very hack-y soln but it works!
            if okPressed and text != '':
                print("new pose prefix = ", text)
                for label in self.selected_labels:
                    # self.update_frame_dict(label.img_xml_data.pose_name, label, remove=True)
                    label.data.pose_name = text
                    label.modified = True
                    # self.update_frame_dict(text, label)
                    label.img_label.setToolTip(label.get_tooltip_string(self))
                
                for label in list(self.selected_labels):
                    # this automatically removes it from self.selected_labels
                    label.select_checkbox.setChecked(False)
            else:
                print("Cancel pressed!")
    
    def display_msg_box(self, window_title="MessageBox", text="Text Here", icon=None):
        self.msgbox = QMessageBox(self)
        self.msgbox.setWindowTitle(window_title)
        self.msgbox.setText(text)
        if not icon:
            self.msgbox.setIcon(QMessageBox.Information)
        else:
            self.msgbox.setIcon(icon)
        x = self.msgbox.exec_()
        print("[DEBUG] Exit status of msgbox: "+str(x))
    
    def get_asset_path(self, wintitle="Sample", fileformat=None, multiple=False):
        if multiple:
            return QFileDialog.getOpenFileNames(
                caption=wintitle, 
                filter=fileformat,
            )[0]
        else:
            return QFileDialog.getOpenFileName(
                caption=wintitle, 
                filter=fileformat,
            )[0]




if __name__ == '__main__':
    app = QApplication(sys.argv)

    prefs = None
    try:
        with open('preferences.json') as f:
            prefs = json.load(f)
    except FileNotFoundError as fnfe:
        with open("error.log", 'a') as errlog:
            errlog.write(str(fnfe))
        
        with open('preferences.json', 'w') as f:
            prefs = { "theme":"default" }
            json.dump(prefs, f)
    
    myapp = MyApp(prefs)
    myapp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Closing...")