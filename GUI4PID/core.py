from time import sleep
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import serial
import threading

connected = False
try:
    s = serial.Serial('COM10', 38400, stopbits=serial.STOPBITS_TWO)
    connected = True
except Exception as err:
    print("Failed to connect to EVB5.1: {}".format(err))
read = True

app = QtGui.QApplication([])

win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000, 600)
win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)


p6 = win.addPlot(title="Updating plot")
curve = p6.plot(pen='r')
curve_target = p6.plot(pen='g')
curve_target.setData([13] * 50)
# data = np.random.normal(size=(110, 10000))
data = np.zeros(50)
data[49] = 150
ptr = 0

data0 = np.zeros(50)
data1 = np.zeros(50)
data2 = np.zeros(50)
data3 = np.zeros(50)
data4 = np.zeros(50)
data5 = np.zeros(50)

curve0 = p6.plot(pen='y', name='yellow')
curve0.setData([1] * 50)
curve1 = p6.plot(pen='r', name='yellow')
curve1.setData([2] * 50)
curve2 = p6.plot(pen='g', name='yellow')
curve2.setData([3] * 50)
curve3 = p6.plot(pen='b', name='yellow')
curve3.setData([4] * 50)
curve4 = p6.plot(pen='w', name='yellow')
curve4.setData([5] * 50)
curve5 = p6.plot(pen='b', name='yellow')
curve5.setData([6] * 50)


def get_com_port_data():
    """get_com_port_data

    :return:
    """
    if not connected:
        return
    global data0, data1, data2, data3, data4, data5
    while read:
        sleep(.005)
        if s.in_waiting > 6:
            # print("Data buffer exceeded")
            s.read_all()
        elif s.in_waiting < 6:
            # print("Not enough data")
            pass
        else:
            # print("Fetching data..")
            sync_data = int(ord(s.read().decode('cp1252')))
            if sync_data == 255:

                data5 = np.roll(data5, 1)
                data4 = np.roll(data4, 1)
                data3 = np.roll(data3, 1)
                data2 = np.roll(data2, 1)
                data1 = np.roll(data1, 1)
                data0 = np.roll(data0, 1)

                data5[-1] = sync_data
                data4[-1] = int(ord(s.read().decode('cp1252')))
                data3[-1] = int(ord(s.read().decode('cp1252')))
                data2[-1] = int(ord(s.read().decode('cp1252')))
                data1[-1] = int(ord(s.read().decode('cp1252')))
                data0[-1] = int(ord(s.read().decode('cp1252')))

            # print(data5[-1], data4[-1], data3[-1], data2[-1], data1[-1], data0[-1])


read_com_data_thread = threading.Thread(target=get_com_port_data)
read_com_data_thread.start()
# read_com_data_thread.join()


def update():
    global ptr

    curve0.setData(data0)
    curve1.setData(data1)
    curve2.setData(data2)
    curve3.setData(data3)
    curve4.setData(data4)
    curve5.setData(data5)

    if ptr == 0:
        pass
        p6.enableAutoRange('xy', False)  # stop auto-scaling after the first data set is plotted

    ptr += 1


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(20)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
        read = False
        s.close()
