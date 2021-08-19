from PyQt5.uic import loadUi
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import QThread
from gsh_opc_platform_server import opc_server_worker
import sys


class server_conf(QDialog):
    def __init__(self):
        super(server_conf, self).__init__()
        loadUi('server_conf.ui', self)
        self.setWindowTitle("Configure Server")
        self.pushButton_browse.clicked.connect(self.open_xml)
        self.buttonBox.accepted.connect(self.ok_button)
        self.buttonBox.rejected.connect(self.cancel_button)

        with open('server_settings.txt') as f:
            lines = f.readlines()
        settings= [lines[i].split("=")[1] for i in range(len(lines))]
        settings= [settings[i].replace('\n', '') for i in range(len(lines))]

        self.lineEdit_2.setText(plc_ip_address)
        self.lineEdit_3.setText(xml_file_path)
        self.lineEdit.setText(server_ip)

    def open_xml(self):
        dlg = QFileDialog()
        fileName = dlg.getOpenFileName(self, 'OpenFile')
        self.lineEdit_3.setText(str(fileName[0]))

    def ok_button(self):
        global plc_ip_address
        global set_plc_time
        global xml_file_path
        global server_ip
        if self.checkBox.isChecked():
            set_plc_time=True
        else:
            set_plc_time=False
        plc_ip_address = self.lineEdit_2.text()
        xml_file_path = self.lineEdit_3.text()
        server_ip = self.lineEdit.text()

    def cancel_button(self):
        self.close()


def main():
    thread = QThread()
    worker = opc_server_worker()
    worker.moveToThread(thread)
    thread.started.connect(worker.start_opc_server)

    
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    tray = QSystemTrayIcon()
    menu = QMenu()
    option1 = QAction("Start Server")
    option2 = QAction("Stop Server")
    option3 = QAction("Configure Server")
    option1.triggered.connect(lambda: tray_start_button(thread))
    option2.triggered.connect(lambda: tray_stop_button(thread))
    option3.triggered.connect(server_conf_dialog)
    menu.addAction(option1)
    menu.addAction(option2)
    menu.addAction(option3)

    # To quit the app
    quit = QAction("Quit")
    quit.triggered.connect(app.quit)
    menu.addAction(quit)
    icon = QIcon("icons8.png")
    tray.setIcon(icon)
    tray.setVisible(True)
    tray.setContextMenu(menu)
    sys.exit(app.exec_())

def tray_start_button(thread):
    thread.start()

def tray_stop_button(thread):
    #thread.requestInterruption()
    
    stop_threads = True
    thread.quit()

def server_conf_dialog():
    server_configuration = server_conf()
    server_configuration.exec_()

if __name__ == '__main__':
    main()