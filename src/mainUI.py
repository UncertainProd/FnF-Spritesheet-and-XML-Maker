# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'NewXMLPngUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1066, 790)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.title_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.title_label.setFont(font)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setObjectName("title_label")
        self.verticalLayout.addWidget(self.title_label)
        self.charname_input_frame = QtWidgets.QFrame(self.centralwidget)
        self.charname_input_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.charname_input_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.charname_input_frame.setObjectName("charname_input_frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.charname_input_frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.charname_label = QtWidgets.QLabel(self.charname_input_frame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.charname_label.setFont(font)
        self.charname_label.setObjectName("charname_label")
        self.horizontalLayout.addWidget(self.charname_label)
        self.charname_textbox = QtWidgets.QLineEdit(self.charname_input_frame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.charname_textbox.setFont(font)
        self.charname_textbox.setObjectName("charname_textbox")
        self.horizontalLayout.addWidget(self.charname_textbox)
        self.verticalLayout.addWidget(self.charname_input_frame)
        self.myTabs = QtWidgets.QTabWidget(self.centralwidget)
        self.myTabs.setObjectName("myTabs")
        self.xmlframes_tab = QtWidgets.QWidget()
        self.xmlframes_tab.setObjectName("xmlframes_tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.xmlframes_tab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.container_frame = QtWidgets.QFrame(self.xmlframes_tab)
        self.container_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.container_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.container_frame.setObjectName("container_frame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.container_frame)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frames_area = QtWidgets.QScrollArea(self.container_frame)
        self.frames_area.setWidgetResizable(True)
        self.frames_area.setObjectName("frames_area")
        self.sprite_frame_content = QtWidgets.QWidget()
        self.sprite_frame_content.setGeometry(QtCore.QRect(0, 0, 990, 456))
        self.sprite_frame_content.setObjectName("sprite_frame_content")
        self.frames_area.setWidget(self.sprite_frame_content)
        self.verticalLayout_3.addWidget(self.frames_area)
        self.controls_frame = QtWidgets.QFrame(self.container_frame)
        self.controls_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.controls_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.controls_frame.setObjectName("controls_frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.controls_frame)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.spsh_settings_btn = QtWidgets.QPushButton(self.controls_frame)
        self.spsh_settings_btn.setMinimumSize(QtCore.QSize(0, 40))
        self.spsh_settings_btn.setObjectName("spsh_settings_btn")
        self.horizontalLayout_2.addWidget(self.spsh_settings_btn)
        self.posename_btn = QtWidgets.QPushButton(self.controls_frame)
        self.posename_btn.setMinimumSize(QtCore.QSize(0, 40))
        self.posename_btn.setObjectName("posename_btn")
        self.horizontalLayout_2.addWidget(self.posename_btn)
        self.generatexml_btn = QtWidgets.QPushButton(self.controls_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.generatexml_btn.sizePolicy().hasHeightForWidth())
        self.generatexml_btn.setSizePolicy(sizePolicy)
        self.generatexml_btn.setMinimumSize(QtCore.QSize(0, 45))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.generatexml_btn.setFont(font)
        self.generatexml_btn.setObjectName("generatexml_btn")
        self.horizontalLayout_2.addWidget(self.generatexml_btn)
        self.horizontalLayout_2.setStretch(0, 2)
        self.horizontalLayout_2.setStretch(1, 2)
        self.horizontalLayout_2.setStretch(2, 3)
        self.verticalLayout_3.addWidget(self.controls_frame)
        self.verticalLayout_2.addWidget(self.container_frame)
        self.myTabs.addTab(self.xmlframes_tab, "")
        self.icongrid_tab = QtWidgets.QWidget()
        self.icongrid_tab.setObjectName("icongrid_tab")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.icongrid_tab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.container_frame_icongrid = QtWidgets.QFrame(self.icongrid_tab)
        self.container_frame_icongrid.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.container_frame_icongrid.setFrameShadow(QtWidgets.QFrame.Raised)
        self.container_frame_icongrid.setObjectName("container_frame_icongrid")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.container_frame_icongrid)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.scrollArea_2 = QtWidgets.QScrollArea(self.container_frame_icongrid)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 990, 451))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.icongrid_holder_label = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.icongrid_holder_label.setText("")
        self.icongrid_holder_label.setObjectName("icongrid_holder_label")
        self.verticalLayout_6.addWidget(self.icongrid_holder_label)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.verticalLayout_5.addWidget(self.scrollArea_2)
        self.controls_frame_icongrid = QtWidgets.QFrame(self.container_frame_icongrid)
        self.controls_frame_icongrid.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.controls_frame_icongrid.setFrameShadow(QtWidgets.QFrame.Raised)
        self.controls_frame_icongrid.setObjectName("controls_frame_icongrid")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.controls_frame_icongrid)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.uploadicongrid_btn = QtWidgets.QPushButton(self.controls_frame_icongrid)
        self.uploadicongrid_btn.setMinimumSize(QtCore.QSize(0, 50))
        self.uploadicongrid_btn.setObjectName("uploadicongrid_btn")
        self.horizontalLayout_3.addWidget(self.uploadicongrid_btn)
        self.uploadicons_btn = QtWidgets.QPushButton(self.controls_frame_icongrid)
        self.uploadicons_btn.setMinimumSize(QtCore.QSize(0, 50))
        self.uploadicons_btn.setObjectName("uploadicons_btn")
        self.horizontalLayout_3.addWidget(self.uploadicons_btn)
        self.iconselected_label = QtWidgets.QLabel(self.controls_frame_icongrid)
        self.iconselected_label.setAlignment(QtCore.Qt.AlignCenter)
        self.iconselected_label.setObjectName("iconselected_label")
        self.horizontalLayout_3.addWidget(self.iconselected_label)
        self.tip_label = QtWidgets.QLabel(self.controls_frame_icongrid)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.tip_label.setFont(font)
        self.tip_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.tip_label.setObjectName("tip_label")
        self.horizontalLayout_3.addWidget(self.tip_label)
        self.zoom_label = QtWidgets.QLabel(self.controls_frame_icongrid)
        self.zoom_label.setObjectName("zoom_label")
        self.horizontalLayout_3.addWidget(self.zoom_label)
        self.generateicongrid_btn = QtWidgets.QPushButton(self.controls_frame_icongrid)
        self.generateicongrid_btn.setMinimumSize(QtCore.QSize(0, 50))
        self.generateicongrid_btn.setObjectName("generateicongrid_btn")
        self.horizontalLayout_3.addWidget(self.generateicongrid_btn)
        self.horizontalLayout_3.setStretch(0, 1)
        self.horizontalLayout_3.setStretch(1, 1)
        self.horizontalLayout_3.setStretch(4, 1)
        self.horizontalLayout_3.setStretch(5, 1)
        self.verticalLayout_5.addWidget(self.controls_frame_icongrid)
        self.verticalLayout_5.setStretch(0, 10)
        self.verticalLayout_5.setStretch(1, 1)
        self.verticalLayout_4.addWidget(self.container_frame_icongrid)
        self.myTabs.addTab(self.icongrid_tab, "")
        self.verticalLayout.addWidget(self.myTabs)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 10)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1066, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_import_existing = QtWidgets.QAction(MainWindow)
        self.action_import_existing.setObjectName("action_import_existing")
        self.actionImport_Images = QtWidgets.QAction(MainWindow)
        self.actionImport_Images.setObjectName("actionImport_Images")
        self.actionClear_Spritesheet_Grid = QtWidgets.QAction(MainWindow)
        self.actionClear_Spritesheet_Grid.setObjectName("actionClear_Spritesheet_Grid")
        self.actionEdit_Frame_Properties = QtWidgets.QAction(MainWindow)
        self.actionEdit_Frame_Properties.setObjectName("actionEdit_Frame_Properties")
        self.actionImport_icons = QtWidgets.QAction(MainWindow)
        self.actionImport_icons.setEnabled(False)
        self.actionImport_icons.setObjectName("actionImport_icons")
        self.actionImport_IconGrid = QtWidgets.QAction(MainWindow)
        self.actionImport_IconGrid.setEnabled(False)
        self.actionImport_IconGrid.setObjectName("actionImport_IconGrid")
        self.actionImport_Icons = QtWidgets.QAction(MainWindow)
        self.actionImport_Icons.setEnabled(False)
        self.actionImport_Icons.setObjectName("actionImport_Icons")
        self.actionClear_IconGrid = QtWidgets.QAction(MainWindow)
        self.actionClear_IconGrid.setEnabled(False)
        self.actionClear_IconGrid.setObjectName("actionClear_IconGrid")
        self.actionClear_Icon_selection = QtWidgets.QAction(MainWindow)
        self.actionClear_Icon_selection.setEnabled(False)
        self.actionClear_Icon_selection.setObjectName("actionClear_Icon_selection")
        self.menuFile.addAction(self.action_import_existing)
        self.menuFile.addAction(self.actionImport_Images)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionImport_IconGrid)
        self.menuFile.addAction(self.actionImport_Icons)
        self.menuEdit.addAction(self.actionClear_Spritesheet_Grid)
        self.menuEdit.addAction(self.actionEdit_Frame_Properties)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionClear_IconGrid)
        self.menuEdit.addAction(self.actionClear_Icon_selection)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        self.retranslateUi(MainWindow)
        self.myTabs.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.title_label.setText(_translate("MainWindow", "Spritesheet XML Generator for Friday Night Funkin\'"))
        self.charname_label.setText(_translate("MainWindow", "Character Name:"))
        self.spsh_settings_btn.setText(_translate("MainWindow", "Spritesheet\n"
"Generation Settings"))
        self.posename_btn.setText(_translate("MainWindow", "Set Animation (Pose) Name"))
        self.generatexml_btn.setText(_translate("MainWindow", "Generate XML"))
        self.myTabs.setTabText(self.myTabs.indexOf(self.xmlframes_tab), _translate("MainWindow", "XML from Frames"))
        self.uploadicongrid_btn.setText(_translate("MainWindow", "Upload Icon-grid"))
        self.uploadicons_btn.setText(_translate("MainWindow", "Upload Icons"))
        self.iconselected_label.setText(_translate("MainWindow", "No. of\n"
"icons selected:\n"
"0"))
        self.tip_label.setText(_translate("MainWindow", "Tip: Use ctrl+i and ctrl+o to zoom in or out respectively"))
        self.zoom_label.setText(_translate("MainWindow", "Zoom:"))
        self.generateicongrid_btn.setText(_translate("MainWindow", "Generate New\n"
"Icon-grid"))
        self.myTabs.setTabText(self.myTabs.indexOf(self.icongrid_tab), _translate("MainWindow", "Add Icons to Icon-grid"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.action_import_existing.setText(_translate("MainWindow", "Import existing Spritesheet and XML"))
        self.actionImport_Images.setText(_translate("MainWindow", "Import Images...."))
        self.actionClear_Spritesheet_Grid.setText(_translate("MainWindow", "Clear Spritesheet Grid"))
        self.actionEdit_Frame_Properties.setText(_translate("MainWindow", "Edit Frame Properties"))
        self.actionImport_icons.setText(_translate("MainWindow", "Import icons"))
        self.actionImport_IconGrid.setText(_translate("MainWindow", "Import IconGrid"))
        self.actionImport_Icons.setText(_translate("MainWindow", "Import Icons"))
        self.actionClear_IconGrid.setText(_translate("MainWindow", "Clear IconGrid"))
        self.actionClear_Icon_selection.setText(_translate("MainWindow", "Clear Icon selection"))


# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     MainWindow = QtWidgets.QMainWindow()
#     ui = Ui_MainWindow()
#     ui.setupUi(MainWindow)
#     MainWindow.show()
#     sys.exit(app.exec_())
if __name__ == '__main__':
    print("To run the actual application, Please type: \npython xmlpngUI.py\nor \npython3 xmlpngUI.py \ndepending on what works")