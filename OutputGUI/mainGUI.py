from importGUI import *

############################# MAIN WINDOW CLASS ##########################################
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.setupUi(self)

        # Init default value for UI component
        self.Interactive_widget.setCurrentWidget(self.DB_tab)
        self.Tab_name.setCurrentWidget(self.DB_name)

        self.Total_num.setText('0')
        self.Passed_num.setText('0')
        self.Failed_num.setText('0')

        self.totalCount = 0
        self.passedCount = 0
        self.failedCount = 0

        # Connect button to corespond tab and name
        self.DB_btn.clicked.connect(lambda : self.Interactive_widget.setCurrentIndex(0))
        self.Cfg_btn.clicked.connect(lambda : self.Interactive_widget.setCurrentIndex(1))
        self.Info_btn.clicked.connect(lambda : self.Interactive_widget.setCurrentIndex(2))

        self.DB_btn.clicked.connect(lambda : self.Tab_name.setCurrentIndex(0))
        self.Cfg_btn.clicked.connect(lambda : self.Tab_name.setCurrentIndex(1))
        self.Info_btn.clicked.connect(lambda : self.Tab_name.setCurrentIndex(2))

        # Connect slider with spinbox
        self.HL_value.valueChanged.connect(self.HL_num.setValue)
        self.HL_num.valueChanged.connect(self.HL_value.setValue)
        self.SL_value.valueChanged.connect(self.SL_num.setValue)
        self.SL_num.valueChanged.connect(self.SL_value.setValue)
        self.VL_value.valueChanged.connect(self.VL_num.setValue)
        self.VL_num.valueChanged.connect(self.VL_value.setValue)

        self.HH_value.valueChanged.connect(self.HH_num.setValue)
        self.HH_num.valueChanged.connect(self.HH_value.setValue)
        self.SH_value.valueChanged.connect(self.SH_num.setValue)
        self.SH_num.valueChanged.connect(self.SH_value.setValue)
        self.VH_value.valueChanged.connect(self.VH_num.setValue)
        self.VH_num.valueChanged.connect(self.VH_value.setValue)

        # Connect show expanding tab button
        self.Show_checkbox.stateChanged.connect(self.showET)
        
        # Assign thread
        self.CAS = CaptureAndShow()
        
        # Connect thread signal to UI component/function
        self.CAS.displaySignal.connect(self.camFrameUpdate)
        self.CAS.contourSignal.connect(self.contourFrameUpdate)
        self.CAS.minCircleSignal.connect(self.minCircleFrameUpdate)
        self.CAS.resultFrameSignal.connect(self.resultFrameUpdate)
        self.CAS.conveyerSignal.connect(self.sendSignal)
        self.CAS.setSignal.connect(self.setOutput)
        self.CAS.resultSignal.connect(self.showResult)

        # Init serial port default value
        self.port = QSerialPort()
        self.Port_sel.addItems([port.portName() for port in QSerialPortInfo().availablePorts()])
        self.Cam_sel.addItems([camera.description() for camera in QCameraInfo.availableCameras()])
        self.Baudrate_sel.setCurrentText('115200')

        # Connect button signal to slot
        self.Set_btn.clicked.connect(self.CAS.setValue)
        self.Port_btn.clicked.connect(self.portConnect)

        self.Start_btn.clicked.connect(self.CAS.allow)
        self.Stop_btn.clicked.connect(self.CAS.deny)

        self.Start_btn.clicked.connect(lambda: self.sendSignal(1))
        self.Stop_btn.clicked.connect(lambda: self.sendSignal(0))

        # Set autoscroll down
        x = self.Output.verticalScrollBar().maximum()
        self.Output.verticalScrollBar().setSliderPosition(x)

        # Add status bar text
        self.statusBar().showMessage("Design by TTL Team")

        # Start thread
        self.CAS.start()

    def close_event(self, event):
        self.CAS.stop()

    def camFrameUpdate(self, image):
        self.Camera_frame.setPixmap(QPixmap.fromImage(image))

    def contourFrameUpdate(self, image):
        self.Contour_frame.setPixmap(QPixmap.fromImage(image))

    def minCircleFrameUpdate(self, image):
        self.minCircle_frame.setPixmap(QPixmap.fromImage(image))
    
    def resultFrameUpdate(self, image):
        self.Result_frame.setPixmap(QPixmap.fromImage(image))

    def showResult(self, result):
        if result == True:
            self.Result_label.setText('Passed')
            self.Result_label.setStyleSheet("background-color: rgb(157, 201, 91); \
                                            border: 2px solid rgb(157, 201, 91);")
            self.totalCount += 1
            self.passedCount += 1
        else:
            self.Result_label.setText('Failed')
            self.Result_label.setStyleSheet("background-color: rgb(255, 0, 92); \
                                            border: 2px solid rgb(255, 0, 92);")
            self.totalCount += 1
            self.failedCount += 1
        
        self.Total_num.setText(str(self.totalCount))
        self.Passed_num.setText(str(self.passedCount))
        self.Failed_num.setText(str(self.failedCount))

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def showET(self):
        check = self.Show_checkbox.isChecked()
        if check == True:
            self.resize(1700,900)
            self.Expandable_widget.show()
            self.Expandable_bar.show()
        else:
            self.resize(1300,900)
            self.Expandable_widget.hide()
            self.Expandable_bar.hide()
        self.centerWindow()

    def setOutput(self, result):
        if result == True:
            self.Output.appendPlainText('Set value success.')
        else:
            self.Output.appendPlainText('Set value failed. Please click set button again.')

    def sendSignal(self,flag):
        check = self.port.isDataTerminalReady()
        if check:
            if flag == 3:
                self.port.writeData(b"F1\n")
            elif flag == 2:
                self.port.writeData(b"F0\n")
            elif flag == 1:
                self.port.writeData(b"C1\n")
            elif flag == 0:
                self.port.writeData(b"C0\n")
            else:
                pass
        else:
            self.Output.appendPlainText('Please connect to COM port first.')

    def portConnect(self):
        check = self.Port_btn.isChecked()
        if check == True:
            if self.port.isOpen():
                self.port.close()

            self.port.setPortName(self.Port_sel.currentText())
            self.port.setBaudRate(int(self.Baudrate_sel.currentText()), QSerialPort.AllDirections)

            self.port.setDataBits(QSerialPort.Data8)
            self.port.setParity(QSerialPort.NoParity)
            self.port.setStopBits(QSerialPort.OneStop)
            self.port.setFlowControl(QSerialPort.SoftwareControl)

            self.result = self.port.open(QSerialPort.ReadWrite)
            self.port.setDataTerminalReady(True)
            if not self.result:
                self.Output.appendPlainText('Port connect error.')
            else:
                self.Output.appendPlainText('Port connected.')
                self.Port_btn.setText('Disconnect Port')
        else:
            self.port.close()
            self.Output.appendPlainText('Port disconnected.')
            self.Port_btn.setText('Connect Port')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())