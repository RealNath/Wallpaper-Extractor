from PyQt6 import QtCore, QtGui, QtWidgets
import os

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(350, 350)
        icon_path = os.path.join(os.getcwd(), "assets", "appicon.svg")
        if os.path.exists(icon_path):
            MainWindow.setWindowIcon(QtGui.QIcon("./assets/appicon.svg"))

        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        self.wallLabel = QtWidgets.QLabel(parent=self.centralwidget)
        self.wallLabel.setObjectName("wallpaper_label")
        # Make label expand horizontally to fill the layout width
        self.wallLabel.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.wallLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.verticalLayout.addWidget(self.wallLabel)
        
        self.get_wall_path_btn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.get_wall_path_btn.setObjectName("get_wall_path_btn")
        self.get_wall_path_btn.setEnabled(False)
        self.verticalLayout.addWidget(self.get_wall_path_btn)

        self.extract_wall_btn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.extract_wall_btn.setObjectName("extract_wall_btn")
        self.extract_wall_btn.setEnabled(False)
        self.verticalLayout.addWidget(self.extract_wall_btn)

        self.btn_msg_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.btn_msg_label.setObjectName("btn_message_label")
        self.btn_msg_label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        self.btn_msg_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.btn_msg_label.setWordWrap(True)
        self.verticalLayout.addWidget(self.btn_msg_label)

        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Extract Wallpaper"))
        self.wallLabel.setText(_translate("MainWindow", "Can\'t display current wallpaper"))
        self.get_wall_path_btn.setText(_translate("MainWindow", "Copy Path to Clipboard"))
        self.extract_wall_btn.setText(_translate("MainWindow", "Extract Wallpaper"))
        # self.btn_msg_label.setText(_translate("MainWindow", "File path saved to clipboard"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
