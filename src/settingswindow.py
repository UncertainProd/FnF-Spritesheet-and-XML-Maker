import spritesheetgensettings
from PyQt5.QtWidgets import QWidget
from utils import g_settings

class SettingsWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = spritesheetgensettings.Ui_Form()
        self.ui.setupUi(self)

        self.ui.packingalgo_combobox.addItems([
            "Growing Packer (Fits the frames as tightly as possible but doesn't maintain frame ordering)",
            "Ordered Packer (Fits the frames in the order they were added but produces a slightly bigger spritesheet)"
        ])
        self.ui.packingalgo_combobox.setCurrentIndex(0)
        # self.setStyleSheet(get_stylesheet_from_file("app-styles.qss"))

        # self.isclip = self.ui.clip_checkbox.checkState()
        # self.prefix_type = 'custom' if self.ui.custom_prefix_radiobtn.isChecked() else 'charname'
        # self.custom_prefix = self.ui.custom_prefix_text.text()
        # self.must_use_prefix = self.ui.insist_prefix_checkbox.checkState()
        self.saveSettings(False)

        self.ui.custom_prefix_radiobtn.toggled.connect(lambda is_toggled: self.ui.custom_prefix_text.setEnabled(is_toggled))
        self.ui.save_settings_btn.clicked.connect(lambda: self.saveSettings()) # make sure event related parameters don't get accidentally sent to self.saveSettings
        self.ui.settings_cancel_btn.clicked.connect(self.restoreToNormal)

        # hide the no_merge checkbox for now as it is a WIP
        self.ui.no_merge_checkbox.setVisible(False)
    
    def _get_prefix_type(self):
        if self.ui.custom_prefix_radiobtn.isChecked():
            return 'custom'
        elif self.ui.charname_first_radiobtn.isChecked():
            return 'charname'
        elif self.ui.no_prefix_radiobtn.isChecked():
            return 'noprefix'
    
    def _set_radiobuttons(self):
        self.ui.custom_prefix_radiobtn.setChecked(self.prefix_type == 'custom')
        self.ui.charname_first_radiobtn.setChecked(self.prefix_type == 'charname')
        self.ui.no_prefix_radiobtn.setChecked(self.prefix_type == 'noprefix')
    
    def restoreToNormal(self):
        self.ui.clip_checkbox.setCheckState(self.isclip)
        self._set_radiobuttons()
        self.ui.custom_prefix_text.setText(self.custom_prefix)
        self.ui.insist_prefix_checkbox.setCheckState(self.must_use_prefix)
        self.ui.frame_padding_spinbox.setValue(self.frame_padding)
        self.ui.packingalgo_combobox.setCurrentIndex(self.packing_algo)
        # self.ui.no_merge_checkbox.setCheckState(self.no_merge)
        self.close()
    
    def saveSettings(self, shouldclose=True):
        self.isclip = self.ui.clip_checkbox.checkState()
        # self.prefix_type = 'custom' if self.ui.custom_prefix_radiobtn.isChecked() else 'charname'
        self.prefix_type = self._get_prefix_type()
        self.custom_prefix = self.ui.custom_prefix_text.text()
        self.must_use_prefix = self.ui.insist_prefix_checkbox.checkState()
        self.frame_padding = self.ui.frame_padding_spinbox.value()
        self.packing_algo = self.ui.packingalgo_combobox.currentIndex()
        # self.no_merge = self.ui.no_merge_checkbox.checkState()
        # saving to global settings obj
        g_settings['isclip'] = self.isclip
        g_settings['prefix_type'] = self.prefix_type
        g_settings['custom_prefix'] = self.custom_prefix
        g_settings['must_use_prefix'] = self.must_use_prefix
        g_settings['frame_padding'] = self.frame_padding
        g_settings['packing_algo'] = self.packing_algo
        # g_settings['no_merge'] = self.no_merge
        if shouldclose:
            self.close()
    
    def closeEvent(self, a0):
        self.restoreToNormal()
        # return super().closeEvent(a0)