from PyQt5.QtWidgets import QFormLayout, QLineEdit, QPushButton, QWidget, QLabel

class FrameAdjustWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adjust FrameX and FrameY")
        self.setFixedSize(500, 300)
        formlayout = QFormLayout()

        self.lab1 = QLabel("FrameX: ", self)
        self.frame_x_input = QLineEdit(self)
        self.frame_x_input.setText("0")

        self.lab2 = QLabel("FrameY: ", self)
        self.frame_y_input = QLineEdit(self)
        self.frame_y_input.setText("0")

        self.lab3 = QLabel("Frame Width: ", self)
        self.frame_w_input = QLineEdit(self)
        self.frame_w_input.setText("default")

        self.lab4 = QLabel("Frame Height: ", self)
        self.frame_h_input = QLineEdit(self)
        self.frame_h_input.setText("default")

        self.submitbtn = QPushButton("Set FrameX and FrameY", self)

        # self.warnlabel = QLabel("Warning: If 'clip all to checkbox' option is selected then these options will be overwritten!")

        formlayout.addWidget(self.lab1)
        formlayout.addWidget(self.frame_x_input)
        formlayout.addWidget(self.lab2)
        formlayout.addWidget(self.frame_y_input)
        formlayout.addWidget(self.lab3)
        formlayout.addWidget(self.frame_w_input)
        formlayout.addWidget(self.lab4)
        formlayout.addWidget(self.frame_h_input)
        formlayout.addWidget(self.submitbtn)
        # formlayout.addWidget(self.warnlabel)

        self.setLayout(formlayout)

if __name__ == '__main__':
    print("To run the actual application, Please type: \npython xmlpngUI.py\nor \npython3 xmlpngUI.py \ndepending on what works")