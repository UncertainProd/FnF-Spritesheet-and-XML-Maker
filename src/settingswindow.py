import spritesheetgensettings
from PyQt5.QtWidgets import QWidget

class SettingsWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = spritesheetgensettings.Ui_Form()
        self.ui.setupUi(self)
        self.ui.reuse_combobox.addItems([
            "Do not merge duplicate frames\n(Generates bigger spritesheets but is more customizable)", 
            "Merge frames that are taken from existing XMLs (Recommended option)\n(avoids duplicate frames when importing from existing XMLs)", 
            "Merge duplicate frames as much as possible\n(Smaller total spritesheet size but takes much longer to generate. Mostly works but still experimental)"
        ])
        self.ui.reuse_combobox.setCurrentIndex(1)

        self.isclip = self.ui.clip_checkbox.checkState()
        self.reuse_sprites_level = self.ui.reuse_combobox.currentIndex()
        self.prefix_type = 'custom' if self.ui.custom_prefix_radiobtn.isChecked() else 'charname'
        self.custom_prefix = self.ui.custom_prefix_text.text()
        self.must_use_prefix = self.ui.insist_prefix_checkbox.checkState()

        self.ui.custom_prefix_radiobtn.toggled.connect(lambda is_toggled: self.ui.custom_prefix_text.setEnabled(is_toggled))
        self.ui.save_settings_btn.clicked.connect(self.saveSettings)
        self.ui.settings_cancel_btn.clicked.connect(self.restoreToNormal)
    
    def restoreToNormal(self):
        self.ui.clip_checkbox.setCheckState(self.isclip)
        self.ui.reuse_combobox.setCurrentIndex(self.reuse_sprites_level)
        self.ui.custom_prefix_radiobtn.setChecked(self.prefix_type == 'custom')
        self.ui.charname_first_radiobtn.setChecked(self.prefix_type != 'custom')
        self.ui.custom_prefix_text.setText(self.custom_prefix)
        self.ui.insist_prefix_checkbox.setCheckState(self.must_use_prefix)
        self.close()
    
    def saveSettings(self):
        self.isclip = self.ui.clip_checkbox.checkState()
        self.reuse_sprites_level = self.ui.reuse_combobox.currentIndex()
        self.prefix_type = 'custom' if self.ui.custom_prefix_radiobtn.isChecked() else 'charname'
        self.custom_prefix = self.ui.custom_prefix_text.text()
        self.must_use_prefix = self.ui.insist_prefix_checkbox.checkState()
        self.close()
    
    def closeEvent(self, a0):
        self.restoreToNormal()
        # return super().closeEvent(a0)