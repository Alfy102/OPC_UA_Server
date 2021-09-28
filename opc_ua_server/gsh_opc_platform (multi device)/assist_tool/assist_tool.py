import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog
from PyQt5.QtWidgets import QMainWindow
from assist_tool_gui import Ui_MainWindow
from pathlib import Path
import PyQt5

class MainWindow(QMainWindow, Ui_MainWindow):
    
    def __init__(self):
        super(MainWindow,self).__init__()
        self.title = 'GSH OPC Assist tool'
        self.path = ''

    def setupUi(self, MainFrame):
        super(MainWindow, self).setupUi(MainFrame)
        self.plainTextEdit.setReadOnly(True)

        self.pushButton.clicked.connect(self.open) # connect clicked to self.open()

        self.pushButton_2.clicked.connect(self.convert_ui_file)  
        self.pushButton_3.clicked.connect(self.convert_rc_file) 

    def open(self):
        path = QFileDialog.getOpenFileName(self, 'Open a file', '',
                                        'All Files (*.*)')
        if path != ('', ''):
            self.plainTextEdit.appendPlainText("File path : "+ path[0])
            input_file = path[0].split("/")
            self.i_file = input_file[len(input_file)-1]
    
            self.path = Path(path[0]).parent.absolute()

    def convert_ui_file(self):
        input_ui_file = self.path.joinpath(self.i_file)
        output_ui_file = self.i_file.replace(".ui",".py")
        output_ui_file = self.path.joinpath(output_ui_file)
        #print(input_ui_file)
        command = f"python -m PyQt5.uic.pyuic -x '{input_ui_file}' -o '{output_ui_file}'"
        os.system(command)
        self.plainTextEdit.appendPlainText("Converted from ui file to py file")

        
    def convert_rc_file(self):
        input_qrc_file = self.path.joinpath(self.i_file)
        output_qrc_file = self.i_file.replace(".ui",".py")
        output_qrc_file = self.path.joinpath(output_qrc_file)
        os.system(f"pyrcc5 -o qtqr.py qtr.qrc")
        self.plainTextEdit.appendPlainText("Converted from qrc file to py file")



def main():
    app = QApplication(sys.argv)
    Main_UI = QMainWindow()
    ui = MainWindow()
    ui.setupUi(Main_UI)
    Main_UI.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()


#python -m PyQt5.uic.pyuic -x opc_ui.ui -o .\gsh_opc_platform_gui.py
#pyrcc5 -o qtqr.py qtr.qrc