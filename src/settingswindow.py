import spritesheetgensettings
from PyQt5.QtWidgets import QWidget
from utils import g_settings

class SettingsWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = spritesheetgensettings.Ui_Form()
        self.ui.setupUi(self)
        # self.setStyleSheet(get_stylesheet_from_file("app-styles.qss"))

        # self.isclip = self.ui.clip_checkbox.checkState()
        # self.prefix_type = 'custom' if self.ui.custom_prefix_radiobtn.isChecked() else 'charname'
        # self.custom_prefix = self.ui.custom_prefix_text.text()
        # self.must_use_prefix = self.ui.insist_prefix_checkbox.checkState()
        self.saveSettings(False)

        self.ui.custom_prefix_radiobtn.toggled.connect(lambda is_toggled: self.ui.custom_prefix_text.setEnabled(is_toggled))
        self.ui.save_settings_btn.clicked.connect(lambda: self.saveSettings()) # make sure event related parameters don't get accidentally sent to self.saveSettings
        self.ui.settings_cancel_btn.clicked.connect(self.restoreToNormal)
    
    def restoreToNormal(self):
        self.ui.clip_checkbox.setCheckState(self.isclip)
        self.ui.custom_prefix_radiobtn.setChecked(self.prefix_type == 'custom')
        self.ui.charname_first_radiobtn.setChecked(self.prefix_type != 'custom')
        self.ui.custom_prefix_text.setText(self.custom_prefix)
        self.ui.insist_prefix_checkbox.setCheckState(self.must_use_prefix)
        self.close()
    
    def saveSettings(self, shouldclose=True):
        self.isclip = self.ui.clip_checkbox.checkState()
        self.prefix_type = 'custom' if self.ui.custom_prefix_radiobtn.isChecked() else 'charname'
        self.custom_prefix = self.ui.custom_prefix_text.text()
        self.must_use_prefix = self.ui.insist_prefix_checkbox.checkState()
        # saving to global settings obj
        g_settings['isclip'] = self.isclip
        g_settings['prefix_type'] = self.prefix_type
        g_settings['custom_prefix'] = self.custom_prefix
        g_settings['must_use_prefix'] = self.must_use_prefix
        if shouldclose:
            self.close()
    
    def closeEvent(self, a0):
        self.restoreToNormal()
        # return super().closeEvent(a0)