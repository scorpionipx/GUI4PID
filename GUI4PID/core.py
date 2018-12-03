from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import serial

s = serial.Serial('COM10', 9600, stopbits=serial.STOPBITS_TWO)

app = QtGui.QApplication([])

win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000, 600)
win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)


p6 = win.addPlot(title="Updating plot")
curve = p6.plot(pen='r')
# data = np.random.normal(size=(110, 10000))
data = np.arange(50)
data[49] = 100
ptr = 0


def update():
    global ptr
    values = []
    while s.in_waiting:
        res = int(ord(s.read().decode()))
        values.append(res)
    global curve, data, p6
    curve.setData(data)
    if values:
        try:
            index = 49
            if values:
                data[49] = values[49 - index]
                data = np.roll(data, 1)
            if ptr == 0:
                pass
                p6.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted

        except Exception as err:
            print(err)
    ptr += 1


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(20)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
        s.close()
