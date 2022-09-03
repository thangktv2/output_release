from importGUI import *

class CaptureAndShow(QThread,QTimer):
    displaySignal = pyqtSignal(QImage)
    contourSignal = pyqtSignal(QImage)
    minCircleSignal = pyqtSignal(QImage)
    resultFrameSignal = pyqtSignal(QImage)

    setSignal = pyqtSignal(bool)

    conveyerSignal = pyqtSignal(int)

    resultSignal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._run_flag = True

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run)
        self.timer.start(33)

        self.cap = capture(1, 800, 600)
        
        self.set = 0 # Init value to determine error value is set or not

        self.done = 0
        self.done1 = 0

        self.frameCount = 0
        self.begin = 0
        self.result = -1

        self.total_contoursArea = [0,0]
        self.total_minCircleArea = [0,0]

        self.avg_contoursArea = [0,0]
        self.avg_minCircleArea = [0,0]

    def run(self):
        self.ThreadActive = True
        ok, frame = self.cap.read()
        if ok:
            display_init = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            preProcess_init = imagePreprocess(frame.copy())
            contour_init = frame.copy()
            minCircle_init = frame.copy()

            if self.set == 1:
                coordinate = getItemCoordinate(preProcess_init)

                if coordinate[0] == 1:
                    x_startpoint = int(coordinate[1] - 5)
                    y_startpoint = int(coordinate[2] - 5)
                    x_endpoint = int(coordinate[1] + coordinate[3] + 5)
                    y_endpoint = int(coordinate[2] + coordinate[4] + 5)

                    cv.rectangle(display_init, (x_startpoint, y_startpoint), (x_endpoint, y_endpoint), (255, 0, 0), 2)

                    contoursProcessArea = contoursProcess(preProcess_init,contour_init,0)
                    minCircleArea = contoursProcess(preProcess_init,minCircle_init,1)

                    if self.begin == 1:
                        if self.frameCount < 30: # Stop conveyer and wait for 30 frame until it's stable
                            if self.done == 0:
                                print('emit stop signal')
                                self.conveyerSignal.emit(0)
                                self.done = 1
                            else:
                                pass
                        elif 30 <= self.frameCount < 40: # 10 frame to calculate average value and classify base on the value
                            self.total_contoursArea[0] = self.total_contoursArea[0] + contoursProcessArea[0]
                            self.total_contoursArea[1] = self.total_contoursArea[1] + contoursProcessArea[1]

                            self.total_minCircleArea[0] = self.total_minCircleArea[0] + minCircleArea[0]
                            self.total_minCircleArea[1] = self.total_minCircleArea[1] + minCircleArea[1]

                            if self.frameCount == 39:
                                self.avg_contoursArea[0] = self.total_contoursArea[0]/10
                                self.avg_contoursArea[1] = self.total_contoursArea[1]/10

                                self.avg_minCircleArea[0] = self.total_minCircleArea[0]/10
                                self.avg_minCircleArea[1] = self.total_minCircleArea[1]/10

                                result = contour_init | minCircle_init
                                cropInput0 = result[y_startpoint:y_endpoint,x_startpoint:x_endpoint]
                                cropOuput0 = cropImage(cropInput0, 300)

                                result_converted = QImage(cropOuput0.data, 300, 300, QtGui.QImage.Format_RGB888)
                                self.resultFrameSignal.emit(result_converted.copy())

                                if (0.96*self.avg_contoursArea[0] <= self.avg_minCircleArea[0] <= 1.04*self.avg_contoursArea[0]) \
                                    and (0.96*self.avg_contoursArea[1] <= self.avg_minCircleArea[1] <= 1.04*self.avg_contoursArea[1]):
                                    self.result = 1
                                    self.resultSignal.emit(True)
                                else:
                                    self.result = 0
                                    self.resultSignal.emit(False)
                            else:
                                pass
                        elif 40 <= self.frameCount < 70:
                            self.done = 0
                            if self.done1 == 0:
                                print('emit run signal')
                                self.conveyerSignal.emit(1)

                                self.total_contoursArea = [0,0]
                                self.total_minCircleArea = [0,0]

                                self.avg_contoursArea = [0,0]
                                self.avg_minCircleArea = [0,0]

                                self.done1 = 1
                            else:
                                pass
                        else:
                            self.frameCount = 0
                            self.done1 = 0
                    else:
                        pass
                    
                    cropInput1 = contour_init[y_startpoint:y_endpoint,x_startpoint:x_endpoint]
                    cropOuput1 = cropImage(cropInput1, 300)
                    cropInput2 = minCircle_init[y_startpoint:y_endpoint,x_startpoint:x_endpoint]
                    cropOuput2 = cropImage(cropInput2, 300)
                    try:
                        contour_converted = QImage(cropOuput1.data, 300, 300, QtGui.QImage.Format_RGB888)
                        minCircle_conveted = QImage(cropOuput2.data, 300, 300, QtGui.QImage.Format_RGB888)

                        self.contourSignal.emit(contour_converted.copy())
                        self.minCircleSignal.emit(minCircle_conveted.copy())
                    except:
                        pass
                    if self.begin == 1:
                        self.frameCount+=1
                    else:
                        pass
                else:
                    if self.result == 1:
                        self.conveyerSignal.emit(3)
                    elif self.result == 0:
                        self.conveyerSignal.emit(2)
                    else:
                        pass
                    self.result = -1
                    self.frameCount = 0
                    self.done1 = 0
            else:
                pass

            display_converted = QImage(display_init.data, 800, 600, QtGui.QImage.Format_RGB888)
            self.displaySignal.emit(display_converted.copy())
        else:
            print("Can't read frame")
        
    def setValue(self):
        result = setGlobalValue(self.cap,0.3,0.04)
        if result is True:
            self.set = 1
        else:
            pass
        self.setSignal.emit(result)
    
    def allow(self):
        self.begin = 1
        
    def deny(self):
        self.begin = 0

    def stop(self):
        self.ThreadActive = False
        self.quit()